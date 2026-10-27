---
name: stop
description: Stop this session's SDLC jobs. Every agent reaches a safe stopping point, saves where it left off, and halts. Human-invoked only.
disable-model-invocation: true
argument-hint: "[job-id | #ticket] [now]"
---

# Stop

Load `sdlc:protocol` and its `references/stopping.md`.

**Arguments** (any order, all optional):

| Argument | Effect |
|---|---|
| `<job-id>` | Stop that job instead of all this session's jobs. |
| `#<ticket>` | Stop only that ticket's task; the rest of its job keeps running. |
| `now` | Stop immediately instead of at a safe stop (step 3). |

1. **Scope:** this session's jobs, or the job or ticket named.
2. **Stop dispatching.** Set each job's status in `job.md` to `stopped` with the
   time (for one ticket, only that task's state), and start no new task, spawn,
   or merge in scope.
3. **Message every running agent** in scope with `SendMessage` to the agent ID
   in `job.md`, to stop per `stopping.md`; a running agent takes it as task
   direction. With `now`: message each lead to `TaskStop` its workers and return
   at once, `TaskStop` every agent you dispatched that's still running, stop
   their processes from the ledger (verifying each PID still runs the recorded
   command), and mark their tasks `interrupted`: their worktrees may hold
   uncommitted, unverified changes.
4. **Wait** for each to return `stopped`, and record each task's state in
   `job.md`. Without `now`, an agent that doesn't respond keeps running until it
   finishes; report it rather than killing it.
5. **Report** in a few lines: what stopped where, anything still running, and
   how many inbox questions wait. `/sdlc:resume` continues.
