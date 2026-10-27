#!/usr/bin/env python3
"""Script-only test: how many planted stale lines does a drift_check.py version flag?

Usage:
  python3 script_benchmark.py SEED path/to/drift_check.py

Builds the synthetic launch week for SEED, writes the canon a user would write from
the brief (every line the decisions log names, plus both forms of the old date), runs
the script on the current-copy folders and counts which planted lines it flags.
Sent mail and archived folders aren't scanned: they're history.
This tests the script alone. The full skill run (grade.py) also tests judgment.
"""
import json, os, re, subprocess, sys, tempfile, contextlib, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_launch_week import V, build
from grade import norm

def main():
    seed, script = int(sys.argv[1]), sys.argv[2]
    v = dict(V[seed])
    root = tempfile.mkdtemp()
    with contextlib.redirect_stdout(io.StringIO()):
        build(seed, root)
    lw = os.path.join(root, 'launch-week')
    canon = {
        "approved": {"tagline": v['v4'], "product_name": v['new_product'], "launch_date": v['new_date_long'],
                     "press_contact": f"press@{v['domain']}"},
        "retired": [
            {"find": v['v1'], "use": "tagline", "why": "retired"},
            {"find": v['v1b'], "use": "tagline", "why": "retired"},
            {"find": v['v2'], "use": "tagline", "why": "retired"},
            {"find": v['v3'], "use": "tagline", "why": "retired"},
            {"find": v['old_product'], "use": "product_name", "why": "renamed"},
            {"find": v['old_date_long'], "use": "launch_date", "why": "moved"},
            {"find": v['old_date_short'], "use": "launch_date", "why": "moved"},
            {"find": f"info@{v['domain']}", "use": "press_contact", "why": "press moved", "ok_if": ["General questions"]},
            {"find": v['banned1'], "use": v['use_instead'], "why": "word list"},
        ],
    }
    cp = os.path.join(root, 'canon.json')
    json.dump(canon, open(cp, 'w'))
    targets = [os.path.join(lw, d) for d in ('site', 'llms', 'notion', 'brand', 'press', 'ai', 'sales', 'drafts') if os.path.exists(os.path.join(lw, d))]
    out = os.path.join(root, 'report.md')
    subprocess.run([sys.executable, script, cp, *targets, '--out', out], capture_output=True, text=True)
    rep = open(out).read() if os.path.exists(out) else ''
    stale_part = rep.split('## Skipped')[0]
    lines_flagged = []
    for r in stale_part.splitlines():
        if not r.startswith('| ') or r.startswith('| Where') or r.startswith('|---'):
            continue
        cols = [c.strip() for c in r.strip('|').split(' | ')]
        line = cols[-1] if len(cols) == 5 else (cols[2] if len(cols) == 4 else '')
        lines_flagged.append((cols[0], norm(line)))
    v1b_straight = v['v1b'].replace('\u2019', "'")
    # (file, a piece of the planted line, how many stale phrases that line holds, label)
    expect = [
        ('site/index.html', v['v3'], 2, 'h1 and og:description'), ('site/index.html', v['v1'], 1, 'meta description'),
        ('site/index.html', 'Launching', 1, 'banner date'), ('site/index.html', 'Every agent action lands', 1, 'body copy product name'),
        ('site/index.html', 'showing an exported', 1, 'image alt text'), ('site/index.html', 'Press inquiries', 1, 'press contact'),
        ('site/llms.txt', v1b_straight, 1, 'line with a straight apostrophe'), ('site/llms.txt', v['old_product'] + ':', 1, 'product name'),
        ('notion/messaging-doc.md', 'Tagline:', 1, '"Approved" tagline'), ('notion/messaging-doc.md', 'Proof:', 1, 'product name'),
        ('notion/ceo-launch-page.md', v['v2'], 1, 'CEO line'), ('notion/ceo-launch-page.md', ', embargo', 1, 'CEO date'),
        ('brand/brand-guide.md', v['v3'], 1, 'tagline'), ('brand/brand-guide.md', '(always capitalized)', 1, 'product name'),
        ('press/press-release.md', v['v4near'], 1, 'near-miss of the approved line'), ('press/press-release.md', 'Every decision lands', 1, 'product name'),
        ('press/press-release.md', 'EMBARGOED', 1, 'embargo date'), ('press/press-release.md', 'Media contact', 1, 'press contact'),
        ('ai/voice-prompt.md', 'Always open launch copy', 1, 'AI instructions tagline'), ('ai/voice-prompt.md', 'Call ', 1, 'AI instructions product name'),
        ('sales/deck-outline.md', 'Slide 1', 1, 'lowercase tagline'), ('sales/deck-outline.md', 'Slide 4', 1, 'lowercase product name'),
        ('drafts/slack-saved-drafts.md', 'our line is locked', 2, 'saved Slack draft line and date'), ('drafts/slack-saved-drafts.md', 'can you swap slide 1', 1, 'saved Slack DM'),
        ('drafts/email-to-analyst.md', 'Ahead of our launch', 2, 'email date and line'), ('drafts/email-to-analyst.md', 'walk you through', 1, 'email product name'),
    ]
    total = sum(n for _, _, n, _ in expect)
    found = 0
    misses = []
    for rel, marker, n, label in expect:
        got = sum(1 for w, l in lines_flagged if w.endswith(rel) and norm(marker) in l)
        found += min(n, got)
        if got < n:
            misses.append(f'{rel}: {label} ({got} of {n})')
    traps = [('brand/brand-guide.md', 'Never say'), ('notion/messaging-doc.md', 'tried'), ('notion/messaging-doc.md', 'retired'),
             ('site/index.html', 'General questions')]
    false_alarms = [f'{rel}: {k}' for rel, k in traps if any(w.endswith(rel) and norm(k) in l for w, l in lines_flagged)]
    print(f'{os.path.basename(os.path.dirname(os.path.abspath(script)))}/{os.path.basename(script)} on seed {seed} ({v["company"]}): '
          f'flagged {found} of {total} planted stale phrases. False alarms on traps: {len(false_alarms)}.')
    for m in misses:
        print('  missed:', m)
    for f in false_alarms:
        print('  false alarm:', f)

if __name__ == '__main__':
    main()
