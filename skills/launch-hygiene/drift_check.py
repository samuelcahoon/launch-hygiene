#!/usr/bin/env python3
"""Launch hygiene drift check. Finds stale launch copy. Reads files, never edits them.

Usage:
  python3 drift_check.py canon.json PATH [PATH ...] [--notion pages.json] [--out report.md]

PATH can be a folder, a file or a live page (https://...). A live page is read the
way crawlers and link previews read it: the raw HTML, no JavaScript. Folders are walked. Skipped: folders named
_superseded*, _retired*, _archive*, node_modules or .git, symlinks, binary files
and files over 5 MB.
--notion takes a JSON list of {"page", "id", "text"} if you export Notion text yourself.
With Claude, the skill reads Notion through the Notion connector instead.

What it reports:
  Stale        a retired phrase in current copy. Fix it or queue it.
  Close        text that's almost an approved line but not word for word. Check it.
  Skipped      lines it ignored on purpose (history, or a rule that quotes a banned
               phrase). Listed so nothing is hidden.

Matching ignores capital letters, curly vs straight quotes and extra spaces.
Web pages are checked for what people and machines read: visible text, alt text,
titles, meta and Open Graph descriptions, and JSON-LD.
Exit code: 0 when safe to ship, 1 when anything is stale or close, 2 when it couldn't check.
On GitHub Actions, the report also goes to the run's summary (see templates/github/).
"""
import datetime, difflib, html, json, os, re, sys, unicodedata, urllib.request

SKIP_DIRS = ('_superseded', '_retired', '_archive', 'node_modules', '.git')
EXTS = ('.md', '.mdx', '.txt', '.html', '.htm', '.ts', '.tsx', '.js', '.jsx', '.json', '.yml', '.yaml',
        '.xml', '.csv', '.svg', '.webmanifest', '.toml', '.astro', '.vue', '.svelte', '.liquid', '.mdc')
EXTRA_NAMES = ('_headers', '_redirects', 'llms.txt', 'CLAUDE.md', 'AGENTS.md')
MAX_BYTES = 5_000_000
# Words that mark a line as history or as a rule. A line is skipped only when it has
# one of these AND the stale phrase sits inside quote marks, like: Never say "teammate."
MARKERS = re.compile(r"(?i)\b(never|avoid|banned|don'?t (say|use)|instead of|retired|superseded|earlier draft|"
                     r"was|used to|old line|changelog|history|moved from|kept for the record)\b")
HISTORY_HEADING = re.compile(r'(?i)^#+\s.*\b(changelog|history|archive|retired|superseded|decisions log|old versions?)\b')
AI_FILE = re.compile(r'(?i)(prompt|instruction|skill|claude\.md|agents\.md|system|voice|gpt)')
BLOCK_TAGS = r'(?i)</?(p|h[1-6]|li|ul|ol|div|section|article|header|footer|nav|main|br|tr|td|th|title|blockquote|figcaption|button|a)\b[^>]*>'

def N(s, case=False):
    """Normalize for matching: decode entities, unify quotes, collapse spaces, ignore case."""
    s = unicodedata.normalize('NFKC', html.unescape(s))
    for a, b in (('\u2019', "'"), ('\u2018', "'"), ('\u201c', '"'), ('\u201d', '"'), ('\u00a0', ' '), ('\u00ad', ''), ('\u200b', '')):
        s = s.replace(a, b)
    s = ' '.join(s.split())
    return s if case else s.casefold()

def core(phrase, case=False):
    return N(phrase, case).strip(' .,;:!?')

def atext(v):
    """An approved value can be a string or {"text": ...}."""
    return v.get('text', '') if isinstance(v, dict) else (v if isinstance(v, str) else '')

def words(s):
    return re.findall(r"[a-z0-9@'&+-]+", N(s))

def page_text(raw, path):
    """For web pages, keep what people and machines read, one block per line."""
    if not (path.lower().endswith(('.html', '.htm')) or path.startswith('http')):
        return raw
    ld = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', raw, flags=re.S | re.I)
    attrs = [a or b for a, b in re.findall(r'''(?i)\b(?:alt|aria-label|title|content|placeholder)\s*=\s*(?:"([^"]*)"|'([^']*)')''', raw)]
    body = re.sub(r'(?is)<(script|style|svg)\b.*?</\1>', ' ', raw)
    body = re.sub(BLOCK_TAGS, '\n', body)
    body = re.sub(r'<[^>]+>', ' ', body)
    return '\n'.join([html.unescape(body)] + attrs + ld)

