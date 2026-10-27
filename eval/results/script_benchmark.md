# The script on its own

`script_benchmark.py` builds each launch week, writes the canon a PMM would write from the brief, runs one version of `drift_check.py` and counts which planted stale phrases it flags. No judgment, just the script. Sent mail and archive folders aren't scanned.

```
baseline/drift_check_v1.py (v1) on seed 1121 (Northlight AI): flagged 24 of 29 planted stale phrases. False alarms on traps: 1.
  missed: site/index.html: h1 and og:description (1 of 2)
  missed: site/index.html: meta description (0 of 1)
  missed: site/llms.txt: line with a straight apostrophe (0 of 1)
  missed: press/press-release.md: near-miss of the approved line (0 of 1)
  missed: sales/deck-outline.md: lowercase product name (0 of 1)
  false alarm: notion/messaging-doc.md: tried
baseline/drift_check_v1.py (v1) on seed 7788 (Harborline): flagged 24 of 29 planted stale phrases. False alarms on traps: 1.
  missed: site/index.html: h1 and og:description (1 of 2)
  missed: site/index.html: meta description (0 of 1)
  missed: site/llms.txt: line with a straight apostrophe (0 of 1)
  missed: press/press-release.md: near-miss of the approved line (0 of 1)
  missed: sales/deck-outline.md: lowercase product name (0 of 1)
  false alarm: notion/messaging-doc.md: tried
skills/launch-hygiene/drift_check.py (v2) on seed 1121 (Northlight AI): flagged 29 of 29 planted stale phrases. False alarms on traps: 0.
skills/launch-hygiene/drift_check.py (v2) on seed 7788 (Harborline): flagged 29 of 29 planted stale phrases. False alarms on traps: 0.
```

A caveat: I wrote v2 after seeing what v1 missed, so these script numbers are the weakest evidence here. The stronger tests are the blind run on a second company (run 2) and the reviewers' own test files, which they built without seeing my plants. On one reviewer's test page (meta tags, JSON-LD, a phrase split by `<em>`, `&nbsp;`, a double space, a curly apostrophe, a single-quoted alt attribute and a line starting with "Never"), v1 flagged 1 stale line and v2 flagged 15.
