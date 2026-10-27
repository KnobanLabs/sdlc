# Init: GitHub setup

The settings, protections, and Project that init applies, as `gh` commands.
`<owner>/<repo>` is the repository; `$repo` stands for it in shell. `<branch>`
is the default branch: `develop` unless the answers or the audit say otherwise.
Every step may run again: it sets what is already set to the same value, and
leaves the rest alone. Run only what the confirmed plan lists.

## 1. What the owner's plan allows

Read the plan first: `gh api user --jq .plan.name` (personal; empty without
the `read:user` scope) or `gh api orgs/<org> --jq .plan.name` (shown to
organization owners). An empty result means the plan is unknown: say so, and
plan for the fallbacks. The table gives what to expect; GitHub's answer is
what counts. When it refuses, take the
fallback and tell the human what's missing and why.

| Feature | Available | Fallback |
|---|---|---|
| Rulesets | Public repositories on every plan; private ones on Pro, Team, or Enterprise | None: conventions only. Say that pushes to the default branch aren't blocked |
| Merge queue | Repositories owned by an organization: public ones, and private ones on Enterprise Cloud | The ruleset without the `merge_queue` rule, with auto-merge. The files drop `merge_queue.yaml` and the `merge_group` triggers (`workflows.md`) |
| Environments | Public repositories; private ones on paid plans | Repository secrets, after saying that any branch's workflow could then read them |
| Secret scanning and push protection | Public repositories; private ones with GitHub Secret Protection | Skip. The hook and CI's Trivy scan still run |
| Private vulnerability reporting | Public repositories | Reporting through the maintainer's profile or an email address |
| Issue types and issue fields | Organizations | Type labels (`bug`, `enhancement`, `task`), and Project fields for Priority and Effort |

## 2. Repository

**New:** create it empty, then clone it into the project's folder:

```bash
gh repo create <owner>/<repo> --private --description "<pitch>"   # or --public
gh repo clone <owner>/<repo> <folder>
git -C <folder> switch --orphan <branch>
```

GitHub makes the first branch pushed the default branch. The files step
pushes it (`SKILL.md`, section 5, step 4).

**Adopt:** use the current clone, or clone the named repository. Record its
default branch as `<branch>`: the files and rulesets use it wherever the
defaults say `develop`.

**A local folder with no GitHub remote** is created from the folder. `--source`
needs a git repository with a commit, and `--push` pushes the current branch.

**The scan** checks exactly what git holds, never the working folder, whose
ignored files (a local `.env`) are never pushed. Copy the files into a
temporary folder inside `.git`, removed afterwards, along with
`.github/trivy-secret.yaml` from `workflows.md`, and scan that folder with the
pre-commit hook's `docker run` (`workflows.md`, `.githooks/pre-commit`). It
checks for the config inside the container, so a Docker that can't see the
folder, and mounts an empty one, fails rather than passing.
Staged files are copied with `git checkout-index` (as the pre-commit hook
does), and a branch with `git worktree add --detach <folder> <branch>`
(`git archive` would skip `export-ignore` paths), removed with
`git worktree remove --force <folder>`.
Without the config, Trivy silently skips Markdown, tests, and examples, so a
missing config stops the scan. Without Docker, say nothing was scanned, and
ask before going on.

In order:

1. **No git repository yet:** write `.gitignore` (`scaffold.md`) and
   `.github/trivy-secret.yaml` first, then `git init -b <branch>` and stage.
   Show the human what's staged, and scan the staged files **before the first
   commit**, so a secret never enters the history. Then commit.
2. **An existing local repository:** `<branch>` is the local branch that holds
   the work (usually the current one), confirmed with the human. The working
   tree must be clean before switching to it. When the plan names the default
   branch differently, renaming it (`git branch -m`) is a planned action. Scan
   `<branch>` as it stands. Earlier commits aren't scanned, so say so, and for
   a public repository recommend the human review the history first.
