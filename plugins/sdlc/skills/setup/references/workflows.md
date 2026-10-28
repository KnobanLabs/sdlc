# Setup: CI, hooks, and automation

The workflows, hooks, scripts, and configs `/sdlc:setup` writes, itself or
through the Release Engineer, alongside `scaffold.md`. Each file that takes comments starts
with the copyright header (`scaffold.md`). Keep the comments: they record why
each choice was made. Wherever a file below says `develop`, use the default
branch (`scaffold.md`, `{{branch}}`).

## Pins

Pin every action by commit SHA with its version in a comment, and every image
by digest with its tag. Use each one's **newest release that is at least 7
days old**, looked up as you write. Never copy a SHA or digest from memory.

- **Actions:** `gh api repos/<owner>/<action>/releases --jq '.[] | select(.prerelease | not) | [.tag_name, .published_at] | @tsv'`,
  then the tag's commit: `gh api repos/<owner>/<action>/commits/<tag> --jq .sha`.
- **Images:** the tag from the project's releases, then its digest:
  `docker buildx imagetools inspect <image>:<tag> --format '{{json .Manifest.Digest}}'`.
  Without Docker, read it from the registry: ghcr.io and Docker Hub both issue
  anonymous pull tokens, and a `HEAD` on the manifest returns
  `Docker-Content-Digest`.

| Pin | What it is |
|---|---|
| `actions/checkout` | Checkout |
| `amannn/action-semantic-pull-request` | PR title lint |
| `actions/labeler` | PR labels from paths |
| `actions/create-github-app-token` | App tokens for release-please and Renovate |
| `googleapis/release-please-action` | Releases |
| `renovatebot/github-action`, with `ghcr.io/renovatebot/renovate` | Renovate |
| `ghcr.io/aquasecurity/trivy` | Secret scan (CI, the hook, and `CONTRIBUTING.md`, all the same pin) |
| `docker.io/rhysd/actionlint` | Workflow lint |
| `ghcr.io/zizmorcore/zizmor` | Workflow security audit |

Below, `<checkout>` stands for `actions/checkout@<sha> # <version>`, and so on.

## Which files

| Files | Written when |
|---|---|
| `validate.yaml`, `pr_preparation.yaml`, `labeler.yaml`, `trivy-secret.yaml`, `.githooks/`, `scripts/install-hooks.sh` | Always |
| `merge_queue.yaml`, and the `merge_group` trigger in `validate.yaml` | The merge queue is available (`github-setup.md`, section 1) |
| `release_please.yaml`, `release-please-config.json`, `.release-please-manifest.json`, `version.txt` | Releases |
| `renovate.yaml`, `renovate.json`, `.github/renovate-global.json` | Renovate |
| `.github/dependabot.yml` | Dependabot |
| `triage-fields.yaml`, `scripts/triage-fields.sh` | An organization with `Priority` and `Effort` issue fields |

**Adopting**, keep the repository's own CI. Add only the jobs the plan names,
and add their checks to its existing aggregate job when it has one.

## Verify

Before committing, run what CI will. With Docker, run the three `docker run`
commands in `validate.yaml`, and `shellcheck` on the scripts and hooks. Without it, run `shellcheck` if it's installed,
and say which checks will run first in CI. Also check that every JSON file
parses (`jq . <file>`) and that `git ls-files --stage` shows the scripts and
hooks as executable (`100755`).

## .github/workflows/validate.yaml

