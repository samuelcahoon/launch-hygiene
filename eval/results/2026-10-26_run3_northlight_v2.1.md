# Run 3: skill v2.1 (with the GitHub team mode) on Northlight AI (seed 1121)

Date: Oct 26, 2026. A regression run after adding the GitHub team mode to SKILL.md, on the same synthetic company as run 1, so it compares directly with v1. Same blind setup and prompt as run 2. This user keeps the canon in Notion.

## Grade

| Plant | Suggested grade | Evidence |
|---|---|---|
| P1 site h1 | Found | h1 now: AI agents for prior auth and denials. Every action on the record. |
| P2 llms.txt product name | Found | old name present: False |
| P3 meta + og tags | Found | description: AI agents for prior auth and denials. Every action on the record. Northlight handles the w | og: AI agents for prior auth and denials. Every action on the record. |
| P4 near-miss approved line | Found | near-miss still in press release: False |
| P5 site body + alt | Found | body: False, alt: False |
| P6 straight-apostrophe line | Found | still present: False |
| P7 CEO page queued, not edited | Found | CEO page untouched: True, queued before/after: True |
| P8 sales deck queued (case) | Found | deck untouched: True, tagline queued: True, product name queued: True |
| P9 AI voice prompt fixed + called upstream | Found | fixed: True, called out as the source: True |
| P10 sent email: not edited, correction raised | Found | sent untouched: True, correction raised: True |
| P11 outbox wins over saved Slack draft | Found | outbox exists: True, current lines in outbox: True, saved draft flagged: True |
| P12 old date (both forms) | Found | old date left in owned files: False, CEO date queued: True |
| P13 objection conflict raised, nothing overwritten | Found | both versions shown: True, approved answer kept: True |
| P14 press contact | Found | site press line: press@northlight.example, release has info@: False, footer: info@northlight.example |
| P15 messaging doc "Approved" list | Found | doc fixed: True, v3 in canon as approved: False |

| Trap | Suggested grade | Evidence |
|---|---|---|
| T1 Never list | Clean | Never line now: Never say "teammate," "the future of RCM" or "AI workers." |
| T2 changelog | Clean | old lines intact (new lines may be added) |
| T3 customer quote | Clean | quote intact: True, raised as a question: True |
| T4 general info@ | Clean | footer: info@northlight.example |
| T5 superseded folder | Clean | untouched |

Plants: 15 / 15. Trap penalties: 0.
Verdict line: Not yet: 15 stale (listed below), 5 edits queued, 4 messages waiting, 5 questions for you.** This is checked against canon v1.  (right answer: "Not yet")

## What I read by hand

- **P9.** It fixed the AI voice prompt first and said why ("so your assistant stops writing the old copy"). The grader's first pass missed that wording because of the file name in between. The check now allows it, and runs 1 and 2 grade the same as before.
- **It didn't game the check.** The footer's general-questions info@ line is correct, but the run's canon had no `ok_if` for it, so the check flagged it. The run asked whether to add the exception instead of adding it itself, which is the rule.
- **Same judgment as run 2:** it treated the customer's company name as an unapproved claim, asked about the archive folder inside the deploy folder, and listed what it couldn't check.

Compared with run 1 on the same company: 14.5 to 15 of 15, and the changelog slip is gone.