3. **A secret found stops the push.** In a repository started in step 1, have
   the human take the secret out of the file (into an ignored `.env`, say), or
   add the file to `.gitignore`. Then stage again, scan again, and tell them
   which files were left out. In an existing history, the
   secret must be removed from it and revoked before anything is pushed.
4. With `<branch>` checked out:
   `gh repo create <owner>/<repo> --private --source . --remote origin --push`
   (or `--public`).

## 3. Settings

After the first push, and before the rulesets. **Adopting,** send only the keys
the plan changes, never the whole body: each key left out keeps the
repository's current value (Discussions, a wiki, other merge methods).

```bash
gh api --silent -X PATCH "repos/$repo" --input - <<'EOF'
{
  "default_branch": "<branch>",
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false,
  "squash_merge_commit_title": "PR_TITLE",
  "squash_merge_commit_message": "BLANK",
  "allow_auto_merge": true,
  "allow_update_branch": true,
  "delete_branch_on_merge": true,
  "has_issues": true,
  "has_projects": true,
  "has_wiki": false,
  "has_discussions": false
}
EOF
gh api --silent -X PUT "repos/$repo/actions/permissions/workflow" \
  -F default_workflow_permissions=read -F can_approve_pull_request_reviews=false
```

`allow_forking` governs only private repositories in an organization, where
its policy may decide instead; anyone can fork a public one, whatever the
contribution answer.

## 4. Security

```bash
gh api --silent -X PUT "repos/$repo/vulnerability-alerts"         # Dependabot alerts
gh api --silent -X PUT "repos/$repo/automated-security-fixes"     # and its security updates
gh api --silent -X PATCH "repos/$repo" --input - <<'EOF'
{"security_and_analysis": {"secret_scanning": {"status": "enabled"}, "secret_scanning_push_protection": {"status": "enabled"}}}
EOF
gh api --silent -X PUT "repos/$repo/private-vulnerability-reporting"   # only when chosen
```

## 5. Labels

Create each label in `.github/labels.json` (`scaffold.md`), and the project's
own areas, with `gh label create "<name>" --color <hex> --description "<text>" --force`.
In a new repository owned by an organization, delete GitHub's default labels
that the issue types and these labels replace: `bug`, `duplicate`,
`enhancement`, `good first issue`, `help wanted`, `invalid`, and `wontfix`.
A personal account keeps `bug` and `enhancement` as its type labels and adds
`task`. When adopting, delete nothing unless the plan says so.

## 6. Rulesets

Create each with `gh api -X POST "repos/$repo/rulesets" --input -`. When one
of that name exists, update it with `-X PUT "repos/$repo/rulesets/<id>"`
(`gh api "repos/$repo/rulesets" --jq '.[] | select(.name == "<name>") | .id'`).
**Adopting,** a ruleset of that name, or another on `<branch>`, is merged, not
replaced: a PUT replaces the `rules` and `bypass_actors` arrays whole, so send
back every existing rule, parameter, and bypass actor, and add only the
missing rules. Where a parameter differs, keep the existing value unless the
plan changes it. `integration_id` 15368 is GitHub Actions, which reports both
checks. Actor 5 is
the repository's admin role, so the human can still act in an emergency.

```json
{
  "name": "<branch> branch",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [{ "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }],
  "conditions": { "ref_name": { "include": ["refs/heads/<branch>"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    {
      "type": "pull_request",
      "parameters": {
        "allowed_merge_methods": ["squash"],
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": true,
        "require_last_push_approval": false,
        "required_approving_review_count": 0,
        "required_review_thread_resolution": true
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "do_not_enforce_on_create": false,
        "strict_required_status_checks_policy": false,
        "required_status_checks": [
          { "context": "validation-outcome", "integration_id": 15368 },
          { "context": "pr-lint-title", "integration_id": 15368 }
        ]
      }
    },
    {
      "type": "merge_queue",
      "parameters": {
        "check_response_timeout_minutes": 60,
        "grouping_strategy": "ALLGREEN",
        "max_entries_to_build": 5,
        "max_entries_to_merge": 5,
        "merge_method": "SQUASH",
        "min_entries_to_merge": 1,
        "min_entries_to_merge_wait_minutes": 5
      }
    }
  ]
}
```

