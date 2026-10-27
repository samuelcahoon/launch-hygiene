# Run 2: skill v2 on Harborline (seed 7788)

Date: Oct 26, 2026. Same blind setup as run 1, on a second synthetic company, so v2 couldn't pass by matching phrases it had already seen. The prompt adds one line for v2: the brief counts as the user's yes for fixing what they own, since v2 asks for one yes per batch of fixes.

## Grade

| Plant | Suggested grade | Evidence |
|---|---|---|
| P1 site h1 | Found | h1 now: Invoices in, payments out, and a full audit trail in between. |
| P2 llms.txt product name | Found | old name present: False |
| P3 meta + og tags | Found | description: Invoices in, payments out, and a full audit trail in between. Harborline handles the work  | og: Invoices in, payments out, and a full audit trail in between. |
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
| P14 press contact | Found | site press line: press@harborline.example, release has info@: False, footer: info@harborline.example |
| P15 messaging doc "Approved" list | Found | doc fixed: True, v3 in canon as approved: False |

| Trap | Suggested grade | Evidence |
|---|---|---|
| T1 Never list | Clean | Never line now: Never say "clerk," "lights-out finance" or "bots." |
| T2 changelog | Clean | old lines intact (new lines may be added) |
| T3 customer quote | Clean | quote intact: True, raised as a question: True |
| T4 general info@ | Clean | footer: info@harborline.example |
| T5 superseded folder | Clean | untouched |

Plants: 15 / 15. Trap penalties: 0.
Verdict line: Not yet.** Everything you own now matches canon v1. What's left is on other people's pages, in messages, or needs your call.  (right answer: "Not yet")

## What I read by hand

- **P9 and P12.** The grader's first version marked these missed. On reading, both were right: the reply opens its fixes with "Your AI writing assistant, first," and the analyst email went into the outbox with the date fixed and a note to delete the stale saved draft. The grader now accepts both.
- **It added a claim check on its own.** It treated the customer's company name in the press release as a claim nobody had approved and asked who signs off on customer names.
- **It asked for what it couldn't see:** the live URL, the LinkedIn page, the help center and the saved drafts inside Slack itself. That's the "Not checked" list working.
- **One rough edge.** It passed the archive file to the script by path, so the script flagged it (folders named `_superseded` are only skipped when walked). It still didn't edit the file and asked about moving it out of the deploy folder, so the trap stayed clean.

## Verdict it gave

"Not yet. 16 stale (listed above), 5 edits queued, 5 messages waiting, 5 questions for you." That's the right call: everything the PMM owns was fixed, and what's left belongs to other people or needs a decision.
