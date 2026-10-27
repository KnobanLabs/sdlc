# Templates

Fill every section; write "none" rather than dropping one.

## Brief

A worker knows only its brief: give it your full understanding.

```markdown
# Brief: <task>
**Job:** <job-id>  **Role:** <role>  **Slot:** <N>  **From:** <role>

## Objective
What and why.

## Inputs
Issue owner/repo#N (with comments), its parent if it's a sub-issue, and its
Project (owner, number) and current status; design location; profile path;
standards path; relevant repo skills.

## Workspace
Base branch; branch to create; files you own (ask before editing others). For a
workstream lead: its tasks, agent budget (counting itself), and slot numbers.
For the single technology worker of a one-task job: whether it may merge its
own PR once checks pass and review converged.

## Constraints
Scope, prior decisions, the human's instructions.

## Definition of done
Checkable conditions, including `sdlc:expert-review` convergence.

## Escalate when
Situations that must come back up the chain.
```

## Worker report

Save the full report to `jobs/<job-id>/reports/<task>.md` and return only the
summary block, so your conductor's context holds one block per task.

```markdown
**<task>:** delivered | awaiting review | blocked | sent back | stopped. <one-line outcome>
PR or branch: <link> · Review: converged in <N> rounds | pending · Open questions: <N> (inbox Q<n>, ...) · Report: <path>
```

Full report:

```markdown
# Report: <task>
**Status:** delivered | awaiting review | blocked | sent back | stopped

## Summary
## Changes
Branch, PR, each file and why.
## Evidence
Commands and results, tests, screenshot file names.
## Review
`sdlc:expert-review` rounds, fixes, declined findings and why, or "pending".
## Acceptance criteria
Each with its evidence, or why not met.
## Created
Issues, PRs, ledger entries.
## Open questions
With full context, and what each blocks.
## Follow-ups
Out-of-scope findings (filed where appropriate).
## Resume from
If stopped: what's done, the exact next step, anything half-finished.
```

## Job file

`jobs/<job-id>/job.md`, kept current by the conductor.

```markdown
# Job: <job-id>
**Goal:** <one sentence>  **Status:** active | stopped | transferred | closed (<time>)
**Conductor:** <this session's role, and when it started or resumed the job>

| Task | Role | Agent ID | Slot | Branch | State |
|---|---|---|---|---|---|
```

## Fit-check message

Asked directly, right away (protocol sections 3 and 5).

```markdown
**Fit check:** <the mismatch, one sentence>. I'd recommend <entry point, and why>.
1. <recommended>  2. <alternative>  3. Proceed as asked
Which would you like?
```

## Approval request

A critical inbox entry, put to the human only during an inbox check.

```markdown
**Approval needed:** <what>
- **Command:** `<exact command>`
- **Repository:** owner/repo (human-owned | external)
- **Affects:** <what changes, who can see it>
- **Reversible:** yes, by <how> | no
- **Why:** <reason>
```

Bundled requests number each action for individual approval.

## Inbox

`jobs/<job-id>/inbox.md`, one entry per question, open or decided.

```markdown
## Q<n>: <title>
- **Priority:** low | medium | high | critical  **Raised by:** <role>  **Blocks:** <what waits>
- **Question:** ...  **Options:** ... (recommended marked)
- **Status:** open | answered: <answer> | decided by conductor: <answer and why> (<date>)
- **Announced:** yes | no
```

## Ledger

`jobs/<job-id>/ledger.md`, one row per resource, appended on creation.

```markdown
| Task | Owner | Type | Identifier | Created | Status |
|---|---|---|---|---|---|
| #1234 | engineer/s2 | process | pid 48211, `npm run dev`, port 4200 | 2026-10-05 14:10 | active |
```

Types: worktree, branch, process, container, compose, database, tempdir,
browser, lease, slot, claim, issue, pr, comment. Status: active, removed, record only.

## Job report

```markdown
# Job report: <job-id>
**Goal:** <one sentence>
## Delivered
Ticket, PR, merged or awaiting merge, review outcome.
## Awaiting your acceptance
Each task and what it still holds.
## Inbox
How many questions are waiting, each by title and what it blocks. Don't ask
them here; `/sdlc:inbox` does.
## Decided on your behalf
Each decision the conductor made, and why.
## Filed
New issues.
## Parked
What stopped, why, and where it stands.
## Next steps
```

## Cleanup report

```markdown
# Cleanup: <tasks>
## Removed
## Left in place
Each with the reason (shared, uncommitted, needs `-D`, remote, failed step).
## Needs your approval
As approval requests.
```