```yaml
name: Validate Branch

permissions: {}

on:
  pull_request:
    branches:
      - develop
  merge_group:
    branches:
      - develop
  workflow_dispatch:
  # Every night on develop, for what changed underneath it: a new runner
  # image, or a newer rule in a pinned scanner's database.
  schedule:
    - cron: '13 5 * * *'

# A new push cancels a pull request's run. Each merge queue group has a ref of
# its own, so one queue run never cancels another, and the event in the group
# keeps the nightly run and a manual run on develop from cancelling each other.
concurrency:
  group: ${{ github.workflow }}-${{ github.event_name }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # The checks that need no toolchain. A project adds its own here as steps,
  # or as jobs of their own listed in validation-outcome's needs.
  static:
    name: Static checks
    runs-on: ${{ vars.RUNNER_LINUX || 'ubuntu-24.04' }}
    timeout-minutes: 15
    permissions:
      contents: read # To check out the code.
    steps:
      - name: Checkout
        uses: <checkout>
        with:
          persist-credentials: false

      # The image the pre-commit hook runs too, which keeps the two the same.
      # Trivy ignores a missing --secret-config and falls back to its allow
      # rules without a word, so the step checks the file is there.
      - name: Scan for secrets
        run: |
          config=.github/trivy-secret.yaml
          if [[ ! -f "$config" ]]; then
            echo "::error::$config is missing, so the scan would skip examples, Markdown and tests."
            exit 1
          fi
          docker run --rm --network none -v "$PWD:/repo:ro" \
            <trivy image:tag@digest> \
            fs --scanners secret --skip-version-check --exit-code 1 \
            --secret-config "/repo/$config" /repo

      # actionlint runs shellcheck over each run: block too, with the
      # shellcheck its image ships.
      - name: Lint the workflows
        run: |
          docker run --rm --network none -v "$PWD:/repo:ro" -w /repo \
            <actionlint image:tag@digest> \
            -color

      # The workflows' security: template injection, excessive permissions,
      # unpinned uses, and the dangerous triggers. Offline, so it reads only
      # the files, never GitHub's API.
      - name: Audit the workflows
        run: |
          docker run --rm --network none -v "$PWD:/repo:ro" -w /repo \
            <zizmor image:tag@digest> \
            --offline --persona regular .github/workflows

      - name: Lint the shell scripts
        run: |
          mapfile -t scripts < <(git ls-files -z -- 'scripts/*.sh' '.githooks/*' | tr '\0' '\n')
          shellcheck --external-sources "${scripts[@]}"

  # The one required check. A skipped required check counts as passing, so
  # this job runs even when the run is cancelled, and fails unless every job
  # in needs succeeded. A new job joins the requirement by being added to
  # needs, never to the ruleset.
  validation-outcome: # zizmor: ignore[anonymous-definition]
    needs: [static]
    if: ${{ always() }}
    runs-on: ${{ vars.RUNNER_LINUX || 'ubuntu-24.04' }}
    timeout-minutes: 10
    permissions: {}
    steps:
      - name: Check every job passed
        env:
          NEEDS: ${{ toJSON(needs) }}
        run: |
          failed=$(jq -r 'to_entries[] | select(.value.result != "success") | "\(.key): \(.value.result)"' <<< "$NEEDS")
          if [[ -n "$failed" ]]; then
            while IFS= read -r line; do echo "::error::$line"; done <<< "$failed"
            exit 1
          fi
          echo "Every job passed."
```

Without the merge queue, drop the `merge_group` trigger and the merge-queue
clause of the concurrency comment.

## .github/workflows/pr_preparation.yaml

```yaml
name: ~PR Preparation

# pull_request_target runs this file from the base branch, with a token that
# can write to fork pull requests too, which labelling needs. That is safe only
# because no job checks out or runs the pull request's code: both run pinned
# actions that read the pull request through the API. Keep it that way.
on: # zizmor: ignore[dangerous-triggers]
  pull_request_target:
    types:
      - opened
      - edited
      - synchronize

permissions: {}

# A newer run on a pull request cancels its older one. pull_request_target sets
# github.ref to the base branch, so the group is keyed on the pull request's
# number. Every run lints the title, even for an edit to the body alone: a
# skipped check would show as passed, over an earlier failure on the same
# commit.
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  # The job id is the required check's name, so it gets no `name:`. This file
  # never runs in the merge queue, so merge_queue.yaml reports the same check
  # there under the same job id.
  pr-lint-title: # zizmor: ignore[anonymous-definition]
    # Pinned, outside the runner toggle: pull_request_target runs for fork pull
    # requests too, with a token that can write (CONTRIBUTING.md, Runners).
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      pull-requests: read # To read the pull request's title.
    steps:
      - uses: <action-semantic-pull-request>
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  pr-label:
    name: Label the pull request
    # Pinned, outside the runner toggle: see pr-lint-title.
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      contents: read # To read the labeler configuration.
      pull-requests: write # To add and remove the pull request's labels.
    steps:
      - uses: <labeler>
        with:
          sync-labels: true
          configuration-path: .github/labeler.yaml
```

Without the merge queue, the first job's comment drops its last sentence.

## .github/workflows/merge_queue.yaml

```yaml
name: ~Merge Queue

# The merge queue waits for every required check on each group it builds.
# pr_preparation.yaml runs only on pull requests, so its title check would never
# report on a group, and every pull request would wait in the queue until it
# timed out. This workflow reports that check there, and checks out nothing.
# It has no concurrency group: each merge group has a ref of its own and one run
# of this workflow, and a shared group would cancel another group's check.
on: # zizmor: ignore[concurrency-limits]
  merge_group:
    branches:
      - develop

permissions: {}

jobs:
  # The queue takes only a pull request whose required checks passed, so its
  # title passed its lint before it joined. The job id is the required check's
  # name, and must stay the same as the job id in pr_preparation.yaml.
  pr-lint-title: # zizmor: ignore[anonymous-definition]
    runs-on: ${{ vars.RUNNER_LINUX || 'ubuntu-24.04' }}
    timeout-minutes: 10
    permissions: {}
    steps:
      - name: Pass the title check
        run: echo "The title passed its lint on the pull request."
```

