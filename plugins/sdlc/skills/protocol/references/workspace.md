# Workspace and shared resources

All agents share one machine. Worktrees isolate tracked files only; everything
else is isolated by these rules.

## 1. Worktrees

- Every role that writes files works in its own worktree and branch (the
  technology agents that write files set `isolation: worktree`). Read-only work
  needs none.
- Worktrees branch from the default branch unless `worktree.baseRef` is `"head"`.
  To build on unmerged work, the brief names the base branch; check it out or
  rebase onto it in your worktree.
- Untracked files the project needs (`.env`, local config) come from the repo's
  `.worktreeinclude` or as the profile describes. Never commit them.
- The conductor assigns file ownership so parallel tasks never edit the same
  files, and owns integration.

## 2. Slots

Slots are machine-wide, so sessions and repos running side by side never share
one. A conductor claims each slot before assigning it: the lowest `<N>` for
which `mkdir -p ~/.sdlc/slots && mkdir ~/.sdlc/slots/<N>` succeeds, with an
`owner.md` naming the repo, job, task, and time, ledgered as a `slot`. A failed
`mkdir` means another job holds it; try the next number. The brief passes the
slot on; a workstream lead uses the slots its brief gives it. Reviewers need no
slot. A slot whose `owner.md` names a job folder that no longer exists is stale:
report it, and free it only with the human's approval. Derive everything unique
from the slot:

- **Ports:** `4000 + slot × 100` through `+ 99`, unless the profile defines
  another scheme. Higher slots can overlap common service ports (5432, 6379,
  8080), so confirm a port is free before binding, and point the app's config
  at it.
- **Databases:** suffix `_slot<N>`.
- **Containers and compose projects:** prefix `sdlc-<job-id>-s<N>`; use
  `docker compose -p`.
- **Temp files, sockets, browser profiles:** under `/tmp/sdlc/<job-id>/s<N>/`.

A slot stays with its task until the task is accepted and cleaned up. At job
start, the conductor reports slots held by other jobs alongside open jobs.

## 3. Shared state

- **Ticket claims:** `mkdir -p ~/.sdlc/<owner>/<repo>/claims && mkdir
  ~/.sdlc/<owner>/<repo>/claims/<N>`, with an `owner.md` naming the job, task,
  and time, ledgered as a `claim`. A failed `mkdir` means another job holds it.
  Release it when the task is cleaned up or released unfinished.
- Never install packages globally; avoid concurrent installs writing the same
  lockfile.
- The git stash, branch namespace, config, and hooks are shared (`approvals.md`,
  section 3).
- Workers push only their own branches. Only the integrating technology role
  (or a CTO workstream lead, within its workstream) merges or marks PRs ready; only the Release Engineer tags or releases (with
  approval).
- Stagger heavy work (full test suites, browsers, video renders) so the machine
  isn't starved.
- **Leases:** claim an unsplittable resource (a shared test environment, a single
  browser the tooling can drive) with `~/.sdlc/<owner>/<repo>/leases/<resource>.md`
  naming holder, job, and time. Release it when done; never take one held by
  someone else.

## 4. Browsers

Each agent uses its own browser instance and profile (`/tmp/sdlc/<job-id>/s<N>/browser/`)
against the dev server on its own slot's ports, or a lease if only one browser is
drivable.

## 5. Ledger

`jobs/<job-id>/ledger.md` (format in `templates.md`). **Record every resource the
moment you create it:** worktrees, branches, processes (PID, port), containers,
databases, temp directories, browser profiles, leases, slots, ticket claims,
and GitHub artifacts (for traceability only). Mark entries removed if you remove your own scratch resources
mid-task. Cleanup touches only what the ledger lists.

## 6. Cleanup after acceptance

Only after the human accepts a task, done by the conductor present then (usually
via `/sdlc:accept`), for that task's ledger entries:

1. Stop its processes (verify each PID still runs the recorded command).
2. Remove its containers, compose projects, databases, temp directories, and
   browser profiles; release its leases.
3. Remove its worktrees only if nothing uncommitted remains; otherwise report.
4. Delete its local branches only with `git branch -d`; anything needing `-D`, or
   any remote branch, needs approval.
5. Free its slot and release its ticket claims: remove `~/.sdlc/slots/<N>/` and
   `~/.sdlc/<owner>/<repo>/claims/<N>/`, each after checking its `owner.md`
   names this job and task.

Leave resources shared with tasks still in flight, GitHub artifacts, committed
docs, and the durable local folders. Finish with the cleanup report.