```json
{
  "name": "versioning tag",
  "target": "tag",
  "enforcement": "active",
  "bypass_actors": [{ "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }],
  "conditions": { "ref_name": { "include": ["refs/tags/v*"], "exclude": [] } },
  "rules": [{ "type": "update" }, { "type": "deletion" }, { "type": "non_fast_forward" }]
}
```

Leave out the tag ruleset when there are no releases. When adopting, a
required check exists only once the workflow that reports it is on the default
branch: apply the branch ruleset after the files' pull request merges, never
before, or that pull request can't merge.

## 7. Environments, issue types, and issue fields

**The `renovate` environment** (Renovate only), deployable from `<branch>`
alone:

```bash
gh api --silent -X PUT "repos/$repo/environments/renovate" --input - <<'EOF'
{"deployment_branch_policy": {"protected_branches": false, "custom_branch_policies": true}}
EOF
gh api --silent -X POST "repos/$repo/environments/renovate/deployment-branch-policies" \
  -f name=<branch> -f type=branch   # skip when the policy is already there
```

**Issue types** (organizations): `gh api orgs/<org>/issue-types` should list
Bug, Feature, and Task. Create any that are missing, when the plan says so,
with `gh api -X POST orgs/<org>/issue-types -f name=<name> -f color=<color>
-F is_enabled=true -f description=<text>`, using red for Bug, blue for
Feature, and yellow for Task.

**Issue fields** (organizations, when chosen), created only when
`gh api orgs/<org>/issue-fields` lacks them:

```bash
gh api -X POST "orgs/<org>/issue-fields" --input - <<'EOF'
{"name": "Priority", "description": "Current importance level assigned to this issue", "data_type": "single_select",
 "options": [{"name": "Urgent", "color": "pink", "priority": 1}, {"name": "High", "color": "red", "priority": 2},
             {"name": "Medium", "color": "yellow", "priority": 3}, {"name": "Low", "color": "green", "priority": 4}]}
EOF
gh api -X POST "orgs/<org>/issue-fields" --input - <<'EOF'
{"name": "Effort", "description": "Relative level of effort for completing this issue", "data_type": "single_select",
 "options": [{"name": "High", "color": "red", "priority": 1}, {"name": "Medium", "color": "yellow", "priority": 2},
             {"name": "Low", "color": "green", "priority": 3}]}
EOF
```

## 8. The Project

**Create and link** (new board):

```bash
gh project create --owner <owner> --title "<name>" --format json --jq .number
gh project link <number> --owner <owner> --repo <owner>/<repo>
gh project edit <number> --owner <owner> \
  --description "Work on <name>: issues, roadmap milestones and their status" --readme "<readme>"
```

**Adopting** an existing Project, link it to the repository if it isn't, and
add only what the audit found missing.