## .github/labeler.yaml and .github/trivy-secret.yaml

```yaml
# The area labels ~PR Preparation sets from the paths a pull request changes,
# kept in sync with its diff (sync-labels). Each one is in .github/labels.json
# too. Add the project's own areas here as its folders appear.

config:
  - changed-files:
      - any-glob-to-any-file:
          - .editorconfig
          - .gitattributes
          - .gitignore
          - .vscode/**
          - .mcp.json

infra:
  - changed-files:
      - any-glob-to-any-file:
          - deploy/**
          - infra/**

documentation:
  - changed-files:
      - any-glob-to-any-file:
          - '**/*.md'
          - .github/PULL_REQUEST_TEMPLATE.md
          - .github/ISSUE_TEMPLATE/**
          - .github/copilot-instructions.md
          - .agents/**
          - .claude/**

ci:
  - changed-files:
      - any-glob-to-any-file:
          - .github/workflows/**
          - .github/actions/**
          - .github/labeler.yaml
          - .github/labels.json
          - .github/renovate-global.json
          - .github/dependabot.yml
          - .github/trivy-secret.yaml
          - .githooks/**
          - scripts/**
          - renovate.json
          - release-please-config.json
          - .release-please-manifest.json

dependencies:
  # Renovate's and Dependabot's branches, whatever they change. Dependabot's
  # security updates come with a label of their own that sync-labels would
  # otherwise strip.
  - head-branch: ['^renovate/', '^dependabot/']
```

Add each of the project's own areas from the brief, with the folders it will
have, when the stack makes them clear.

```yaml
# Trivy's secret scan config, for CI's Scan for secrets step, the pre-commit
# hook and the local command in CONTRIBUTING.md. By default Trivy skips every
# path with "example" in it, all Markdown and test folders, which is where an
# .env.example or a doc's sample would leak a real value, so all three are
# scanned. Add a project's own token formats under rules.
disable-allow-rules:
  - tests
  - examples
  - markdown
```

## .githooks and scripts/install-hooks.sh

`.githooks/pre-commit`, executable:

```bash
#!/usr/bin/env bash
# Scans what a commit stages for secrets, with the Trivy image and config CI's
# Scan for secrets step uses, so a secret is stopped before it is committed.
# Opt in with `scripts/install-hooks.sh` (CONTRIBUTING.md: Secret scan before
# each commit). It copies the staged version of each added or changed file to a
# temporary folder, which it always removes, and runs Trivy over it with no
# network and the folder read-only. It fails when Docker isn't running or
# can't see the folder, rather than letting the commit through without a scan;
# SKIP_SECRET_SCAN=1 or `git commit --no-verify` skips it, and CI still scans
# the push. pre-merge-commit runs it for the merges git commits itself.

set -euo pipefail

# The image validate.yaml's Scan for secrets step runs: keep the two the same.
image=<trivy image:tag@digest>
config=.github/trivy-secret.yaml

if [[ "${SKIP_SECRET_SCAN:-}" == 1 ]]; then
  echo "pre-commit: SKIP_SECRET_SCAN=1, so the secret scan is skipped." >&2
  exit 0
fi

files=$(git diff --cached --name-only --diff-filter=d -z | tr '\0' '\n')
if [[ -z "$files" ]]; then
  exit 0
fi

# checkout-index --ignore-skip-worktree-bits came with git 2.36.
read -r major minor < <(git version | sed -E 's/^git version ([0-9]+)\.([0-9]+).*/\1 \2/')
if ! [[ "$major" =~ ^[0-9]+$ && "$minor" =~ ^[0-9]+$ ]] ||
  ((major < 2 || (major == 2 && minor < 36))); then
  echo "pre-commit: the secret scan needs git 2.36 or newer, and this is" \
    "$(git version). Update git, or commit with SKIP_SECRET_SCAN=1." >&2
  exit 1
fi

if ! docker info > /dev/null 2>&1; then
  echo "pre-commit: Docker isn't running, so the staged files can't be scanned" \
    "for secrets. Start Docker, or commit with SKIP_SECRET_SCAN=1 to skip the" \
    "scan; CI still runs it." >&2
  exit 1
fi

# Trivy ignores a missing config and falls back to rules that skip examples,
# Markdown and tests, so the scan needs the staged one.
if ! git cat-file -e ":$config" 2> /dev/null; then
  echo "pre-commit: $config isn't staged, so the scan would skip examples," \
    "Markdown and tests. Restore it, or commit with SKIP_SECRET_SCAN=1." >&2
  exit 1
fi

# In the clone's git folder rather than the system's temporary one, which a
# Docker running in a VM, such as Colima's, may not share.
tree=$(mktemp -d "$(git rev-parse --path-format=absolute --git-common-dir)/secret-scan.XXXXXX")
trap 'rm -rf "$tree"' EXIT

# The staged versions, as the commit will hold them, at their own paths, with
# the staged config, which Trivy reads from the same folder. A sparse
# checkout's index marks files outside it, which are still committed.
{
  git diff --cached --name-only --diff-filter=d -z
  printf '%s\0' "$config"
} | git checkout-index --force --ignore-skip-worktree-bits \
  --prefix="$tree/" -z --stdin

# A Docker that can't see the folder mounts an empty one, where Trivy would
# find nothing and pass, so the scan first checks the config is there.
if ! docker run --rm --network none -v "$tree:/repo:ro" --entrypoint sh \
  "$image" -c '
    if [ ! -f "/repo/$1" ]; then
      echo "pre-commit: Docker can'\''t see the staged files, so it can'\''t" \
        "scan them." >&2
      exit 1
    fi
    exec trivy fs --scanners secret --skip-version-check --exit-code 1 \
      --quiet --secret-config "/repo/$1" /repo
  ' sh "$config"; then
  echo "pre-commit: the secret scan failed. Remove the secret from the staged" \
    "files and commit again; if it found none, the message above says why" \
    "the scan didn't run." >&2
  exit 1
fi
```

