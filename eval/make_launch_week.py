#!/usr/bin/env python3
"""Builds a synthetic launch week to test the launch-hygiene skill.

Usage:
  python3 make_launch_week.py SEED OUT_DIR

SEED picks the company: 1121 is Northlight AI (prior auth and denials agents),
7788 is Harborline (accounts payable automation). Both are fictional. Every name,
email, quote and date is made up.

It writes two things:
  OUT_DIR/launch-week/   the folder you hand the skill (no answers inside)
  OUT_DIR/answer_key.md  what a good run should find. Read it after the run.

The idea, borrowed from the Synthetic GTM Lab: plant the flaws first, then write
the files that hide them. A skill you can't grade is a skill you can't improve.
"""
import os, sys, textwrap

V = {
  1121: dict(
    company="Northlight AI", short="Northlight", domain="northlight.example",
    what="AI agents for prior authorizations and denials",
    pmm="Sasha Ortiz", ceo="Priya Raman", sales="Marcus Bell", reporter="Jo Park", outlet="Health Tech Daily",
    analyst="Rina Shah", firm="Clearview Research",
    v1="Your AI teammate for revenue operations.",
    v1b="Revenue cycle automation you’ll never have to explain.",
    v2="Provable automation for prior auth and denials.",
    v3="Prior auth and denials, handled by agents you can audit.",
    v4="AI agents for prior auth and denials. Every action on the record.",
    v4near="AI agents for prior auth and denials. Every action on record.",
    old_product="Review Queue", new_product="Northlight Record",
    product_job="the human approval layer, where every agent action is logged with the policy it cited",
    old_date_long="Tuesday, February 9", old_date_short="Tue Feb 9",
    new_date_long="Wednesday, February 10", new_date_short="Wed Feb 10",
    d1="Mon Feb 1", d2="Tue Feb 2", d3="Wed Feb 3", d4="Thu Feb 4",
    banned1="teammate", banned2="the future of RCM", banned3="AI workers", use_instead="AI agents",
    objA="We’re SOC 2 Type II today, and HITRUST r2 is in progress, with a target date we’ll share under NDA.",
    objB="We’re SOC 2 Type II today. HITRUST r2 certification is underway.",
    obj_q="Do you have HITRUST?",
    quote="“It’s like having a teammate who never sleeps,” said Dr. Ana Ruiz, CFO of Ironwood Specialty Group.",
    customer="Ironwood Specialty Group", buyer="revenue cycle leaders",
  ),
  7788: dict(
    company="Harborline", short="Harborline", domain="harborline.example",
    what="accounts payable automation for mid-market finance teams",
    pmm="Theo Lang", ceo="Mara Okafor", sales="Dev Patel", reporter="Sam Reyes", outlet="Finance Ops Weekly",
    analyst="Lee Hart", firm="Northgate Advisory",
    v1="Your AI clerk for accounts payable.",
    v1b="AP automation you’ll actually trust.",
    v2="Touchless invoice processing for mid-market finance.",
    v3="Invoices paid on time, by agents your auditors can check.",
    v4="Invoices in, payments out, and a full audit trail in between.",
    v4near="Invoices in, payments out, with a full audit trail in between.",
    old_product="Approval Inbox", new_product="Harborline Ledger",
    product_job="where every invoice decision is logged with who approved it and why",
    old_date_long="Thursday, March 4", old_date_short="Thu Mar 4",
    new_date_long="Monday, March 8", new_date_short="Mon Mar 8",
    d1="Mon Mar 1", d2="Tue Mar 2", d3="Wed Mar 3", d4="Thu Mar 4",
    banned1="clerk", banned2="lights-out finance", banned3="bots", use_instead="agents",
    objA="We’re SOC 1 Type II today, and SOC 2 Type II lands this spring, with the report available under NDA.",
    objB="We’re SOC 1 Type II today. SOC 2 is underway.",
    obj_q="Are you SOC 2?",
    quote="“It’s like having a clerk who never takes a day off,” said Jamie Cole, controller at Brightwater Foods.",
    customer="Brightwater Foods", buyer="controllers and AP leads",
  ),
}

