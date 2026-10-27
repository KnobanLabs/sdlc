---
name: resume
description: Resume stopped or transferred SDLC jobs from where their agents left off, in this session or a new one. Human-invoked only.
disable-model-invocation: true
argument-hint: "[job-id | #ticket] [fresh]"
---

# Resume

Load `sdlc:protocol`, its `references/conducting.md`, and its
`references/stopping.md`.

**Arguments** (any order, all optional):

| Argument | Effect |
|---|---|
| `<job-id>` | Resume that job instead of all this session's stopped jobs. |
| `#<ticket>` | Resume only that ticket's task; the rest stays stopped. |
| `fresh` | Start fresh workers from their **Resume from** notes instead of reconnecting to the old agents. |

1. **Scope:** the job or ticket named, else this session's stopped jobs. Naming
   a job another session stopped or transferred adopts it into this session. If
   its `job.md` still shows it active under another session, ask the human
   before adopting it: that session may still be running.
2. **Re-read** `job.md`, the ledger, the inbox, and each stopped task's report.
   Re-run the conductor's start checks that may have changed: repo profile,
   open jobs, slots, and Claude Code limits.
3. **Set status** to `active` with the time, and record this session as the
   job's conductor.
4. **Resume each task,** within Claude Code's limits: `SendMessage` to an agent
   this session dispatched (it keeps its context); otherwise, or with `fresh`, a
   fresh worker with the original brief plus its report's **Resume from**, on
   the same slot, worktree, and branch. An `interrupted` task reconciles first
   (`stopping.md`). Restart what each task needs. Tasks blocked on unanswered
   questions stay stopped until answered.
5. **Report** what resumed, what still waits, and on what.