`.githooks/pre-merge-commit`, executable:

```bash
#!/usr/bin/env bash
# git merge and git pull make their merge commits without running pre-commit,
# so this runs the same secret scan on what a merge stages.

exec "$(dirname "$0")/pre-commit" "$@"
```

`scripts/install-hooks.sh`, executable:

```bash
#!/usr/bin/env bash
# Turns on the hooks in .githooks/ for this clone (CONTRIBUTING.md, Secret scan
# before each commit), by pointing core.hooksPath at them. Run it again after
# a fresh clone; `git config --unset core.hooksPath` turns them off.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
chmod +x .githooks/*
git config core.hooksPath .githooks
echo "Hooks on: core.hooksPath is .githooks. The secret scan needs Docker running."
```

The header goes after the shebang line in each. Don't run `install-hooks.sh`
in the human's clone: changing git config is the human's call
(`approvals.md`). The report tells them to run it.

## Releases

`version.txt` is `0.0.0`. `.release-please-manifest.json` is `{ ".": "0.0.0" }`.
`release-please-config.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    ".": {
      "changelog-path": "CHANGELOG.md",
      "changelog-host": "https://github.com",
      "release-type": "simple",
      "bump-minor-pre-major": false,
      "bump-patch-for-minor-pre-major": false,
      "draft": false,
      "prerelease": false,
      "initial-version": "0.1.0",
      "package-name": "<repo name>",
      "include-component-in-tag": false,
      "include-v-in-tag": true,
      "include-v-in-release-name": true
    }
  },
  "pull-request-title-pattern": "chore: release${component} v${version}",
  "pull-request-header": "Merging this PR will create a release."
}
```

`release-type` stays `simple` until the stack has a manifest file that
release-please can version, such as `node` for `package.json`. The Architect's
foundation tickets change it.

`.github/workflows/release_please.yaml`:

```yaml
name: ~Release Please

# No concurrency group. Cancelling a run part-way through a release could leave
# it tagged but never published.
on: # zizmor: ignore[concurrency-limits]
  push:
    branches: [develop]

permissions: {}

jobs:
  release-please:
    name: Create or update release PR
    # Pinned, outside the runner toggle: it holds the release App's token and
    # cuts releases (CONTRIBUTING.md, Runners).
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    # The App token below makes every write, so GITHUB_TOKEN needs nothing.
    permissions: {}
    outputs:
      release_created: ${{ steps.release.outputs.release_created }}
      tag_name: ${{ steps.release.outputs.tag_name }}

    steps:
      # The expressions below say only whether each secret is set, so neither
      # reaches the script. Until the App is set up, neither is
      # (CONTRIBUTING.md, Releasing).
      - name: Check for the release App's secrets
        id: app
        env:
          HAS_CLIENT_ID: ${{ secrets.RELEASE_APP_CLIENT_ID != '' }}
          HAS_PRIVATE_KEY: ${{ secrets.RELEASE_APP_PRIVATE_KEY != '' }}
        run: |
          if [[ "$HAS_CLIENT_ID" == true && "$HAS_PRIVATE_KEY" == true ]]; then
            echo 'configured=true' >> "$GITHUB_OUTPUT"
            exit 0
          fi
          echo 'configured=false' >> "$GITHUB_OUTPUT"
          message="release-please didn't run: the repository secrets RELEASE_APP_CLIENT_ID and RELEASE_APP_PRIVATE_KEY aren't both set (CONTRIBUTING.md, Releasing)."
          echo "$message" >> "$GITHUB_STEP_SUMMARY"
          echo "::warning title=Release App not set up::$message"

      # A pull request or push made with GITHUB_TOKEN starts no workflows, so
      # the release PR's checks would wait for someone to start them. An App
      # token's do start them, and Actions never has to be allowed to open
      # pull requests.
      - name: Create the release App token
        id: app-token
        if: steps.app.outputs.configured == 'true'
        uses: <create-github-app-token>
        with:
          client-id: ${{ secrets.RELEASE_APP_CLIENT_ID }}
          private-key: ${{ secrets.RELEASE_APP_PRIVATE_KEY }}
          permission-contents: write # To commit, tag and publish the release.
          permission-issues: write # To label the release pull request.
          permission-pull-requests: write # To open and update the release PR.

      - name: Run release-please
        id: release
        if: steps.app.outputs.configured == 'true'
        uses: <release-please-action>
        with:
          token: ${{ steps.app-token.outputs.token }}
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json

  # TODO(setup): a job that builds and publishes or deploys the release, with
  # `needs: release-please` and
  # `if: needs.release-please.outputs.release_created == 'true'`, asking only
  # for the permissions it uses.
```

## Renovate

`renovate.json`:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "description": [
    "Proposes every dependency update: the GitHub Actions, and the images pinned by digest in the workflows and hooks. Add each ecosystem the project uses to enabledManagers."
  ],
  "enabledManagers": ["github-actions", "custom.regex"],
  "dependencyDashboard": false,
  "vulnerabilityAlerts": { "enabled": false },
  "schedule": ["* 0-5 * * 1"],
  "rebaseWhen": "behind-base-branch",
  "prHourlyLimit": 0,
  "prConcurrentLimit": 20,
  "minimumReleaseAge": "7 days",
  "internalChecksFilter": "strict",
  "semanticCommits": "enabled",
  "semanticCommitType": "build",
  "semanticCommitScope": "deps",
  "pinDigests": true,
  "customManagers": [
    {
      "customType": "regex",
      "description": "Images run by digest in the workflows and the hooks, written <image>:<version>@sha256:<digest>.",
      "managerFilePatterns": ["/^\\.github/workflows/.+\\.ya?ml$/", "/^\\.githooks/.+$/", "/^CONTRIBUTING\\.md$/"],
      "matchStrings": [
        "(?<depName>(?:ghcr\\.io|docker\\.io)/[a-z0-9._/-]+):(?<currentValue>[A-Za-z0-9._-]+)@(?<currentDigest>sha256:[a-f0-9]{64})"
      ],
      "datasourceTemplate": "docker"
    }
  ],
  "packageRules": [
    {
      "description": "Never the runner images in runs-on, while the Actions still move: a new runner image is a pull request of its own.",
      "matchManagers": ["github-actions"],
      "matchDepTypes": ["github-runner"],
      "enabled": false
    },
    {
      "description": "The Actions, pinned by commit with the version in a comment: minor and patch updates share one pull request.",
      "matchManagers": ["github-actions"],
      "matchUpdateTypes": ["minor", "patch", "digest"],
      "groupName": "actions minor and patch"
    },
    { "matchManagers": ["github-actions"], "semanticCommitType": "ci" },
    {
      "description": "The images CI and the hooks run: minor, patch and digest updates share one pull request, and majors each get their own.",
      "matchManagers": ["custom.regex"],
      "matchUpdateTypes": ["minor", "patch", "digest"],
      "groupName": "ci images minor and patch",
      "semanticCommitType": "ci"
    },
    {
      "description": "GHCR gives no release date, so Renovate can't hold its images back 7 days, and without this would never propose them. The pull request says to check the release's age by hand.",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["ghcr.io/**"],
      "minimumReleaseAgeBehaviour": "timestamp-optional",
      "prBodyNotes": [
        "`{{{depName}}}`'s registry gives no release date, so this pull request didn't wait 7 days: before merging, check on the project's releases that it came out at least 7 days ago."
      ]
    }
  ]
}
```

`.github/renovate-global.json`:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-global-schema.json",
  "platform": "github",
  "autodiscover": false,
  "onboarding": false,
  "requireConfig": "required",
  "binarySource": "install",
  "allowScripts": false,
  "ignoreScripts": true,
  "allowPlugins": false,
  "allowedCommands": []
}
```