FILES = {
"brief.md": """\
# Launch week brief (from {pmm}, PMM)

Everything below is locked as of {d4}. Set up launch hygiene for the {short} launch, drift check every surface, fix what I own, queue what I don't, set up the outbox, and tell me if we're safe to ship.

## What I own
- `site/` (the launch site, including `llms.txt`)
- `notion/messaging-doc.md` (my messaging doc)
- `brand/brand-guide.md`
- `press/press-release.md` (my draft)
- `ai/voice-prompt.md` (the instructions my AI writing assistant follows)
- `drafts/` (my unsent drafts)

## What other people own
- `notion/ceo-launch-page.md`: {ceo}, CEO. Never edit without my OK.
- `sales/deck-outline.md`: {sales}, Head of Sales.

## Already sent
- `sent/`: messages that already went out.

## Decisions log
- {d1}: hero line "{v1}" retired. New line: "{v1b}" ({ceo})
- {d2}: changed to "{v2}" ({ceo} and {pmm})
- {d3}: changed to "{v3}" ({pmm})
- {d4}: FINAL, locked: "{v4}" ({ceo})
- {d4}: the {old_product} is now called the {new_product}.
- {d4}: launch moves from {old_date_long} to {new_date_long}. Embargo lifts 6:00 a.m. PT that day.
- {d4}: press contact is press@{domain}. info@{domain} stays for general questions only.
- Word list (standing): never "{banned1}," "{banned2}" or "{banned3}." Say "{use_instead}."
- {d3}: answer to "{obj_q}" approved by {pmm}: "{objA}"
""",

"site/index.html": """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{company} | {v4}</title>
<meta name="description" content="{v1} {short} handles the work your team shouldn’t have to.">
<meta property="og:description" content="{v3}">
</head>
<body>
<div class="banner">Launching {old_date_long}</div>
<h1>{v3}</h1>
<p>{what_cap}. Every agent action lands in the {old_product}, with the reason it was taken.</p>
<img src="/img/record.png" alt="The {old_product} showing an exported audit packet">
<section id="press"><p>Press inquiries: info@{domain}</p></section>
<footer><p>General questions: info@{domain}</p></footer>
</body>
</html>
""",

"site/llms.txt": """\
# {company}

> {v1b_straight}

{company} builds {what}.

## Product
- {old_product}: {product_job}.
- Pricing: talk to sales.

## Contact
- Press: press@{domain}
""",

"site/_superseded-{d1_slug}/index.html": """\
<!doctype html><html><body><h1>{v1}</h1><p>Kept for the record.</p></body></html>
""",

"notion/messaging-doc.md": """\
# Messaging doc
Owner: {pmm} · Last edited {d3}

## Approved (current)
- Tagline: {v3}
- Category: {what}
- Buyer: {buyer}
- Proof: the {old_product}, {product_job}

## Objections
- "{obj_q}" → {objA}

## Changelog
- {d1}: retired "{v1}"
- {d2}: tried "{v2}"
""",

"notion/ceo-launch-page.md": """\
# {short} launch: CEO page
Owner: {ceo} (CEO) · Last edited by {ceo} {d4}, 9:40 p.m.

## Our line
{v2}

## Launch date
{old_date_short}, embargo 6:00 a.m. PT

## If a reporter asks "{obj_q}"
{objB}

## My notes
Do not change this section. ({ceo})
""",

"brand/brand-guide.md": """\
# Brand guide v2

## Voice
Plain words. Sentence case. Never say "{banned1}," "{banned2}" or "{banned3}."

## Tagline
{v3}

## Product names
- {old_product} (always capitalized)
""",

"press/press-release.md": """\
EMBARGOED UNTIL {old_date_long}, 6:00 a.m. PT

# {company} launches {what}

{v4near}

{company} today launched {what}. Every decision lands in the {old_product}, so teams can show exactly what happened and why.

{quote}

Media contact: info@{domain}
""",

"ai/voice-prompt.md": """\
# Instructions for my writing assistant

- Write like {pmm}: plain, short sentences, sentence case.
- Always open launch copy with our tagline: "{v3}"
- Call {product_job_short} the {old_product}.
- Never use em dashes.
""",

"sales/deck-outline.md": """\
# Launch deck outline
Owner: {sales} (Head of Sales)

- Slide 1: {company}, {v1_lower}
- Slide 4: How the {old_product_lower} works
- Slide 9: Pricing
""",

"drafts/slack-saved-drafts.md": """\
# Saved drafts (exported from Slack)

## #launch-war-room (saved {d2}, 4:12 p.m.)
Team: our line is locked: "{v2}" Launch is {old_date_short}. Please use it everywhere.

## DM to {sales} (saved {d3}, 10:05 a.m.)
Hey, can you swap slide 1 to "{v3}" before Friday?
""",

"drafts/email-to-analyst.md": """\
To: {analyst} ({firm})
Subject: {short} launch briefing

Hi {analyst},

Ahead of our launch on {old_date_long}, here's the short version: {v3}

Happy to walk you through the {old_product} live.

{pmm}
""",

"sent/{d2_slug}_email-to-reporter.md": """\
SENT {d2}, 3:30 p.m.
To: {reporter} ({outlet})
Subject: Embargoed: {short} launch

Hi {reporter},

Under embargo until {old_date_long}: {v2}

{pmm}
""",
}

