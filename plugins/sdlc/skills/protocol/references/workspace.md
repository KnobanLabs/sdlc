# Workspace and shared resources

All agents share one machine. Worktrees isolate tracked files only; everything
else is isolated by these rules.

## 1. Worktrees

- Every role that writes files works in its own worktree and branch (the
  technology agents that write files set `isolation: worktree`). Read-only work
  needs none.
- Worktrees branch from the default branch unless `worktree.baseRef` is `"head"`.
  To build on unmerged work, the brief names the base branch; check it out or
  rebase onto it in your worktree. With squash merges, wait for that work to
  merge and branch from the default branch instead: each squash re-conflicts
  the branches stacked on it.
- Untracked files the project needs (`.env`, local config) come from the repo's
  `.worktreeinclude` or as the profile describes. Never commit them.
- The conductor assigns file ownership so parallel tasks never edit the same
  files, and owns integration. Tasks that must share one (the profile's shared
  files) run in sequence, each branching once the one before it merges.

## 2. Slots

Slots are machine-wide, so sessions and repos running side by side never share
one. Only agents that run processes or bind ports get one. A conductor claims
each slot before assigning it: the lowest `<N>` for which
`mkdir -p ~/.sdlc/slots && mkdir ~/.sdlc/slots/<N>` succeeds, never a block or
a number picked for a workstream or ticket, with an `owner.md` naming the repo,
job, task, and time, ledgered as a `slot`. A failed `mkdir` means another job
holds it; try the next number. Slots stop at 286, below Linux, macOS, and
Windows ephemeral ports; past it, queue the task and tell the human which jobs
hold slots. The brief passes the slot on; a
workstream lead uses the slots its brief gives it. A slot whose `owner.md` names
a job folder that no longer exists is stale: report it; `/sdlc:clean` frees it
once the human confirms. Derive everything unique from the slot:

- **Ports:** `4000 + slot × 100` through `+ 99`, unless the profile defines
  another scheme. Higher slots can overlap common service ports (5432, 6379,
  8080), so confirm a port is free before binding, and point the app's config
  at it.
- **Databases:** suffix `_slot<N>`.
- **Containers and compose projects:** prefix `sdlc-<job-id>-s<N>`; use
  `docker compose -p`.
- **Temp files, sockets, browser profiles:** under `/tmp/sdlc/<job-id>/s<N>/`.

A slot stays with its task until the task is handed over (section 6). At job
start, the conductor reports slots held by other jobs alongside open jobs.

## 3. Shared state

- **Ticket claims:** `mkdir -p ~/.sdlc/<owner>/<repo>/claims && mkdir
  ~/.sdlc/<owner>/<repo>/claims/<N>`, with an `owner.md` naming the job, task,
  and time, ledgered as a `claim`. A failed `mkdir` means another job holds it.
  Release it when the task is done or released unfinished.
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

## 6. Cleanup

Automatic, never waiting on the human, and only for the task's ledger entries,
marking each removed.

- **Before handing over** (delivered or awaiting review), the worker stops its
  processes (checking each PID still runs the recorded command), freeing their
  ports; removes its containers, compose projects, databases, temp directories,
  browser profiles, and any other worktree it made (a screenshot base); and
  releases its leases.
- **When a worker hands over,** its conductor removes its worktree if nothing
  uncommitted remains, otherwise reports it; a role working alone removes its
  own. The slot goes back to whoever assigned it: a workstream lead reuses it,
  and the conductor that claimed it frees it (`~/.sdlc/slots/<N>/`) once none
  of its tasks will. A stopped or blocked worker keeps everything. A send-back
  gets a fresh worktree on the branch.
- **When the task is done,** the conductor deletes its local branch only with
  `git branch -d` (anything needing `-D`, or any remote branch, is an approval
  request) and releases its ticket claim (`~/.sdlc/<owner>/<repo>/claims/<N>/`).

Free a slot only after checking its `owner.md` names this job, and release a
claim only after checking it names the task's job and task. Leave resources shared with tasks still in flight, GitHub artifacts,
committed docs, and the durable local folders. Report what was left, and why.
