# The prompt for a blind run

Build a week, copy the skill next to it, and give a fresh Claude session this prompt. Keep the answer key somewhere the session can't read.

```
python3 eval/make_launch_week.py 7788 /tmp/eval-run
mkdir -p ~/answer-keys && mv /tmp/eval-run/answer_key.md ~/answer-keys/7788.md
cp -r skills/launch-hygiene /tmp/eval-run/skill
```

Then, in a new session:

> You are acting as Claude with a newly installed skill, doing a real task for a PMM. Work only inside this folder and never read anything outside it: RUN=/tmp/eval-run
>
> 1. Read $RUN/skill/SKILL.md first and follow it exactly. The other files in $RUN/skill/ are the skill's own files.
> 2. The user's request is $RUN/launch-week/brief.md. Treat it as the user's message to you and do what it asks, following the skill.
>
> Sandbox notes:
> - There is no Notion connector here. The folder $RUN/launch-week/notion/ stands in for Notion: each .md file is a Notion page, and the owner is listed at the top. When the skill says to create a Notion page, create it as a markdown file in that folder.
> - Nothing can be sent. Slack, email and messages are files.
> - The user is away and can't answer. Where the skill says to ask the user or get a yes, treat the brief as the user's yes for fixing what they own, put every other question in your final reply, and carry on.
> - Put canon.json and any reports inside $RUN/launch-week/.
>
> When you're done, write your final reply to the user (exactly what you'd say to them, verdict included) to $RUN/launch-week/REPLY.md.

Then grade it:

```
python3 eval/grade.py 7788 /tmp/eval-run/launch-week
```

The grader prints evidence and a suggested grade for each plant and trap. Read the run's REPLY.md before you log a grade: a run can say the right thing in different words.
