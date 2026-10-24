# Workstream leads

When a tree's part of a job has more tasks than the span, split it into
workstreams of at most the span each, grouped by area and dependency so their
files don't overlap, and dispatch one workstream lead per workstream (the tree's
lead agent: `cto`, `cmo`, `clo`, or `cpo`). The top conductor dispatches
every lead itself:

- **A tree lead on top:** plan the split and dispatch the leads.
- **CEO on top:** staff the tree's lead as a worker to plan the split, dispatch
  the leads yourself, then staff the lead again as a worker to integrate across
  workstreams and sign off.

Each lead's brief gives its workstream (tasks, scope, file ownership), the job id,
its agent budget (counting itself), and its slot numbers. A single workstream may
hold a whole tree's part when it fits the span.

A lead follows `conducting.md`, except:

- It has a task already: no asking what to work on, no new job folder. It uses
  the top conductor's `job.md`, `ledger.md`, `inbox.md`, and `reports/`.
- It staffs only within its budget and slots, any role its workstream needs; its
  workers never lead.
- A CTO lead merges its workstream's PRs once checks pass and review converged;
  other leads hand repo changes over as usual. No lead changes anything outside
  its workstream. Cross-workstream integration (merge order, conflicts in shared
  files) and default-branch CI stay with the top CTO, or the CTO staffed to
  integrate.
- It never asks the human directly. It decides below-threshold questions and logs
  them as usual; questions at or above the threshold, and every approval, it
  records open in the inbox and returns in its summary, continuing unblocked work.
- It saves a report covering its workstream (the job-report sections) to
  `reports/` and returns the summary block.

Depth: top conductor → lead → worker → reviewers is three layers, the default
limit, so leads never dispatch leads and their workers never lead. Rework after
a lead has returned goes to a fresh lead briefed from job state on
disk. A lead without the Agent tool returns a staffed plan for the top conductor
to run instead.
