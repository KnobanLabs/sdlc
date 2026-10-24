# sdlc

A Claude Code plugin that runs software and marketing work on any GitHub
repository through an org of agent roles. You set the agenda; a conductor staffs
the smallest team that can do the job.

## Quick start

1. Install the plugin from the KnobanLabs marketplace, in a Claude Code session:

   ```
   /plugin marketplace add KnobanLabs/sdlc
   /plugin install sdlc@KnobanLabs
   ```

2. Copy `config.example.md` to `~/.sdlc/config.md` and list the users,
   organizations, and repositories that count as yours.
3. Turn off Claude Code's own attribution in `~/.claude/settings.json`:

   ```json
   { "attribution": { "commit": "", "pr": "" } }
   ```

4. Have `gh` 2.99+ authenticated, with the `project` scope if you use GitHub
   Projects (`gh auth refresh -s project`), and (for UI work) a browser MCP such
   as Chrome DevTools configured.
5. Keep Claude Code's subagent nesting on (the default). Workers spawn their own
   reviewers, which needs `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` of at least 2;
   workstream leads need 3 (the default). Conductors check this and
   `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` at job start and tell you if either is
   too low.
6. Ask for work: "Engineer, fix #57", "QA, find bugs", "CEO, work tickets #12
   to #18 and QA the app". A role invoked without a task asks what to work on.

## The org

| Tree | Roles (skill) |
|---|---|
| Leadership | CEO (`ceo`) |
| Technology, under the CTO (`cto`) | Architect, Engineer, QA, Security, Release (`architect`, `engineer`, `qa`, `security`, `release`) |
| Marketing, under the CMO (`cmo`) | Brand Designer, Content Writer, Community (`brand-designer`, `writer`, `community`) |
| Legal, under the Chief Legal Officer (`clo`) | Compliance Officer, Privacy Counsel, IP Counsel (`compliance`, `privacy`, `ip`) |
| Product, under the Chief Product Officer (`cpo`) | PM, Data Analyst, Product Designer (`pm`, `analyst`, `product-designer`) |

Skills are invoked as `/sdlc:<skill>`. Any role invoked directly runs its own job.
`/sdlc:accept <tasks>` records your acceptance and cleans up; `/sdlc:inbox`
answers waiting questions; `/sdlc:expert-review` reviews any change.
`/sdlc:pause` brings every agent to a safe stop (finishing its current step,
committing and pushing work in progress, stopping its processes);
`/sdlc:resume` continues from there, in this session or a new one; and
`/sdlc:transfer` pauses and gives you a prompt that picks the work up in a new
session.

## What to expect

- **Inbox:** questions wait in an inbox instead of interrupting you, one per
  job; `/sdlc:inbox` asks only the current session's questions, so two sessions
  running side by side never mix them. A
  conductor asks you directly only what to work on (when you give it no task)
  and fit checks (when you've picked the wrong entry point). Run
  `/sdlc:inbox` (or say "ask your questions now") to hear the decisions made on
  your behalf and answer what's waiting. Questions below your threshold
  (`/sdlc:inbox medium`, a "threshold: medium" in your request, or
  `- inbox_threshold:` in config; default `high`) are decided by the conductor.
  Critical questions, including every approval, always wait for you rather than
  being decided. Work that depends on an answer waits;
  everything else continues. When nothing else can proceed, the conductor stops
  and tells you how many questions are waiting.
- **Approvals:** in your repos, agents act within their roles; dangerous,
  destructive, or irreversible operations, new dependencies and tools, and any
  write elsewhere, wait for you.
- **Tickets:** whichever role picks up a ticket assigns it to you and keeps its
  status current (Todo, In Progress, In Review, Done), whether or not the work
  touches code. Work needing several roles is split into sub-issues, one per role.
  When the repo has a related GitHub Project, every ticket the org files or
  triages goes into it with every field populated.
- **Acceptance:** nothing is cleaned up until you accept it ("accept #57").
  Merges may happen earlier when checks and review pass.
- **Only the technology tree commits.** Other roles keep work in
  `~/.sdlc/<owner>/<repo>/` and hand repo changes over.
- **Legal and compliance** work is informational analysis, not legal advice.
  It names its jurisdictions (`- jurisdictions:` in config), cites dated
  sources, keeps exposure private, says when you need a licensed attorney, and
  can block a delivery on a high-risk finding until you fix it or accept the
  risk. License audits belong to IP Counsel, not Security.
- **No attribution:** agents write as you, and never post to social platforms
  (they draft; you post).
- **Every repo change** passes `sdlc:expert-review`; UI PRs include before and
  after screenshots unless the repo's guidance says otherwise.
- **Model and effort** follow your session, except expert-review's reviewers,
  which the read-only `expert-reviewer` agent pins to Opus 5.5 at High. Don't add
  `effort` to the other agent files.
- **Concurrency:** 6 agents at once by default (`- concurrency:` in config),
  each running its own review rounds, to stay under Claude Code's default limit
  of 20 running subagents.
- **Large jobs:** a conductor coordinates at most 8 tasks per run directly
  (`- span:` in config). Beyond that, the work splits into workstreams, each run
  by a workstream lead (a CTO or CMO in lead mode) that staffs, integrates, and,
  for technical work, merges its slice. The top conductor dispatches every lead
  and keeps cross-workstream integration. Workers return a short summary and
  save full reports to the job folder, keeping each conductor's context small.

## Layout

| Path | Contents |
|---|---|
| `skills/protocol/` | The shared protocol every role loads, plus references (conducting, workstreams, pausing, approvals, workspace, GitHub, screenshots, repo profile, legal, design, templates) |
| `skills/<role>/` | Nineteen role skills, plus `accept`, `inbox`, `pause`, `resume`, `transfer`, and `expert-review` |
| `agents/` | Worker definitions for every role except the CEO, plus the read-only `expert-reviewer` |
| `tests/check_rules.py` | Verifies every recorded decision is still stated and removed features stay removed. It also enforces token budgets on the files agents load most. Run `python3 tests/check_rules.py` after any edit (needs PyYAML); update its entry when a decision changes, and raise a budget only on purpose |

Local state lives in `~/.sdlc/`: config, and per-repo profiles and jobs.

## Known gaps

- With nesting off, or an older Claude Code that lacks it, workers can't spawn
  reviewers; conductors then run the rounds and route fixes to a technology
  worker.
- Approval rules are enforced by instructions, not hooks. Plugin agents can't
  limit Bash to specific commands, so the reviewers' read-only Bash use is an
  instruction too (they have no edit or spawn tools, but can read GitHub and
  the web to verify behavior).
- Agent teams are optional and experimental; everything works without them.
