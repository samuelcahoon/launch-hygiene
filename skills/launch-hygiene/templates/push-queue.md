# Push queue

Edits to pages someone else owns wait here. Nothing on those pages changes until you say "push" in chat. Before pushing, Claude reads each line again. If the owner changed it since it was queued, their edit wins and the row comes back to you.

## Queue

| # | Status | Queued by | Where (page and section) | Now | Becomes | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ready | Claude, [date] | [Page name, section] | [The exact current text] | [The exact new text] | [The decision, who and when] |
| 2 | Waiting on [name] | Claude, [date] | [Page name, section] | [Current text] | [Option A / Option B] | [What they need to decide] |

Statuses: Ready, Waiting on [name], Skip, Pushed.

## Done

Every change Claude makes, on your pages and theirs, so any of it can be undone.

| Date | Where | Was | Now |
| --- | --- | --- | --- |
| [Date] | [Page or file, section] | [Old text] | [New text] |
