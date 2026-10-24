---
name: inbox
description: Check the SDLC inbox. Announces decisions conductors made on the human's behalf, then asks the human every open question. Human-invoked only.
disable-model-invocation: true
argument-hint: "[job-id] [threshold: low | medium | high | critical]"
---

# Inbox

Load `sdlc:protocol` and check the inbox per its `references/conducting.md`
(this session's jobs, or the job named).

- A threshold in the arguments applies to these jobs' unanswered questions.
- Approval requests are answered "approve" or "deny" per action.
- For a named job another session still runs, only record the answers; that
  session picks them up.
- If nothing is waiting, say so in one line.
