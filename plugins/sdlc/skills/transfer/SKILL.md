---
name: transfer
description: Stop this session's SDLC jobs and hand them off, giving the human a prompt that picks the work back up in a new session. Human-invoked only.
disable-model-invocation: true
argument-hint: "[job-id | #ticket] [same-machine]"
---

# Transfer

Load `sdlc:protocol` and its `references/stopping.md`.

**Arguments** (any order, all optional):

| Argument | Effect |
|---|---|
| `<job-id>` | Transfer that job instead of all this session's jobs. |
| `#<ticket>` | Transfer only that ticket's task; this session keeps the rest. |
| `same-machine` | Minimal handoff that relies on this machine's local state. |

1. **Stop** the scope as `/sdlc:stop` does (branches are pushed, so another
   machine can continue).
2. **One ticket:** move its task into a new job (new job id and folder) with its
   ledger entries, slot, claim, report, and inbox questions, and mark it
   `transferred to <new job-id>` in the old job. The handoff names the new job.
3. **Mark** each transferred job `transferred` with the time in `job.md`. This
   session then leaves it alone unless the human resumes it here.
4. **Write the handoff** to `jobs/<job-id>/handoff.md` and show it in chat, ready
   to copy. With `same-machine`, only the first two lines below; otherwise all
   of it, standing alone, because local state may not exist where it's used:

   ```markdown
   Use the sdlc plugin in <owner/repo> (local clone: <path>) and run
   `/sdlc:resume <job-id>`. **Goal:** <one sentence>

   **Tasks:** <each: ticket, role, branch (pushed: yes | no), state, Resume from>
   **Waiting on you:** <open inbox questions, verbatim, most blocking first>
   **Decided on your behalf:** <unannounced decisions and why>
   **Local state:** `~/.sdlc/<owner>/<repo>/jobs/<job-id>/` on <machine>. If it
   isn't on this machine, rebuild the job folder from this prompt and the pushed
   branches, and claim new slots.
   ```
5. **Report** in one line where the handoff was saved.
