# sdlc

A Claude Code plugin that runs software and marketing work on any GitHub
repository through an org of agent roles. You set the agenda; a conductor staffs
the smallest team that can do the job.

Under a CEO, four trees cover the lifecycle: technology (CTO, Architect,
Engineer, QA, Security, Release), marketing (CMO, Brand Designer, Content
Writer, Community), legal (Chief Legal Officer, Compliance, Privacy, IP), and
product (CPO, PM, Data Analyst, Product Designer). Every repo change passes a
multi-round expert review, and questions wait in an inbox instead of
interrupting you.

This repository is also the `KnobanLabs` Claude Code plugin marketplace.

## Install

In a Claude Code session:

```
/plugin marketplace add KnobanLabs/sdlc
/plugin install sdlc@KnobanLabs
```

Or from your shell:

```bash
claude plugin marketplace add KnobanLabs/sdlc
claude plugin install sdlc@KnobanLabs
```

Then finish setup with the [Quick start](plugins/sdlc/README.md#quick-start)
(your config file and attribution settings) and ask for work, such as
"Engineer, fix #57" or "CEO, work tickets #12 to #18 and QA the app". Skills
are invoked as `/sdlc:<skill>`.

## Update

Auto-update is off by default for third-party marketplaces. Either:

- run `/plugin marketplace update KnobanLabs` in a session (or
  `claude plugin update sdlc@KnobanLabs` in your shell), or
- turn on auto-update: open `/plugin`, go to **Marketplaces**, select
  `KnobanLabs`, and select **Enable auto-update**.

A new release reaches you when its version changes.

## Requirements

- Claude Code with subagent nesting on (the default):
  `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` of at least 2, and 3 (the default) for
  workstream leads
- `git`, to add the marketplace
- [`gh`](https://cli.github.com) 2.99+ authenticated, with the `project` scope
  if you use GitHub Projects (`gh auth refresh -s project`)
- For UI work, a browser MCP such as Chrome DevTools

## Documentation

The plugin's [README](plugins/sdlc/README.md) covers the org, what to expect,
the layout, and known gaps. [CHANGELOG.md](CHANGELOG.md) lists each release.

| Path | Contents |
|---|---|
| `.claude-plugin/marketplace.json` | The `KnobanLabs` marketplace catalog |
| `plugins/sdlc/` | The `sdlc` plugin |
| `.github/` | CI, issue forms, the PR template, labels |
| `AGENTS.md` | Instructions for coding agents working on this repository |

## Contributing

Bug reports, feature requests and pull requests are welcome. See
[CONTRIBUTING.md](CONTRIBUTING.md) for setup, the checks CI runs, and the
branch, commit and pull request conventions, and [AGENTS.md](AGENTS.md) for the
instructions coding agents follow. Releases come from release-please: a merged
release PR moves the plugin's version, which is what sends the update to users.

## Security

Report vulnerabilities privately, as [SECURITY.md](SECURITY.md) describes.

## License

MIT. Copyright © 2026 Knoban LLC. See [LICENSE](LICENSE).
