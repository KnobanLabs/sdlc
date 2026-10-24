# SDLC config

Copy to `~/.sdlc/config.md`. Read by every role; keep the `- name: value` lines
intact.

## Owned accounts and repositories

Repositories owned by these users and organizations, and the repositories
listed below, count as yours: writes there need no approval, except dangerous
operations and new dependencies and tools. Your own account is always included.
Enterprises can't be listed. Each entry needs its host (`github.com` or an
Enterprise Server host).

### Users
- (none)  <!-- my-second-account @ github.com -->

### Organizations
- (none)  <!-- my-org @ github.com -->

### Repositories
- (none)  <!-- some-org/shared-tooling @ github.com -->

## Jurisdictions
Where legal and compliance analysis applies (countries or states, such as
`US-ID, EU`). Unset means the legal tree raises it as a question first.
- jurisdictions: (none)

## Inbox threshold
Questions at or above this priority (`low`, `medium`, `high`, `critical`) wait in
the inbox for you; below it, conductors decide and report. Critical questions,
including every approval, always come to you.
- inbox_threshold: high

## Span of control
Tasks one conductor coordinates directly per run. Larger jobs split into
workstreams of at most this many tasks, each under a workstream lead.
- span: 8

## Concurrency
Agents at once across all layers, excluding expert-review's reviewers. Each
running agent holds one workspace slot, so this also sets the highest slot
number. Claude Code refuses subagents past `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`
(default 20) running at once, so keep agents × (1 + reviewers per round) within
it; conductors tell you when it, or `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, is too
low for a job.
- concurrency: 6

## Additional standing orders
- (none)
