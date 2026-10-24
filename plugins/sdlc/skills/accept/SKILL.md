---
name: accept
description: Record the human's explicit acceptance of delivered SDLC tasks and clean up their workspaces. Human-invoked only.
disable-model-invocation: true
argument-hint: "<issue or PR numbers, or a job id>"
---

# Accept

The human is explicitly accepting delivered work, which unlocks cleanup. Load
`sdlc:protocol` first.

1. **Resolve** the arguments (issue or PR numbers, or a job id meaning all its
   delivered tasks) against `~/.sdlc/<owner>/<repo>/jobs/*/job.md`. Accept only
   tasks in the "delivered" state; if anything doesn't match as expected, list
   what you found and ask.
2. **Record** acceptance and the date in each task's `job.md`. Set each ticket's
   Project status to Done if it isn't already, and close tickets no merged PR
   closed (non-code work).
3. **ADRs:** if the task has ADRs marked "proposed", they move to "accepted"
   through the normal PR flow (review gate included). That's a repo change, so a
   technology conductor does it itself; any other conductor staffs the Architect
   for it.
4. **Clean up** each task from its ledger entries per the protocol's
   `workspace.md` (section 6), leaving anything shared with tasks in flight.
5. **Report** with the cleanup report template, raising any step needing approval
   (such as an unmerged or remote branch) as approval requests.

This command authorizes cleanup of the named tasks only, nothing else.
