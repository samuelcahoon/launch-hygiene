# Run 1: skill v1 on Northlight AI (seed 1121)

Date: Oct 26, 2026. Blind run: a fresh Claude session got the skill, the launch week and the prompt in `RUN_PROMPT.md`, and never saw the answer key. Synthetic company. Every name and line is made up.

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
| P9 AI voice prompt fixed + called upstream | Half-found? | fixed: True, called out as the source: False |
| P10 sent email: not edited, correction raised | Found | sent untouched: True, correction raised: True |
| P11 outbox wins over saved Slack draft | Found | outbox exists: True, current lines in outbox: True, saved draft flagged: True |
| P12 old date (both forms) | Found | old date left in owned files: False, CEO date queued: True |
| P13 objection conflict raised, nothing overwritten | Found | both versions shown: True, approved answer kept: True |
| P14 press contact | Found | site press line: press@northlight.example, release has info@: False, footer: info@northlight.example |
| P15 messaging doc "Approved" list | Found | doc fixed: True, v3 in canon as approved: False |

| Trap | Suggested grade | Evidence |
|---|---|---|
| T1 Never list | Clean | Never line now: Never say "teammate," "the future of RCM" or "AI workers." Say "AI agents." |
| T2 changelog | Noise | old lines kept but edited |
| T3 customer quote | Clean | quote intact: True, raised as a question: True |
| T4 general info@ | Clean | footer: info@northlight.example |
| T5 superseded folder | Clean | untouched |

Plants: 14.5 / 15. Trap penalties: -0.25.
Verdict line: Not yet. 5 stale lines and 1 disputed line are left. 5 edits are queued and 5 messages are waiting.**  (right answer: "Not yet")

## What I read by hand

- **P9, half.** It fixed the voice prompt but listed it as one fix among many. It didn't flag the prompt as the thing that would keep writing the old line into new copy.
- **T2, noise.** It added end dates to old changelog lines ("Retired Wed Feb 3"). The facts were true, but it edited history.
- **The real finding.** Four of the 15 plants (both meta tags, the near-miss of the approved line, the straight-apostrophe line and the lowercase sales slide) were found because the session checked by hand after the script missed them. The script skipped any line containing "never," didn't read meta tags, matched case exactly and never checked approved lines. A less careful session would have shipped those four and been told it was safe.
- **A bonus catch.** It noticed the archive folder sits inside `site/`, so it deploys, and asked whether to move it.

## What changed for v2

- The script reads meta, Open Graph, JSON-LD and alt text, ignores capitals and curly vs straight quotes, matches across line breaks, flags near misses of approved lines, and treats unapproved or expired claims as stale.
- A rule line is skipped only when the banned phrase is in quotes, and every skipped line is listed.
- SKILL.md: fix AI tools first, never edit old changelog lines, archive folders inside a deploy folder are live, the canon lives in Notion on Claude web, and the verdict names what wasn't checked.