`.github/workflows/renovate.yaml`:

```yaml
# Renovate, which proposes every dependency update (renovate.json), run as the
# Renovate App, installed on this repository (CONTRIBUTING.md, Dependency
# updates). Its global config, which runs none of the repository's code, is
# .github/renovate-global.json, and RENOVATE_REPOSITORIES keeps it to this
# repository.
#
# It runs once a week, on Monday at 01:17 UTC, inside the window renovate.json's
# schedule allows, Mondays 00:00 to 06:00 UTC. The same run rebases the open
# pull requests develop has moved past. A run started by hand proposes what is
# due at once, unless told to keep to the window; a dry run changes nothing.
#
# The App's two secrets are the renovate environment's, which only develop may
# use. Until both are set, a scheduled run does nothing and passes with a
# warning, and a run started by hand fails.
name: Renovate

permissions: {}

on:
  schedule:
    - cron: '17 1 * * 1'
  workflow_dispatch:
    inputs:
      dry-run:
        description: Log what Renovate would do, and change nothing
        type: boolean
        default: false
      ignore-schedule:
        description: Propose what is due now, outside the Monday window
        type: boolean
        default: true
      log-level:
        description: How much Renovate logs
        type: choice
        options:
          - info
          - debug
        default: info

# One run at a time, never cancelled part-way, so two never push the same
# branch.
concurrency:
  group: ${{ github.workflow }}
  cancel-in-progress: false

jobs:
  renovate:
    name: Run Renovate
    # Pinned, outside the runner toggle: it holds the Renovate App's token,
    # which can push workflows (CONTRIBUTING.md, Runners).
    runs-on: ubuntu-24.04
    timeout-minutes: 60
    # Holds the App's secrets. Its deployment branches are develop alone, so a
    # run from any other branch fails before it starts, with neither secret.
    environment: renovate
    # The App token below makes every read and write, so GITHUB_TOKEN needs
    # nothing.
    permissions: {}

    steps:
      # The expressions below say only whether each secret is set, so neither
      # reaches the script.
      - name: Check for the Renovate App's secrets
        id: app
        env:
          HAS_CLIENT_ID: ${{ secrets.RENOVATE_APP_CLIENT_ID != '' }}
          HAS_PRIVATE_KEY: ${{ secrets.RENOVATE_APP_PRIVATE_KEY != '' }}
          EVENT: ${{ github.event_name }}
        run: |
          if [[ "$HAS_CLIENT_ID" == true && "$HAS_PRIVATE_KEY" == true ]]; then
            echo 'configured=true' >> "$GITHUB_OUTPUT"
            exit 0
          fi
          echo 'configured=false' >> "$GITHUB_OUTPUT"
          message="Renovate didn't run: the renovate environment's secrets RENOVATE_APP_CLIENT_ID and RENOVATE_APP_PRIVATE_KEY aren't both set (CONTRIBUTING.md, Dependency updates)."
          echo "$message" >> "$GITHUB_STEP_SUMMARY"
          if [[ "$EVENT" == schedule ]]; then
            echo "::warning title=Renovate App not set up::$message"
          else
            echo "::error title=Renovate App not set up::$message"
            exit 1
          fi

      # Not GITHUB_TOKEN, whose pull requests start no workflows. Nor the
      # release App's, which lacks workflows, and keeps release writes apart
      # from dependency ones. With no owner or repositories given, the token
      # reaches this repository alone.
      - name: Create the Renovate App token
        id: app-token
        if: steps.app.outputs.configured == 'true'
        uses: <create-github-app-token>
        with:
          client-id: ${{ secrets.RENOVATE_APP_CLIENT_ID }}
          private-key: ${{ secrets.RENOVATE_APP_PRIVATE_KEY }}
          permission-contents: write # To clone, and push and delete its branches.
          permission-pull-requests: write # To open, update and close its pull requests.
          permission-issues: write # To open the issue that reports a broken renovate.json.
          permission-workflows: write # To move the Actions pins in .github/workflows/.
          permission-statuses: write # To set its renovate/ statuses, such as the 7-day wait's.

      # For the global config alone: Renovate clones the repository itself.
      - name: Check out the global config
        if: steps.app.outputs.configured == 'true'
        uses: <checkout>
        with:
          token: ${{ steps.app-token.outputs.token }}
          persist-credentials: false
          sparse-checkout: .github/renovate-global.json
          sparse-checkout-cone-mode: false

      # The action runs the image by its digest. Renovate's github-actions
      # manager reads the digest and the version beside it, and moves both.
      - name: Run Renovate
        if: steps.app.outputs.configured == 'true'
        uses: <renovatebot/github-action>
        env:
          LOG_LEVEL: ${{ inputs.log-level || 'info' }}
          RENOVATE_REPOSITORIES: ${{ github.repository }}
          RENOVATE_DRY_RUN: ${{ inputs.dry-run && 'full' || '' }}
          RENOVATE_FORCE:
            ${{ inputs.ignore-schedule && '{"schedule":["at any time"]}' || ''
            }}
        with:
          token: ${{ steps.app-token.outputs.token }}
          configurationFile: .github/renovate-global.json
          renovate-image: ghcr.io/renovatebot/renovate@<digest>
          renovate-version: <version>
```

