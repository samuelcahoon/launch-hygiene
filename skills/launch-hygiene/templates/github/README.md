# Put the canon on GitHub

For a team, or a company that needs one answer to "what do we say?" One private repo holds the canon, the files it depends on and the AI instructions that write copy. Everyone's Claude reads from it. Every change is a pull request that the right person approves, and the drift check runs before anything merges.

## Starter layout

```
your-launch-canon/                 (private repo, in the company's GitHub account)
  canon.json                       approved lines, retired phrases, claims, surfaces, who decides
  drift_check.py                   copied from this skill
  knowledge/
    positioning.md                 what you do, who it's for, why it's different
    voice.md                       how you sound, the word list
    objections.md                  the questions buyers ask and your approved answers
  prompts/                         AI instructions and skills that write copy for the team
  copy/                            site copy, press, email and deck text, Notion pages saved as text
  .github/
    CODEOWNERS                     from CODEOWNERS in this folder
    workflows/drift-check.yml      from drift-check.yml in this folder
```

## Set it up (about 30 minutes)

1. Make a private repo in your company's GitHub account. Ask IT if you don't have one.
2. Copy `canon.json` (start from `canon.example.json`), `drift_check.py` and the two files in this folder into the paths above.
3. In `CODEOWNERS`, swap in the GitHub usernames of the people in your canon's `decides`.
4. Turn on branch protection for `main`: Settings, Branches, require a pull request, require review from code owners, require the "Drift check" status check.
5. Point everyone's AI tool at the repo. In Claude Code, clone it. In Claude, connect GitHub and add the repo to the project.

## How a change works

1. Someone decides the tagline changes. Claude updates `canon.json` on a new branch, fixes the copy and prompts it owns, and opens a pull request. The description says who decided, when and why.
2. GitHub asks the code owner to review. The drift check runs and shows its report on the pull request.
3. The owner approves and merges. Every teammate's AI tool now reads the new line.
4. Claude updates the Notion canon page, if you keep one, so people outside GitHub see the same thing.
5. Something wrong? Revert the pull request.

GitHub can't reach pages that live elsewhere (the founders' Notion page, the CMS, a deck). Those still go through the push queue.
