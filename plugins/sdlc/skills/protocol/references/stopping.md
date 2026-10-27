# Stopping

What every agent does when its conductor messages it to stop (`/sdlc:stop`,
`/sdlc:transfer`). A stopped job dispatches nothing.

1. **Pass it on:** a lead messages each of its workers by agent ID and waits for
   them to return `stopped` before stopping itself.
2. **Finish the step you're on,** and start nothing new: no new step, spawn, or
   review round. A review round already running finishes; record its findings
   for resume without adjudicating.
3. **Commit and push** work in progress to your own branch (`chore(wip): stop`
   with a `Refs #N` footer, or the repo's equivalent; a squash merge folds it
   away). In other repos the push needs approval: return it, and the conductor
   puts it to the human within the command they ran.
4. **Stop** your processes, containers, and browsers, marking them stopped in the
   ledger. Keep your worktree, branch, databases, slot, and ticket claim.
5. **Write a Resume from** section in your full report: what's done, the exact
   next step, and anything half-finished. Return the summary block with status
   `stopped`. The ticket's Project status doesn't change.

**Resuming an `interrupted` task** (cut off mid-step by `/sdlc:stop now`): first
review uncommitted changes against the last commit, keep what verifies, and note
what was discarded.