**Status:** the options are Todo, In Progress, Blocked by Human, In Review, and
Done. On a new board, replace the defaults with GraphQL `updateProjectV2Field`
(the field's id comes from `gh project field-list <number> --owner <owner>
--format json`). When adopting, pass every existing option with its `id`,
unchanged, and append only the missing ones.

```bash
gh api graphql -f id=<status-field-id> -f query='
  mutation($id: ID!) { updateProjectV2Field(input: {fieldId: $id, singleSelectOptions: [
    {name: "Todo", color: GRAY, description: "Not started"},
    {name: "In Progress", color: YELLOW, description: "Being worked on"},
    {name: "Blocked by Human", color: RED, description: "Waiting on the owner'"'"'s help, input, answer or action"},
    {name: "In Review", color: PURPLE, description: "A pull request is open"},
    {name: "Done", color: GREEN, description: "Merged, or accepted"}]}) { projectV2Field { ... on ProjectV2SingleSelectField { id } } } }'
```

**Priority and Effort:** an organization's issue fields go on the board with
`gh api -X POST orgs/<org>/projectsV2/<number>/fields -F issue_field_id=<id>`.
Otherwise create Project fields: `gh project field-create <number> --owner
<owner> --name Priority --data-type SINGLE_SELECT --single-select-options
"Urgent,High,Medium,Low"`, and Effort with "High,Medium,Low".

**Area:** a single-select field with one option per area label, plus Other
(`CI,Config,Infra,Documentation,<the project's own>,Other`).

**Views:** create them through REST, with field ids from
`gh api orgs/<org>/projectsV2/<number>/fields --jq '.[] | {id, name}'`. A
personal account uses `users/<login>/projectsV2/<number>/fields`, and for
views `users/<user-id>/projectsV2/<number>/views`, where the user id is
`gh api user --jq .id`. Then delete the board's default "View 1" with GraphQL
`deleteProjectV2View`.

| View | Layout | Filter | Group (board: columns) | Sort | Visible fields |
|---|---|---|---|---|---|
| Board | board | `-closed:<@today-7d` | Status | Priority asc | Title, Linked pull requests, Milestone, Area, Priority |
| By milestone | table | `is:open` | Milestone | Priority asc | Title, Status, Milestone, Area, Priority, Effort |
| Priorities | table | `is:open` | Priority | Priority asc | Title, Status, Linked pull requests, Milestone, Area, Priority, Effort |
| By area | table | `is:open` | Area | Priority asc | Title, Status, Milestone, Area, Priority, Effort |

```bash
gh api -X POST "orgs/<org>/projectsV2/<number>/views" --input - <<'EOF'
{"name": "Board", "layout": "board", "filter": "-closed:<@today-7d",
 "vertical_group_by": [<status-id>], "sort_by": [[<priority-id>, "asc"]],
 "visible_fields": [<title-id>, <linked-prs-id>, <milestone-id>, <area-id>, <priority-id>]}
EOF
```

Table views use `group_by` instead of `vertical_group_by`. **Every view sorts
by Priority, ascending,** so the most urgent work comes first. Read each view
back (GraphQL `views { name sortByFields }`) to confirm it took. When
adopting, add the views missing by name, and offer to add the Priority sort to
existing views that have no sort.

**README:**

```markdown
Tracks the work on <name> (<owner>/<repo>): the open issues and the recently closed ones.

**Fields**

- **Status:** Todo, In Progress, Blocked by Human (waiting on the owner's help, input, answer or action), In Review (a pull request is open), Done.
- **Priority:** Urgent blocks the current milestone or is broken; High is next up; Medium is planned; Low is someday.
- **Effort:** Low is up to a day, Medium a day to a few days, High a week or more (CONTRIBUTING.md, Triaging Issues).
- **Area:** taken from the issue's area label (<the areas>), or Other.
- **Type:** the issue type: Bug, Feature or Task (a personal account: the bug, enhancement and task labels).

**Milestones** follow the roadmap.
```

Say where Priority and Effort are set: on the issue for an organization's
fields, or on the board for Project fields.

## 9. What needs the browser or the human

Give each its link; in the browser, the human signs in and approves.

1. **The board's workflows**, at `https://github.com/orgs/<org>/projects/<number>/workflows`
   (`users/<login>` for a personal account). The API can't turn them on, so
   this step is never skipped: every new board needs it, and an adopted one
   needs whatever the audit found off. Open each one, choose **Edit**, set it,
   and switch it **On**:
   - **Auto-add sub-issues to project:** on.
   - **Auto-add to project:** on, for `<owner>/<repo>`, with the filter `is:issue,pr is:open`.
   - **Auto-archive items:** on, with its default filter.
   - **Auto-close issue:** on, closing an issue when its Status is set to Done.
   - **Item added to project:** Status Todo.
   - **Item closed:** Status Done.
   - **Item reopened:** Status Todo.
   - **Pull request linked to issue:** Status In Review.
   - **Pull request merged:** Status Done.
   - **Code changes requested** and **Code review approved:** off, since
     Status follows the ticket's phase (`github.md`, section 9), not each
     review.

   Afterwards, read them back (GraphQL `workflows { name enabled }`) and
   confirm those nine are enabled. In the same visit, open each view's
   **View** menu: check that it sorts by Priority, and turn **Show
   hierarchy** on, so sub-issues sit under their parents. The API doesn't
   set that toggle.
2. **The release App** (releases only). Reuse the owner's release App if it has
   one, adding the repository to its installation. Otherwise create one at
   `https://github.com/organizations/<org>/settings/apps/new`
   (`https://github.com/settings/apps/new` for a personal account), with:
   - no webhook, installable only on this account;
   - Contents, Issues, and Pull requests read and write, and Metadata read.

   Install it on the repository alone. Then set
   `RELEASE_APP_CLIENT_ID` with `gh secret set RELEASE_APP_CLIENT_ID -R $repo
   --body <client id>`. The human generates the private key and runs
   `! gh secret set RELEASE_APP_PRIVATE_KEY -R $repo < <key>.pem`, then deletes
   the file.
3. **The Renovate App** (Renovate only), a second App kept apart from the
   release one, created the same way, with:
   - Contents, Pull requests, Issues, Workflows, and Commit statuses read and
     write, and Metadata read.

   Its secrets, `RENOVATE_APP_CLIENT_ID` and `RENOVATE_APP_PRIVATE_KEY`, go in
   the `renovate` environment (`--env renovate`). A repository on the
   environment fallback (section 1) uses repository secrets.
4. **Anything GitHub refused** that a settings page or plan change fixes, such
   as GitHub Secret Protection for a private repository. Billing is always the
   human's decision.
5. **An organization or account to create** (`SKILL.md`, section 1).

## 10. Audit (adopt)

Read, change nothing, and record each item as in line, missing, or different:

- **Repository:** every key section 3 sets, and the security settings:
  `gh api "repos/$repo" --jq '{visibility, default_branch, license: .license.spdx_id, allow_squash_merge, allow_merge_commit, allow_rebase_merge, squash_merge_commit_title, squash_merge_commit_message, allow_auto_merge, allow_update_branch, delete_branch_on_merge, has_issues, has_projects, has_wiki, has_discussions, security_and_analysis}'`;
  `gh api "repos/$repo/actions/permissions/workflow"`.
- **Protections:** `gh api "repos/$repo/rulesets"` (with each ruleset's
  details), and classic branch protection
  (`gh api "repos/$repo/branches/<default>/protection"`; a 404 means none).
- **Files:** each file in `scaffold.md` and `workflows.md`, by path and by
  purpose. A repository with its own CI, a `dependabot.yml`, or another
  release tool has made a choice. Its checks keep their names, and the
  ruleset requires those.
- **Tickets:** labels (`gh label list`), issue types and fields
  (organizations), issue forms, milestones, and the open issues: how many lack
  a type, Priority, Effort, area label, or Project item.
- **Project:** the linked Projects (`repo-profile.md`, section 1), or the one
  named: its fields and options (`gh project field-list`), its views and
  workflows (GraphQL `views` and `workflows` on the `projectV2`), its linked
  repositories, and its README.

**SDLC tickets work** when every issue can carry a type, a Priority, an Effort,
and an area label; the Project shows those, and has a Status option for each
phase (`github.md`, section 9, mapped by meaning); and its workflows don't
fight those phases. Everything else in the defaults is a recommendation.
