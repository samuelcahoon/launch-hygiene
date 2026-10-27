#!/usr/bin/env python3
"""Launch hygiene drift check. Finds retired phrases in current copy.

Usage:
  python3 drift_check.py canon.json PATH [PATH ...] [--notion notion_dump.json] [--out report.md]

PATH can be a folder or a file. Folders are walked; anything inside a folder
named _superseded*, _retired*, node_modules or .git is skipped (that's history).
--notion takes a JSON list of {"page", "id", "text"} if you export Notion text yourself.
With Claude, the skill reads Notion through the Notion connector instead.
"""
import json, os, re, sys, html

SKIP_DIRS = ('_superseded', '_retired', 'node_modules', '.git', 'screens')
EXTS = ('.md', '.mdx', '.txt', '.ts', '.tsx', '.js', '.json', '.yml', '.yaml', '.html', '_headers', '_redirects')
# Lines that are history on purpose (changelogs, old drafts) are skipped. Add your own markers here.
HISTORY = ('SUPERSEDED', 'Superseded', 'Earlier draft', 'earlier draft', 'kept for the record', 'Retired', 'retired', 'Changelog', 'Moved from', 'moved from')
# Lines that state a rule (a Never list, a banned-words regex) mention retired words on purpose.
RULE = re.compile(r'(?i)\bnever\b|\bavoid\b|banned|search (it|the copy)[^\n]*for|^\s*/.+/[a-z]*,?\s*(//.*)?$|"find":|pre-flight|Never list|not "|instead of|The phrase')

def visible_text(raw, path):
    if path.endswith('.html'):
        raw = re.sub(r'<helmet>.*?</helmet>', '', raw, flags=re.S)
        raw = re.sub(r'<script.*?</script>', '', raw, flags=re.S)
        raw = re.sub(r'<style.*?</style>', '', raw, flags=re.S)
        attrs = ' '.join(re.findall(r'(?:alt|aria-label|title|href)="([^"]*)"', raw))
        raw = html.unescape(re.sub(r'<[^>]+>', '\n', raw)) + '\n' + attrs
    return raw

def files(paths):
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, fs in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith(SKIP_DIRS)]
            for f in fs:
                if (f.endswith(EXTS) or f in ('_headers', '_redirects')) and f not in ('canon.json', 'canon.example.json'):
                    yield os.path.join(root, f)

def scan(text, where, canon, hits):
    for line in text.splitlines():
        if not line.strip() or any(h in line for h in HISTORY) or RULE.search(line):
            continue
        for r in canon['retired']:
            if r['find'] in line and not any(ok in line for ok in r.get('ok_if', [])):
                hits.append({'where': where, 'find': r['find'], 'use': canon['approved'].get(r['use'], r['use']), 'why': r['why'], 'line': line.strip()[:220]})

def main():
    a = sys.argv[1:]
    canon = json.load(open(a[0]))
    out = None; notion = None; paths = []
    i = 1
    while i < len(a):
        if a[i] == '--out': out = a[i + 1]; i += 2
        elif a[i] == '--notion': notion = a[i + 1]; i += 2
        else: paths.append(a[i]); i += 1
    hits = []
    n = 0
    for f in files(paths):
        try:
            raw = open(f, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        n += 1
        scan(visible_text(raw, f), f, canon, hits)
    if notion:
        for b in json.load(open(notion)):
            n += 1
            scan(b['text'], f"Notion · {b['page']} · {b['id'][:8]}", canon, hits)
    lines = [f"# Drift check", f"", f"Scanned {n} files or blocks. Found {len(hits)} retired phrase(s).", ""]
    if hits:
        lines += ["| Where | Found | Use instead | Why | Line |", "|---|---|---|---|---|"]
        for h in hits:
            cell = lambda s: s.replace('|', '/').replace('\n', ' ')
            lines.append(f"| {cell(h['where'])} | {cell(h['find'])} | {cell(h['use'])} | {cell(h['why'])} | {cell(h['line'])} |")
    lines.append('')
    lines.append('Verdict: ' + ('Safe to ship. 0 drift.' if not hits else f'Not yet. Fix or queue the {len(hits)} line(s) above, then run it again.'))
    report = '\n'.join(lines)
    if out: open(out, 'w').write(report)
    print(report)

if __name__ == '__main__':
    main()