def files(paths, out):
    for p in paths:
        if p.startswith(('http://', 'https://')):
            yield p
            continue
        p = os.path.expanduser(p)
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, fs in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith(SKIP_DIRS)]
            for f in fs:
                full = os.path.join(root, f)
                if f in ('canon.json', 'canon.example.json') or (out and os.path.abspath(full) == os.path.abspath(out)):
                    continue
                if f.lower().endswith(EXTS) or f in EXTRA_NAMES:
                    yield full

def readable(f):
    if f.startswith(('http://', 'https://')):
        req = urllib.request.Request(f, headers={'User-Agent': 'launch-hygiene-drift-check'})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read(MAX_BYTES).decode('utf-8', errors='ignore')
    if os.path.islink(f) or os.path.getsize(f) > MAX_BYTES:
        return None
    with open(f, 'rb') as fh:
        raw = fh.read()
    if b'\x00' in raw[:4096]:
        return None
    return raw.decode('utf-8', errors='ignore')

def quoted(phrase_n, line_n):
    """True when the phrase sits inside quote marks or backticks on this line."""
    for a, b in re.findall(r'"([^"]+)"|`([^`]+)`', line_n):
        if phrase_n.casefold() in core(a or b):
            return True
    return False

def scan(text, where, canon, out):
    approved = [(k, atext(v)) for k, v in canon.get('approved', {}).items() if len(words(atext(v))) >= 4 and '[' not in atext(v)]
    in_history = False
    lines = [l for l in text.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        if re.match(r'^#+\s', line.strip()):
            in_history = bool(HISTORY_HEADING.match(line.strip()))
        ln = N(line)
        for r in canon.get('retired', []):
            c = bool(r.get('match_case'))
            f, here = core(r['find'], c), N(line, c)
            if not f or '[' in f:
                continue
            nxt = N(lines[i + 1], c) if i + 1 < len(lines) else ''
            # A phrase can wrap onto the next line. Count it here only if it isn't whole on the next line.
            if f not in here and not (f in N(line + ' ' + (lines[i + 1] if i + 1 < len(lines) else ''), c) and f not in nxt):
                continue
            if any(N(ok) in ln for ok in r.get('ok_if', [])):
                continue
            use = atext(canon.get('approved', {}).get(r.get('use', ''), '')) or r.get('use', '')
            hit = {'where': where, 'find': r['find'], 'use': use, 'why': r.get('why', ''), 'line': line.strip()[:220]}
            if in_history or (MARKERS.search(ln) and quoted(f, ln)):
                out['skipped'].append(hit)
            else:
                hit['ai'] = bool(AI_FILE.search(where))
                out['stale'].append(hit)
        lw = words(line)
        for k, a in approved:
            aw = words(a)
            if not lw or ' '.join(aw) in ' '.join(lw):
                continue
            n = len(aw)
            best = 0.0
            for size in (n - 1, n, n + 1):
                for j in range(0, max(1, len(lw) - size + 1)):
                    best = max(best, difflib.SequenceMatcher(None, aw, lw[j:j + size]).ratio())
            if best >= 0.84 and not any(N(ok) in ln for ok in canon.get('ok_close', [])):
                out['close'].append({'where': where, 'name': k, 'approved': a, 'line': line.strip()[:220], 'score': round(best, 2)})

def claims_to_retired(canon):
    """A claim that isn't approved, or is past its review date, counts as retired."""
    today = datetime.date.today().isoformat()
    for c in canon.get('claims', []):
        say = c.get('say', '')
        if not say or '[' in say:
            continue
        due = str(c.get('review_by', '') or '')
        if c.get('status') != 'approved':
            why = f"Claim not approved ({c.get('status', 'no status')}). Ask {c.get('approved_by', 'the owner')}."
        elif due and due < today:
            why = f"Claim past its review date ({due}). Ask {c.get('approved_by', 'the owner')} to re-check the source."
        else:
            continue
        canon.setdefault('retired', []).append({'find': say, 'use': 'cut it, or get it approved', 'why': why})

def cell(s):
    return str(s).replace('|', '/').replace('\n', ' ')

def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    canon = json.load(open(a[0], encoding='utf-8'))
    claims_to_retired(canon)
    out_path = None; notion = None; paths = []
    i = 1
    while i < len(a):
        if a[i] in ('--out', '--notion'):
            if i + 1 >= len(a):
                sys.exit(f'{a[i]} needs a file name after it.')
            if a[i] == '--out': out_path = a[i + 1]
            else: notion = a[i + 1]
            i += 2
        else:
            paths.append(a[i]); i += 1
    missing = [p for p in paths if not os.path.exists(os.path.expanduser(p))]
    if missing:
        print(f'Not checked. These paths don\'t exist: {", ".join(missing)}')
        sys.exit(2)
    res = {'stale': [], 'close': [], 'skipped': []}
    n = 0
    for f in files(paths, out_path):
        try:
            raw = readable(f)
        except (OSError, ValueError) as e:
            print(f'Could not read {f}: {e}')
            raw = None
        if raw is None:
            continue
        n += 1
        scan(page_text(raw, f), f, canon, res)
    if notion:
        for b in json.load(open(notion, encoding='utf-8')):
            n += 1
            scan(b['text'], f"Notion · {b['page']} · {str(b.get('id', ''))[:8]}", canon, res)
    if n == 0:
        print('Not checked. No readable files or pages were found.')
        sys.exit(2)
    stale = sorted(res['stale'], key=lambda h: not h['ai'])
    ver = f" v{canon['version']}" if canon.get('version') else ''
    L = ['# Drift check', '', ('Canon' + ver + '. ' if ver else '') + f'Checked {n} {"file or page" if n == 1 else "files or pages"} against {len([r for r in canon.get("retired", []) if '[' not in r.get('find', '')])} retired phrases and '
         f'{len([1 for v in canon.get("approved", {}).values() if atext(v) and "[" not in atext(v)])} approved lines.', '']
    if stale:
        L += [f'## Stale ({len(stale)}): fix or queue', '',
              'AI instructions come first: a prompt or skill with an old line writes new copy with it.', '',
              '| Where | Found | Use instead | Why | Line |', '|---|---|---|---|---|']
        L += [f"| {'AI instructions: ' if h['ai'] else ''}{cell(h['where'])} | {cell(h['find'])} | {cell(h['use'])} | {cell(h['why'])} | {cell(h['line'])} |" for h in stale]
        L.append('')
    if res['close']:
        L += [f"## Close to an approved line ({len(res['close'])}): check", '',
              'Approved lines should appear word for word. If a match is on purpose (a headline, a quote), add the line to "ok_close" in the canon.', '',
              '| Where | Approved line | Found | Match |', '|---|---|---|---|']
        L += [f"| {cell(c['where'])} | {cell(c['approved'])} | {cell(c['line'])} | {c['score']} |" for c in res['close']]
        L.append('')
    if res['skipped']:
        L += [f"## Skipped on purpose ({len(res['skipped'])})", '', 'History, or a rule that quotes a banned phrase. Check the list once.', '',
              '| Where | Phrase | Line |', '|---|---|---|']
        L += [f"| {cell(h['where'])} | {cell(h['find'])} | {cell(h['line'])} |" for h in res['skipped']]
        L.append('')
    if not stale and not res['close']:
        L.append(f'Verdict: Safe to ship against canon{ver}. 0 drift across the {n} {"file or page" if n == 1 else "files or pages"} checked. Anything not listed above was not checked.')
    else:
        L.append(f"Verdict: Not yet. {len(stale)} stale, {len(res['close'])} to check. Fix or queue them, then run it again.")
    report = '\n'.join(L) + '\n'
    if out_path:
        if os.path.exists(out_path) and not open(out_path, encoding='utf-8', errors='ignore').read(20).startswith('# Drift check'):
            print(f'Not writing {out_path}: it already exists and isn\'t a drift report.')
            sys.exit(2)
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(report)
    print(report)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:  # On GitHub, show the report on the pull request's checks page.
        with open(summary, 'a', encoding='utf-8') as fh:
            fh.write(report)
    sys.exit(0 if not stale and not res['close'] else 1)

if __name__ == '__main__':
    main()
