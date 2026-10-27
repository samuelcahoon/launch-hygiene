# The eval

A skill you can't grade is a skill you can't improve. This folder tests launch-hygiene on a synthetic launch week with mistakes planted on purpose, then grades the run against an answer key the run never sees.

## What's in a launch week

`make_launch_week.py` builds one for a made-up company: a site (with meta tags and llms.txt), a messaging doc, a CEO's launch page, a brand guide, a press release draft, a sales deck owned by someone else, an AI writing prompt, Slack and email drafts, a sent email and an archive folder. Over five days, the tagline changed four times, the product was renamed, the launch date moved and press inquiries moved to a new address.

**15 planted mistakes,** including:

- Old lines in the meta description and Open Graph tags
- The approved line, almost: "Every action on record" instead of "Every action on the record"
- An old line typed with a straight apostrophe when the canon has a curly one
- The old tagline in lowercase on a sales slide someone else owns
- An AI writing prompt still telling the assistant to use the old line
- An email that already went out with the old date
- A CEO's newer edit that conflicts with the approved answer to a security question
- A messaging doc that still lists an old line under "Approved (current)"

**5 traps** a good run leaves alone or asks about: a Never list that names banned words, an old changelog, a customer quote that uses a banned word, a general contact address that's still right, and an archive folder.

Two companies so far: seed `1121` is Northlight AI (prior auth and denials) and seed `7788` is Harborline (accounts payable). Same plants, different words, so a skill can't pass by memorizing phrases.

## Results

| Run | Skill | Synthetic company | Plants found | Traps | Verdict |
| --- | --- | --- | --- | --- | --- |
| [1](results/2026-10-26_run1_northlight_v1.md) | v1 | Northlight AI | 14.5 of 15 | One slip: edited an old changelog line | Right ("Not yet") |
| [2](results/2026-10-26_run2_harborline_v2.md) | v2 | Harborline | 15 of 15 | Clean | Right ("Not yet") |
| [3](results/2026-10-26_run3_northlight_v2.1.md) | v2.1 (adds GitHub team mode) | Northlight AI | 15 of 15 | Clean | Right ("Not yet") |

Run 1's score needs an asterisk: four of its finds came from the session checking by hand after the script missed them. v2's script catches those itself. [Script-only numbers](results/script_benchmark.md): v1 flagged 24 of 29 planted stale phrases, v2 flags 29 of 29 with no false alarms, on both companies.

## Run it yourself

```
python3 eval/make_launch_week.py 7788 /tmp/eval-run      # builds the week and an answer key
mkdir -p ~/answer-keys && mv /tmp/eval-run/answer_key.md ~/answer-keys/7788.md
cp -r skills/launch-hygiene /tmp/eval-run/skill
```

Give a fresh Claude session the prompt in [RUN_PROMPT.md](RUN_PROMPT.md). When it's done:

```
python3 eval/grade.py 7788 /tmp/eval-run/launch-week
python3 eval/script_benchmark.py 7788 skills/launch-hygiene/drift_check.py
```

`grade.py` prints evidence and a suggested grade for every plant and trap. Read the run's reply before you log a grade: a run can say the right thing in different words.

## Limits

- Two synthetic companies and three runs. Model runs vary, so treat a single score as a sample, not a guarantee.
- I wrote the plants. The reviewers' own test files and the second company are the checks on that.
- Notion is a folder of markdown files here. The real skill reads Notion through the connector.
- The grader is text checks plus a human read, and the human is me. The evidence is in each results file so you can disagree with a grade.

## Files

| File | What it does |
| --- | --- |
| `make_launch_week.py` | Builds a launch week and its answer key |
| `grade.py` | Grades a finished run against the plants and traps |
| `script_benchmark.py` | Tests `drift_check.py` alone |
| `baseline/drift_check_v1.py` | The first version of the script, kept for comparison |
| `RUN_PROMPT.md` | The prompt for a blind run |
| `results/` | Every run, graded |
