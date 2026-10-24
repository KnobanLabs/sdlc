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

If you switch Claude accounts during a session, see
[Install without claude.ai sync](#install-without-claudeai-sync).

## Update

Auto-update is off by default for third-party marketplaces. Either:

- run `/plugin marketplace update KnobanLabs` in a session (or
  `claude plugin update sdlc@KnobanLabs` in your shell), or
- turn on auto-update: open `/plugin`, go to **Marketplaces**, select
  `KnobanLabs`, and select **Enable auto-update**.

A new release reaches you when its version changes.

## Install without claude.ai sync

When your organization turns sdlc on for its members on claude.ai, Claude Code
downloads a copy for each account into
`~/.claude/plugins/synced/<org>_<account>/`. If you switch accounts during a
session, for example with [claude-swap](https://github.com/realiti4/claude-swap),
Claude Code removes the sdlc skills ("its plugin was synced for another
account"), even when every account is in the same organization.

The workaround below installs sdlc from this marketplace instead and turns the
sync off. It isn't an Anthropic feature, and it has been tested only on macOS
with Claude Code 2.1.308.

1. Install sdlc at user scope, which isn't tied to an account:

   ```bash
   claude plugin marketplace add KnobanLabs/sdlc --scope user
   claude plugin install sdlc@KnobanLabs --scope user
   ```

2. Turn off claude.ai plugin sync for Claude Code. Back up
   `~/.claude/settings.json`, then add this key to it, keeping every other key:

   ```json
   "syncClaudeAiPlugins": false
   ```

   Only `false` has an effect. Claude Code stops downloading claude.ai
   plugins, and on its next launch moves `~/.claude/plugins/synced` to
   `~/.claude/plugins/.trash`.

3. Check the install: `claude plugin list` shows `sdlc@KnobanLabs` enabled,
   and `claude plugin details sdlc@KnobanLabs` lists 26 skills and 19 agents.
4. Start a new session, switch accounts (`cswap switch` with claude-swap), and
   check that the `sdlc:` skills are still there.

Keep in mind:

- **Every claude.ai plugin stops syncing** to Claude Code, not only sdlc.
  Install any other organization plugin you need from its marketplace.
- **The Claude desktop app** still shows your organization's sdlc as enabled on
  its plugin screen. That's your claude.ai account setting, and it's expected.
- **Your organization's updates no longer arrive.** Update as in
  [Update](#update), with `claude plugin marketplace update KnobanLabs`. The
  marketplace follows the default branch, `develop`; to follow a release tag
  instead, add it as `KnobanLabs/sdlc#v0.24.3`.
- **Without network or GitHub access**, copy this repository to the machine
  (a clone or a downloaded archive) and run
  `claude plugin marketplace add /path/to/sdlc --scope user`. The repository
  root is the marketplace.
- **If `claude` isn't on your PATH** on macOS, the Claude desktop app bundles
  one at
  `~/Library/Application Support/Claude/claude-code/<version>/*/claude.app/Contents/MacOS/claude`.
  Use the newest version.
- **To undo it**, remove `syncClaudeAiPlugins` from `settings.json`, then run
  `claude plugin uninstall sdlc@KnobanLabs` and
  `claude plugin marketplace remove KnobanLabs`.

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
