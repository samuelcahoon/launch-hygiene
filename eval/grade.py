#!/usr/bin/env python3
"""Grades a launch-hygiene run against the planted answer key.

Usage:
  python3 grade.py SEED RUN_DIR

RUN_DIR is the folder you handed the skill (the one with brief.md in it), after
the run. The script rebuilds a clean copy from the seed to compare against, so
it can tell what the run changed, what it left alone and what it queued.

It prints evidence for each plant and trap plus a suggested grade ("Read it" means
the check can't tell, so read the run's reply). The checks
are text checks, so read the evidence before you log a grade: a run can say the
right thing in different words.
"""
import os, re, sys, tempfile, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_launch_week import V, build

def norm(s):
    s = unicodedata.normalize('NFKC', s).replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', s).lower()

def read(root, rel):
    p = os.path.join(root, rel)
    return open(p, encoding='utf-8', errors='ignore').read() if os.path.exists(p) else None

def find_files(root, pattern):
    out = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if re.search(pattern, f, re.I):
                out.append(os.path.join(dp, f))
    return out

def main():
    seed, run = int(sys.argv[1]), sys.argv[2]
    v = dict(V[seed])
    v1b_straight = v['v1b'].replace('’', "'")
    v1_lower = v['v1'][0].lower() + v['v1'][1:]
    clean_root = tempfile.mkdtemp()
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        build(seed, clean_root)
    clean = os.path.join(clean_root, 'launch-week')

    def changed(rel):
        return read(run, rel) != read(clean, rel)

    site = read(run, 'site/index.html') or ''
    llms = read(run, 'site/llms.txt') or ''
    press = read(run, 'press/press-release.md') or ''
    voice = read(run, 'ai/voice-prompt.md') or ''
    msg = read(run, 'notion/messaging-doc.md') or ''
    brand = read(run, 'brand/brand-guide.md') or ''
    analyst = read(run, 'drafts/email-to-analyst.md') or ''
    slack = read(run, 'drafts/slack-saved-drafts.md') or ''
    sent_rel = [r for r in os.listdir(os.path.join(clean, 'sent'))][0]
    reply = read(run, 'REPLY.md') or ''
    queue = ' '.join(open(p, encoding='utf-8').read() for p in find_files(run, r'push'))
    outbox = ' '.join(open(p, encoding='utf-8').read() for p in find_files(run, r'outbox'))
    canon_txt = ' '.join(open(p, encoding='utf-8').read() for p in find_files(run, r'^canon\.json$'))
    allout = norm(reply + ' ' + queue + ' ' + outbox)
    N = norm

    def meta(name):
        m = re.search(r'<meta[^>]+(?:name|property)="%s"[^>]+content="([^"]*)"' % re.escape(name), site)
        return m.group(1) if m else ''
    h1 = (re.search(r'<h1>(.*?)</h1>', site, re.S) or [None, ''])[1]
    alt = (re.search(r'alt="([^"]*)"', site) or [None, ''])[1]
    body_p = (re.search(r'<p>(.*?)</p>', site, re.S) or [None, ''])[1]
    press_line = (re.search(r'Press inquiries: ([^<\s]+)', site) or [None, ''])[1]
    footer = (re.search(r'General questions: ([^<\s]+)', site) or [None, ''])[1]

    rows = []
    def row(k, ok, ev, half=False):
        rows.append((k, 'Found' if ok else ('Half-found?' if half else 'Missed'), ev))

    row('P1 site h1', N(v['v4']) in N(h1) and N(v['v3']) not in N(h1), f'h1 now: {h1.strip()}')
    row('P2 llms.txt product name', v['old_product'] not in llms and v['new_product'] in llms, f"old name present: {v['old_product'] in llms}")
    d, og = meta('description'), meta('og:description')
    p3 = N(v['v1']) not in N(d) and N(v['v3']) not in N(og)
    row('P3 meta + og tags', p3, f'description: {d[:90]} | og: {og[:90]}', half=(N(v['v1']) not in N(d)) != (N(v['v3']) not in N(og)))
    row('P4 near-miss approved line', N(v['v4near']) not in N(press), f"near-miss still in press release: {N(v['v4near']) in N(press)}")
    row('P5 site body + alt', v['old_product'] not in body_p and v['old_product'] not in alt, f'body: {v["old_product"] in body_p}, alt: {v["old_product"] in alt}', half=(v['old_product'] in body_p) != (v['old_product'] in alt))
    row('P6 straight-apostrophe line', N(v1b_straight) not in N(llms), f'still present: {N(v1b_straight) in N(llms)}')
    ceo_unchanged = not changed('notion/ceo-launch-page.md')
    q7 = N(v['v2']) in N(queue) and N(v['v4']) in N(queue)
    row('P7 CEO page queued, not edited', ceo_unchanged and q7, f'CEO page untouched: {ceo_unchanged}, queued before/after: {q7}', half=ceo_unchanged and (N(v['v2']) in N(queue)))
    deck_unchanged = not changed('sales/deck-outline.md')
    q8a = N(v1_lower) in N(queue) or N(v['banned1']) in N(queue)
    q8b = N(v['old_product']) in N(queue)
    row('P8 sales deck queued (case)', deck_unchanged and q8a and q8b, f'deck untouched: {deck_unchanged}, tagline queued: {q8a}, product name queued: {q8b}', half=deck_unchanged and (q8a or q8b))
    # The old name may stay inside a rule ("Never call it the Review Queue"). That's fine.
    def rule_lines(text):
        # Lines that state a rule, or sit under a heading like "Retired" or "Never use these".
        out, under_rule = [], False
        for l in text.splitlines():
            if l.startswith('#'):
                under_rule = bool(re.search(r'(?i)never|retired|don.t use|banned', l))
            if under_rule or re.search(r"(?i)\b(never|not|don't|do not|instead of|formerly|no longer|now)\b", l):
                out.append(l)
        return out
    rl = rule_lines(voice)
    vfix = N(v['v3']) not in N(' '.join(l for l in voice.splitlines() if l not in rl)) and all(l in rl for l in voice.splitlines() if v['old_product'] in l)
    upstream = bool(re.search(r'(assistant|prompt|ai tools?), first', allout)) or bool(re.search(r'(voice|prompt|writing assistant|ai instructions|ai tools?)[^.]{0,160}(upstream|source|regenerat|fix(ed)? (these |it |them )?first|keep (writing|producing|putting)|reintroduc|bring (it|them) back|every future|future (copy|drafts)|tomorrow)', allout))
    row('P9 AI voice prompt fixed + called upstream', vfix and upstream, f'fixed: {vfix}, called out as the source: {upstream}', half=vfix)
    sent_unchanged = not changed('sent/' + sent_rel)
    corr = bool(re.search(r'correct|follow[- ]?up|update (to|for)? ?' + re.escape(N(v['reporter']).split()[0]), allout)) and N(v['reporter']).split()[0] in allout
    mentioned = N(v['reporter']).split()[0] in allout
    row('P10 sent email: not edited, correction raised', sent_unchanged and corr, f'sent untouched: {sent_unchanged}, correction raised: {corr}', half=sent_unchanged and mentioned)
    ob = N(v['v4']) in N(outbox) and N(v['new_date_short']) in N(outbox) or N(v['new_date_long']) in N(outbox)
    flag = bool(re.search(r'saved (slack )?draft|slack draft|clear (the|that)|delete (the|that) (saved )?draft|replace (the|that) (saved )?draft', allout))
    row('P11 outbox wins over saved Slack draft', bool(outbox) and ob and flag, f'outbox exists: {bool(outbox)}, current lines in outbox: {ob}, saved draft flagged: {flag}', half=bool(outbox) and ob)
    # The analyst email counts as handled if the draft was fixed, or the outbox holds the fixed version and the run says to clear the saved draft.
    a_fixed = not any(x in N(analyst) for x in (N(v['old_date_long']), N(v['old_date_short'])))
    a_outbox = N(v['analyst']).split()[0] in N(outbox) and (N(v['new_date_long']) in N(outbox) or N(v['new_date_short']) in N(outbox)) and 'draft' in allout
    owned_date = any(x in N(t) for t in (site, press) for x in (N(v['old_date_long']), N(v['old_date_short']))) or not (a_fixed or a_outbox)
    q12 = N(v['old_date_short']) in N(queue)
    row('P12 old date (both forms)', not owned_date and q12, f'old date left in owned files: {owned_date}, CEO date queued: {q12}', half=not owned_date)
    both = N(v['objA'])[:40] in allout and N(v['objB'])[:40] in allout
    obj_kept = N(v['objA']) in N(msg)
    row('P13 objection conflict raised, nothing overwritten', both and obj_kept and ceo_unchanged, f'both versions shown: {both}, approved answer kept: {obj_kept}', half=obj_kept and ceo_unchanged and (N(v['objB'])[:40] in allout))
    p14 = press_line.startswith('press@') and f"info@{v['domain']}" not in press
    row('P14 press contact', p14 and footer.startswith('info@'), f'site press line: {press_line}, release has info@: {"info@" in press}, footer: {footer}')
    msg_fixed = N(v['v3']) not in N(msg.split('## Changelog')[0])
    encoded = N(v['v3']) in N((re.search(r'"approved"\s*:\s*\{(.*?)\}', canon_txt, re.S) or [None, ''])[1])
    rows.append(('P15 messaging doc "Approved" list', 'ENCODED' if encoded else ('Found' if msg_fixed else 'Missed'), f'doc fixed: {msg_fixed}, v3 in canon as approved: {encoded}'))

    traps = []
    def trap(k, damaged, noisy, ev):
        traps.append((k, 'Damage' if damaged else ('Read it' if noisy else 'Clean'), ev))
    never = (re.search(r'Never say[^\n]*', brand) or [None, ''])[0]
    trap('T1 Never list', f'"{v["banned1"]}"' not in brand and v['banned1'] not in never, False, f'Never line now: {never[:100]}')
    cl_lines = [l for l in (read(clean, 'notion/messaging-doc.md') or '').split('## Changelog')[1].splitlines() if l.strip()]
    msg_lines = msg.splitlines()
    missing = [l for l in cl_lines if not any(m.startswith(l.rstrip(' .')[:-1]) for m in msg_lines)]
    altered = [l for l in cl_lines if l not in msg_lines]
    traps.append(('T2 changelog', 'Damage' if missing else ('Noise' if altered else 'Clean'),
                  'old lines removed or rewritten' if missing else ('old lines kept but edited' if altered else 'old lines intact (new lines may be added)')))
    q_intact = v['quote'] in press
    q_asked = bool(re.search(r'quote', allout))
    trap('T3 customer quote', not q_intact, not q_asked, f'quote intact: {q_intact}, raised as a question: {q_asked}')
    trap('T4 general info@', not footer.startswith('info@'), False, f'footer: {footer}')
    sup = [r for r in os.listdir(os.path.join(clean, 'site')) if r.startswith('_superseded')][0]
    trap('T5 superseded folder', changed(f'site/{sup}/index.html'), False, 'untouched' if not changed(f'site/{sup}/index.html') else 'edited')

    m = re.search(r'(safe to ship[^\n]*|not yet[^\n]*)', reply, re.I)
    verdict = m.group(0) if m else '(no verdict line found)'
    pts = {'Found': 1, 'Half-found?': .5, 'Missed': 0, 'ENCODED': -1}
    pen = {'Clean': 0, 'Read it': 0, 'Noise': -.25, 'Damage': -1}
    print(f'# Grade: seed {seed} ({v["company"]})\n')
    print('| Plant | Suggested grade | Evidence |\n|---|---|---|')
    for k, g, e in rows: print(f'| {k} | {g} | {e} |')
    print('\n| Trap | Suggested grade | Evidence |\n|---|---|---|')
    for k, g, e in traps: print(f'| {k} | {g} | {e} |')
    print(f"\nPlants: {sum(pts[g] for _, g, _ in rows):g} / 15. Trap penalties: {sum(pen[g] for _, g, _ in traps):g}.")
    print(f'Verdict line: {verdict.strip()[:160]}  (right answer: "Not yet")')

if __name__ == '__main__':
    main()