On the environment fallback (`github-setup.md`, section 1), drop
`environment:` and its comment, and say in the header comment that the secrets
are the repository's.

## Dependabot

`.github/dependabot.yml`, instead of Renovate:

```yaml
# Dependabot's version updates (CONTRIBUTING.md, Dependency updates): one
# grouped pull request a week for the pinned Actions, each update held 7 days
# after its release. Add each ecosystem the project uses. Security updates come
# from the repository's Dependabot settings, apart from this file.
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
      day: monday
      time: '01:17'
      timezone: Etc/UTC
    cooldown:
      default-days: 7
    commit-message:
      prefix: ci
    groups:
      actions-minor-and-patch:
        update-types: [minor, patch]
```

## Triage fields

`.github/workflows/triage-fields.yaml`:

```yaml
# The triage check (scripts/triage-fields.sh): each day it adds the `triage`
# label to every open issue missing a Priority, an Effort (the organization's
# issue fields) or an area label, so the issue comes back to the triage queue
# (CONTRIBUTING.md, Triaging Issues). Adding that label is all it writes.
#
# It runs with the workflow's own token: issues read access can read an
# issue's field values. A pull request that changes the check runs it without
# writing, and shows what it would label in the run's summary.
name: Triage Fields

permissions: {}

on:
  schedule:
    - cron: '43 4 * * *'
  workflow_dispatch:
  pull_request:
    branches:
      - develop
    paths:
      - .github/workflows/triage-fields.yaml
      - scripts/triage-fields.sh

# One labelling run at a time.
concurrency:
  group:
    ${{ github.workflow }}-${{ github.event_name == 'pull_request' && github.ref
    || 'label' }}
  cancel-in-progress: false

jobs:
  # A pull request's run reads and reports, and writes nothing.
  check:
    name: Find issues missing triage fields, without writing
    if: github.event_name == 'pull_request'
    runs-on: ${{ vars.RUNNER_LINUX || 'ubuntu-24.04' }}
    timeout-minutes: 10
    permissions:
      contents: read # To check out the code.
      issues: read # To list the open issues, their labels and fields.
    steps:
      - name: Checkout
        uses: <checkout>
        with:
          persist-credentials: false

      - name: Find issues missing triage fields
        env:
          GH_TOKEN: ${{ github.token }}
        run: scripts/triage-fields.sh --dry-run

  label:
    name: Label issues missing triage fields
    if: github.event_name != 'pull_request'
    runs-on: ${{ vars.RUNNER_LINUX || 'ubuntu-24.04' }}
    timeout-minutes: 10
    permissions:
      contents: read # To check out the code.
      issues: write # To add the triage label, and read the issues.
    steps:
      - name: Checkout
        uses: <checkout>
        with:
          persist-credentials: false

      - name: Label issues missing triage fields
        env:
          GH_TOKEN: ${{ github.token }}
        run: scripts/triage-fields.sh
```

`scripts/triage-fields.sh`, executable, with `AREA_LABELS` holding
`{{areas}}`:

```bash
#!/usr/bin/env bash
# The triage check (CONTRIBUTING.md, Triaging Issues): adds the `triage` label
# to every open issue missing a Priority, an Effort or an area label, so it
# comes back to the triage queue.
#
#   scripts/triage-fields.sh [--dry-run]
#
# --dry-run lists the issues it would label and writes nothing. It needs gh
# and jq, and reads the repository from GH_REPO, then GITHUB_REPOSITORY, then
# the clone's. It only ever adds `triage`: it never sets, changes or clears a
# field, and never removes a label. Pull requests and closed issues are left
# alone. It exits 1 when it couldn't read the issues or label one, after
# labelling what it could.

set -euo pipefail

TRIAGE=triage
FIELDS='["Priority", "Effort"]'
# The area labels, one of which every triaged issue carries. Add the project's
# own here, in .github/labels.json and in .github/labeler.yaml.
AREA_LABELS='["ci", "config", "documentation", "infra"]'

dry_run=false
case "${1:-}" in
  --dry-run) dry_run=true ;;
  '') ;;
  *)
    echo "usage: $0 [--dry-run]" >&2
    exit 2
    ;;
esac

repo=${GH_REPO:-${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}}

issues=$(gh api --paginate "repos/$repo/issues?state=open&per_page=100" |
  jq -s '[.[][] | select(.pull_request == null)]')

# A listing without issue_field_values means the token can't read the fields,
# and one where no open issue shows a field means it can't read that one or it
# was renamed. Labelling every open issue then would bury the triage queue, so
# both fail the run instead.
unread=$(jq -r 'map(select(has("issue_field_values") | not)) | first | .number // empty' <<< "$issues")
if [[ -n "$unread" ]]; then
  echo "✗ The listing shows no fields for #$unread: the token can't read issue fields. Nothing was labelled." >&2
  exit 1
fi
unseen=$(jq -r --argjson fields "$FIELDS" '
  if length == 0 then empty else
    ([.[].issue_field_values[].issue_field_name] | unique) as $shown
    | $fields - $shown | join(" or ") | select(. != "")
  end' <<< "$issues")
if [[ -n "$unseen" ]]; then
  echo "✗ None of the open issues shows a $unseen: the token can't read the field, or it was renamed. Nothing was labelled." >&2
  exit 1
fi

incomplete=$(jq -c --argjson fields "$FIELDS" --argjson areas "$AREA_LABELS" --arg triage "$TRIAGE" '
  .[]
  | ([.issue_field_values[].issue_field_name]) as $set
  | ([.labels[].name]) as $labels
  | {
      number,
      url: .html_url,
      title,
      missing: (($fields - $set) + (if ($areas - ($areas - $labels)) == [] then ["an area label"] else [] end)),
      labelled: ($labels | index($triage) != null)
    }
  | select(.missing != [])' <<< "$issues")

checked=$(jq length <<< "$issues")
count=0
already=0
rows=()
failed=0
while IFS= read -r issue; do
  [[ -z "$issue" ]] && continue
  count=$((count + 1))
  number=$(jq -r .number <<< "$issue")
  # A title is free text: keep it to one line, and from closing the table's
  # cell or making a link, an image or HTML in the summary. The control
  # characters and the bidi overrides go too, which the log viewer would act
  # on. An escaped `[` also keeps the runner from reading `##[` as a command.
  title=$(jq -r '.title
    | gsub("[\\s\u0085]+"; " ") | ltrimstr(" ") | rtrimstr(" ")
    | gsub("[\u0000-\u001f\u007f‪-‮⁦-⁩]"; "")
    | gsub("(?<c>[|\\\\\\[\\]<>])"; "\\\(.c)")' <<< "$issue")
  missing=$(jq -r '.missing | join(", ")' <<< "$issue")
  url=$(jq -r .url <<< "$issue")
  if [[ $(jq -r .labelled <<< "$issue") == true ]]; then
    already=$((already + 1))
    action='already labelled'
  elif $dry_run; then
    action="would label \`$TRIAGE\`"
  elif gh api --silent -X POST "repos/$repo/issues/$number/labels" -f "labels[]=$TRIAGE"; then
    action="labelled \`$TRIAGE\`"
  else
    echo "✗ #$number: couldn't add the label." >&2
    action='failed to label'
    failed=1
  fi
  rows+=("| [#$number]($url) $title | $missing | $action |")
done <<< "$incomplete"

{
  echo '## Triage fields'
  echo
  note=''
  $dry_run && note=' A dry run: nothing written.'
  echo "Open issues checked: $checked. Missing a Priority, an Effort or an area label: $count, of which already labelled \`$TRIAGE\`: $already.$note"
  if ((count)); then
    echo
    echo '| Issue | Missing | Action |'
    echo '| --- | --- | --- |'
    printf '%s\n' "${rows[@]}"
  fi
} | tee -a "${GITHUB_STEP_SUMMARY:-/dev/null}"

exit "$failed"
```