KEY = """\
# Answer key: launch week, seed {seed} ({company})

Synthetic. Grade each plant Found (1), Half-found (0.5), Missed (0) or Encoded (-1: the run adopted a stale line as current, or treated history as current).
Grade each trap Clean (0), Noise (-0.25: flagged it as drift to fix) or Damage (-1: changed it).

## Plants (15)

| # | Where | What's wrong | Found means |
|---|---|---|---|
| P1 | site/index.html `<h1>` | Retired line v3 "{v3}" | Fixed to v4 |
| P2 | site/llms.txt | Old product name "{old_product}" on the surface AI answer engines read | Fixed to "{new_product}" |
| P3 | site/index.html meta description and og:description | v1 and v3 in tags people never see but search, link previews and AI answers do | Both fixed |
| P4 | press/press-release.md line 5 | Near-miss of the approved line: "{v4near}" | Flagged as not word for word and fixed to v4 |
| P5 | site/index.html body copy and image alt text | "{old_product}" | Both fixed |
| P6 | site/llms.txt | v1b with a straight apostrophe: "{v1b_straight}" | Fixed (the curly-apostrophe canon entry must still match) |
| P7 | notion/ceo-launch-page.md | v2 on a page the PMM doesn't own | Queued with exact before and after. File NOT edited |
| P8 | sales/deck-outline.md | v1 in lowercase, "{old_product_lower}" in lowercase, page owned by Sales | Both queued (case-insensitive match). File NOT edited |
| P9 | ai/voice-prompt.md | v3 and "{old_product}" inside the instructions an AI follows | Fixed AND called out as the upstream source that will keep regenerating drift |
| P10 | sent/ email to {reporter} | v2 and the old date in a message already sent | Sent file NOT edited. Raised as a decision: send {reporter} a correction? Draft it in the outbox if so |
| P11 | drafts/slack-saved-drafts.md | Stale saved Slack draft for #launch-war-room (v2, old date) | Outbox holds the current version, and the run says to clear or replace the saved Slack draft before sending |
| P12 | site banner, press embargo line, CEO page, Slack draft, analyst email | Old date in two forms: "{old_date_long}" and "{old_date_short}" | Every instance fixed or queued (both forms in the canon) |
| P13 | notion/ceo-launch-page.md vs messaging doc | {ceo}'s newer answer to "{obj_q}" differs from the approved one | Both shown, owner asked. Neither overwritten |
| P14 | press release and site press line | Press contact still info@ | Fixed to press@, while the general-questions line stays |
| P15 | notion/messaging-doc.md | Lists v3 under "Approved (current)" | Treated as stale and fixed. Encoded if v3 lands in the canon as approved |

## Traps (5)

| # | Where | Why it's fine |
|---|---|---|
| T1 | brand guide Voice section | A Never list names banned words on purpose |
| T2 | messaging doc Changelog | History quotes old lines on purpose |
| T3 | press release customer quote | A customer's words. Don't edit a quote: ask whether to keep it, cut it or get a new one approved. Asking is Clean; editing is Damage |
| T4 | site footer "General questions: info@" | Still correct for general questions |
| T5 | site/_superseded-*/ | Archived on purpose |

## Score
Plants: sum of grades out of 15. Traps: sum of penalties. Report both, plus the run's final verdict line and whether it was right (the right verdict is "Not yet").
"""

def build(seed, out):
    v = dict(V[seed])
    v['seed'] = seed
    v['v1b_straight'] = v['v1b'].replace('’', "'")
    v['v1_lower'] = v['v1'][0].lower() + v['v1'][1:]
    v['old_product_lower'] = v['old_product'].lower()
    v['what_cap'] = v['what'][0].upper() + v['what'][1:]
    v['product_job_short'] = 'the human approval layer' if seed == 1121 else 'the approval log'
    v['d1_slug'] = v['d1'].lower().replace(' ', '-')
    v['d2_slug'] = v['d2'].lower().replace(' ', '-')
    root = os.path.join(out, 'launch-week')
    for name, body in FILES.items():
        path = os.path.join(root, name.format(**v))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(body.format(**v))
    with open(os.path.join(out, 'answer_key.md'), 'w') as f:
        f.write(KEY.format(**v))
    print(f"Built seed {seed} ({v['company']}) in {root}. Answer key: {os.path.join(out, 'answer_key.md')}")

if __name__ == '__main__':
    if len(sys.argv) != 3 or int(sys.argv[1]) not in V:
        sys.exit(f"Usage: python3 make_launch_week.py [{' | '.join(map(str, V))}] OUT_DIR")
    build(int(sys.argv[1]), sys.argv[2])
