---
name: clean
description: Sweep what stale SDLC jobs left on this machine (slots, claims, leases, worktrees, branches, processes, containers, temp files). Shows a deletion plan and removes nothing until the human confirms it. Human-invoked only.
disable-model-invocation: true
argument-hint: "[owner/repo]"
---

# Clean

Load `sdlc:protocol` and its `references/workspace.md`. Work alone: no workers
and no job folder. Inspect freely, but change nothing until the human confirms
the plan (step 3).

**Argument:** `<owner/repo>` limits the sweep to that repo and the slots naming
it. Without one, sweep every repo under `~/.sdlc/`.

## 1. Sort the jobs

For each folder in `~/.sdlc/<owner>/<repo>/jobs/`:

- **Live:** a file in it changed in the last 7 days. Leave it and everything it
  holds, whatever its `job.md` says.
- **Finished:** untouched for 7 days, its status isn't `stopped` or
  `transferred`, every ticket it claimed is closed, and every PR from its branches
  is merged or closed (check GitHub); and either its status is `closed` or it
  claimed tickets or opened PRs.
- **Unclear:** untouched for 7 days but not finished, such as a stopped job,
  one with work still open, or one with no tickets or PRs to judge by.

A job is **stale** when it's finished, or its folder no longer exists in any
repo.

## 2. Find what stale jobs left

Something is the org's when a ledger, an `owner.md`, or a lease names it, or it
follows the org's naming (`workspace.md`, section 2). Look for:

- **Ledger entries** of stale jobs not marked removed: processes, containers,
  compose projects and their volumes, databases, temp directories, browser
  profiles, worktrees, and local branches.
- **Slots, claims, and leases** (`~/.sdlc/slots/<N>/`, `claims/<N>/`,
  `leases/*.md`) whose `owner.md` or holder names a stale job. Flag any live
  slot above 286 as well: its ports run past the valid range.
- **Temp files** in `/tmp/sdlc/`: folders and loose files named for a stale job
  by its id, or by the id's last four hex digits when no other job in any repo
  ends in them and nothing in the match changed in 7 days.
- **Containers and volumes** named `sdlc-<job-id>-…` for a stale job.
- **Worktrees** under the repo's `.claude/worktrees/` that no ledger names, with
  nothing uncommitted or unpushed, a merged or closed PR, and nothing changed in
  7 days. They may be the human's own `claude --worktree` sessions, so they go
  under Ask, never Remove; removing one also deletes its ignored files.

Keep what you can't tie to a stale job or don't recognize. Never delete or move
job folders, the durable folders, `profile.md`, `exploration-log.md`,
`settings.json`, or GitHub issues, PRs, and comments.

## 3. Confirm the plan

Show the plan, then ask once with AskUserQuestion: run it all, run it without
the approvals, or cancel. The human answers Ask items, or edits the plan, in the
same reply; run the plan as answered.

- **Remove:** per category, each item with its job, plus the space freed.
- **Needs approval:** local branches `git branch -d` refuses (with their PR and
  whether it merged), and remote branches whose PR merged or closed.
- **Ask:** each unclear job, with its status, what is still open, and what it
  holds; and the worktrees no ledger names. They stay unless the human says
  otherwise.
- **Kept:** live jobs' resources in brief, worktrees with uncommitted or
  unpushed work, and what you didn't recognize, each with why.

## 4. Act

Re-check each item just before removing it, since another session may be
working: its job still untouched for 7 days, its `owner.md` still naming the
same job, a process's PID still running the recorded command (on its recorded
port, if any), and no live or unclear job now holding the slot a database or
port is named for. Remove in this order: processes; containers, compose
projects, volumes, and databases; temp directories and browser profiles;
worktrees (`git worktree remove` without `--force`, then `git worktree prune`);
branches (`-d`, and `-D` or remote only as approved); leases; claims; slots.
Leave anything that fails or has changed, and report it.

After all removals, in each job whose resources you removed, mark those ledger
rows `removed <UTC>`. Set `job.md`'s status to `closed (<time>)` only for a
finished job that now holds nothing.

## 5. Report

A few lines: what was removed per category, the space freed, and what was kept
and why.
