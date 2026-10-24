# Contributing to sdlc

sdlc is open source under the [MIT License](LICENSE), and contributions are
welcome: bug reports, feature requests and pull requests. By contributing, you
agree that your contribution is licensed under the same license.

> **Note for coding agents:** [`AGENTS.md`](AGENTS.md) is the canonical
> instruction set. This guide is the human-facing summary and defers to it for
> conventions.

## Prerequisites

- Git 2.36 or newer
- Python 3 with [PyYAML](https://pypi.org/project/PyYAML/), for the plugin's
  rule checks
- [Claude Code](https://code.claude.com/docs), to validate and try the plugin
- Docker, for the pre-commit secret scan
- The [GitHub CLI](https://cli.github.com/) (`gh`), signed in, for the commands
  below

## Development Setup

1. Fork the repository, or, as a maintainer, clone it directly:

   ```bash
   gh repo fork KnobanLabs/sdlc --clone   # or: gh repo clone KnobanLabs/sdlc
   cd sdlc
   python3 -m pip install pyyaml
   scripts/install-hooks.sh
   ```

2. Run the checks CI runs:

   ```bash
   python3 plugins/sdlc/tests/check_rules.py plugins/sdlc
   claude plugin validate ./plugins/sdlc --strict
   claude plugin validate . --strict
   ```

3. Try your change in a session with the working copy loaded:

   ```bash
   claude --plugin-dir ./plugins/sdlc
   ```

   A plugin loaded this way takes the place of an installed `sdlc` for that
   session, so you don't need to uninstall yours. Run `/reload-plugins` after an
   edit to pick it up without restarting.

### Changing the plugin

- `plugins/sdlc/tests/check_rules.py` records the plugin's decisions, the
  features that were removed, its structure, and token budgets on the files
  agents load most. When your change alters a recorded decision, update its
  entry in the same pull request. Raise a budget only on purpose, and say why.
- Don't change `version` in `plugin.json`: the release PR does (see
  _Releasing_).
- The plugin's README, `plugins/sdlc/README.md`, describes its org, layout and
  known gaps; keep it in step with what you change.

### Secret scan before each commit

The pre-commit hook scans what a commit stages for secrets with the same Trivy
image and config (`.github/trivy-secret.yaml`) as CI's _Scan for secrets_ step,
so a secret is stopped before it is committed rather than after it is pushed.
Turn it on once per clone:

```bash
scripts/install-hooks.sh
```

It points `core.hooksPath` at `.githooks/`. The scan copies the staged version
of each added or changed file to a temporary folder inside `.git`, which it
always removes, and runs Trivy over it with no network and the folder
read-only. It fails when Docker isn't running, rather than letting the commit
through unscanned. `SKIP_SECRET_SCAN=1 git commit …` or `git commit --no-verify`
skips it, and CI still scans the push. `pre-merge-commit` runs the same scan on
the merges git commits itself.

To scan the whole tree as CI does:

```bash
docker run --rm --network none -v "$PWD:/repo:ro" \
  ghcr.io/aquasecurity/trivy:0.75.0@sha256:af6acf9a6b85dfe389a1941505c0ce9efef52a4719635e1a962f022a3d855daa \
  fs --scanners secret --skip-version-check --exit-code 1 \
  --secret-config /repo/.github/trivy-secret.yaml /repo
```

## Branch Naming

Branches should follow this pattern:

```
<handle>/<issue#>-<type>-<short-description>
```

Examples: `kNoAPP/41-feat-export-csv`, `mario/none-chore-tidy-gitignore`

If there's no linked issue, specify `none`. Types: `feat`, `fix`, `docs`,
`refactor`, `test`, `ci`, `chore`

## Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

Examples:

- `feat(qa): check dark mode in the viewport sweep`
- `fix(protocol): stop the inbox repeating answered questions`
- `docs: update the requirements in README`

PR titles must also follow this format — CI will reject non-conforming titles.
A pull request squashes to one commit whose message is its title, and
release-please builds the changelog and the next version from those titles:
`feat` bumps the minor version, `fix` the patch, and a `!` after the type (or a
`BREAKING CHANGE:` footer) the major.

## Pull Request Process

`develop` is protected: every change lands through a pull request, and nothing
is ever committed or pushed to `develop` directly.

1. Create your branch from `develop` (the default branch), in your fork or, as
   a maintainer, in this repository
2. Make your changes with every check passing
3. Fill out the PR template completely — replace each `None` placeholder if
   applicable and leave the guidance comments in place
4. Open the PR against `develop`; the code owners are requested automatically
   via CODEOWNERS
5. Get CI green and resolve every review thread; `develop` accepts a merge only
   then. A first-time contributor's workflows wait for a maintainer to approve
   them before they run
6. A maintainer merges it through the merge queue (see _Merging_ below)

`~PR Preparation` lints the title and labels the pull request by the paths it
changes (`.github/labeler.yaml`). The labels it sets are kept in sync with the
diff, so don't add an area label by hand that the paths don't explain.

When a CI job fails for a reason your change can't explain, rerun only the
failed jobs, once: **Re-run failed jobs** on the run's page, or
`gh run rerun <run-id> --failed`. A job that fails and then passes on the rerun
is flaky: open a bug for it rather than rerunning past it again. A job that
fails again is a real failure: find its cause.

First-time contributors are welcome to add themselves to the
[`AUTHORS`](AUTHORS) file in the same PR.

### Merging

`develop` merges through a merge queue. **Merge when ready** on the PR, or
`gh pr merge <number>`, adds a green PR to the queue, or queues it as soon as
its checks pass. The queue squashes the PR onto the latest `develop` together
with the PRs ahead of it, and runs `Validate Branch` again on the result. When
that passes, the queue merges it. When it fails, the PR leaves the queue and the
PRs behind it are tested again without it; find the failed run under
`Validate Branch` in the Actions tab, fix the branch, and add the PR again.

The branch does not have to be up to date with `develop`, since the queue tests
it on the latest `develop` anyway. Bring `develop` into it only to resolve a
conflict or to reproduce a failure from the queue.

The required checks are `validation-outcome` (`Validate Branch`) and
`pr-lint-title` (`~PR Preparation` on a pull request, `~Merge Queue` in the
queue). A new job joins the requirement by being listed in
`validation-outcome`'s `needs`, never by adding it to the ruleset.

CI runs on GitHub's hosted runners only. The repository is public, so a
self-hosted runner would run fork pull requests' code.

## Releasing

release-please keeps a release PR open on `develop`, titled
`chore: release vX.Y.Z`, with the changelog since the last release. It moves
the version in `version.txt` and in `plugins/sdlc/.claude-plugin/plugin.json`
together. Merging it, through the merge queue like any other PR, tags `vX.Y.Z`
and publishes the GitHub release. The `v*` tags are protected: nobody moves or
deletes one.

Merging the release PR is also what reaches users: Claude Code updates an
installed plugin only when its `version` changes, so commits between releases
stay on `develop` until the next one. There is nothing else to deploy.

release-please runs with a GitHub App's token, so the release PR's checks start
on their own. The App is installed on the repository with contents, issues and
pull-requests write. Its Client ID and private key are the
`RELEASE_APP_CLIENT_ID` and `RELEASE_APP_PRIVATE_KEY` repository secrets. Until
both are set, the workflow passes with a warning and opens no release PR.
"Allow GitHub Actions to create and approve pull requests" stays off.

## Dependency updates

Renovate proposes every dependency update, as `renovate.json` says: the pinned
Actions, the images pinned by digest in the workflows and hooks, and the
versions of Claude Code and PyYAML that CI installs. It runs in the `Renovate`
workflow (`.github/workflows/renovate.yaml`), with the token of the Renovate
App, a second GitHub App, kept apart from the release one. The App is installed
on the repository with contents, pull requests, issues, workflows and commit
statuses write, and metadata read, and no webhook. Its Client ID and private key
are the `RENOVATE_APP_CLIENT_ID` and `RENOVATE_APP_PRIVATE_KEY` secrets of the
`renovate` environment, never repository secrets: the environment's deployment
branches are `develop` alone, with no required reviewers, so only the
workflow's runs on `develop` get them. Until both are set, a scheduled run
passes with a warning and does nothing. Its global config,
`.github/renovate-global.json`, keeps it to this repository and runs none of the
repository's code.

The workflow runs once a week, on Mondays at 01:17 UTC, inside the window, 00:00
to 06:00 UTC, in which `renovate.json` lets Renovate open pull requests. Every
update waits 7 days after its release first. To start a run by hand:

```bash
gh workflow run renovate.yaml                  # propose what is due now
gh workflow run renovate.yaml -f dry-run=true  # log it, and change nothing
```

Security updates are Dependabot's: alerts and security update pull requests are
on, and `renovate.json` leaves vulnerability alerts to it.

## Reporting Issues

- **Bugs** — use the [bug report](.github/ISSUE_TEMPLATE/bug_report.yaml)
  template
- **Feature requests** — use the
  [feature request](.github/ISSUE_TEMPLATE/feature_request.yaml) template
- **Tasks** — use the [task](.github/ISSUE_TEMPLATE/task.yaml) template for
  work that is neither, such as a chore, a refactor or a piece of an epic
- **Security vulnerabilities** — see [SECURITY.md](SECURITY.md); do not open
  issues

You don't need to set an issue's priority, effort or area: a maintainer sets
them when triaging it (see _Triaging Issues_ below).

## Triaging Issues

A maintainer, or an agent working for one, triages each new issue before work on
it starts, and gives it four things:

- **A type:** Bug, Feature or Task, the organization's issue types. The issue
  templates set it, so check that it fits.
- **A Priority:** an organization issue field. Urgent blocks the current
  milestone or is broken; High is next up; Medium is planned; Low is someday.
- **An Effort:** High, Medium or Low, an organization issue field, by the rubric
  below.
- **At least one area label:** `plugin`, `ci`, `config` or `documentation`. A
  new area goes in `.github/labels.json`, `.github/labeler.yaml` and
  `AREA_LABELS` in `scripts/triage-fields.sh`.

Set the fields in the issue's sidebar. Once all four are set, remove the
`triage` label. Mark an issue an outside contributor could take with
`help wanted`, and a contained one with `good first issue` as well.

Effort is how much work the issue is:

- **Low:** a contained change, from a few hours to a day (about 200 hand-written
  lines or fewer).
- **Medium:** one area over a day to a few days (about 200–1,000 lines), or a
  decision or document that needs research.
- **High:** a week or more, several areas or a new subsystem (over 1,000 lines),
  or an epic.

When refining an issue changes its scope, set its Effort again.

The `Triage Fields` workflow
([`.github/workflows/triage-fields.yaml`](.github/workflows/triage-fields.yaml))
runs every day and adds the `triage` label to each open issue missing a
Priority, an Effort or an area label, so an issue that slipped through comes
back to the triage queue. Adding that label is all it does: it never sets,
changes or clears a field, and never removes a label. To run it by hand, or to
see what it would label without labelling anything:

```bash
gh workflow run triage-fields.yaml
GH_REPO=KnobanLabs/sdlc scripts/triage-fields.sh --dry-run
```
