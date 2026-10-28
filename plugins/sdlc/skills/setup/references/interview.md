# Setup interview

The defaults, then the questions in the order to ask them. **Asked** questions
go to the human, each with its recommended option first. **Plan** items aren't
asked: they appear in the plan with their value, and the human can change
any of them there. A recommendation follows the default unless an earlier
answer points away from it. When it does, say why in one line.

**Adopting** an existing repository or Project, the audit (`github-setup.md`,
section 10) settles most of these. Where it finds a different choice (another
license, `main`, Dependabot, its own Status options), the recommendation is to
keep it, and the question becomes whether to change it. Owner, name,
visibility, and license are never changed by this command: say so, and point
to the right role (IP Counsel for a license).

## Defaults

| Area | Default |
|---|---|
| Owner | An organization for a company; the personal account for an individual |
| Visibility | Private |
| Default branch | `develop` |
| License | Proprietary, all rights reserved |
| Copyright header | Every config, workflow, and script file that takes comments |
| Contributions | By invitation |
| Merges | Squash only, titled by the pull request; auto-merge, update branch, and merged branches deleted; the merge queue |
| Protections | A `develop` ruleset: no deletion or force push, linear history, pull requests with code-owner review and resolved threads, the `validation-outcome` and `pr-lint-title` checks, and the merge queue. A `v*` tag ruleset: no update or deletion |
| CI | Validate Branch (a Trivy secret scan, actionlint, zizmor, and shellcheck), PR Preparation (title lint, labels from paths), and Merge Queue |
| Releases | release-please, run as a release GitHub App, from Conventional Commits; the version starts at 0.0.0, and the first release is 0.1.0 |
| Dependencies | Renovate, run as a Renovate GitHub App, weekly in a Monday window, with every update waiting 7 days; Dependabot alerts and security updates |
| Security | Reports privately to the maintainer's GitHub profile; acknowledged in 72 hours, with a timeline in 14 days; secret scanning and push protection; a pre-commit Trivy hook |
| Tracking | A GitHub Project with Status, Priority, Effort, Area, and Type; Board, By milestone, Priorities, and By area views; Bug, Feature, and Task issue forms; a daily triage check |
| Agents | `AGENTS.md` as the canonical instructions, with `CLAUDE.md` and Copilot's instructions deferring to it; `.agents/skills/`; the Chrome DevTools MCP server |
| Editor | `.editorconfig`, `.gitattributes`, `.gitignore`, and shared VS Code settings |
| Docs | Architecture decision records in `docs/adr/` |

## 1. Who and where

1. **Asked: "Are you an individual or a company?"** Recommend Company when
   `gh api user/orgs` lists an organization, and Individual otherwise.
   - **Company:** ask for its legal name as copyright notices should show it
     (such as "Example LLC"); it is the copyright holder. The repository goes
     in an organization. Organizations have issue types and fields; personal
     accounts don't (`github-setup.md`, section 1).
   - **Individual:** the holder is their full name, from `git config user.name`
     or `gh api user --jq .name`; confirm it.
2. **Asked, for a company: "Which organization should own it?"** List the
   organizations where they can create repositories. Recommend the one that
   matches the company's name. If there is none, recommend creating one
   (https://github.com/account/organizations/new; the free plan is fine) and
   offer the personal account for now.
3. **Asked: "What's the project called?"** Recommend a name from the brief. The
   repository name is its kebab-case form; check that it's free with
   `gh repo view <owner>/<name>`, where a not-found error means it's free.
4. **Asked: "Should the repository be private or public?"** Recommend Private
   unless the brief says open source.
   - **Public:** the license recommendation turns to open source (2), and
     contributions (3) are asked. GitHub's private vulnerability reporting and
     secret scanning become available, and protections work on every plan.
     `AUTHORS` leaves out email addresses.
   - **Private on a free plan:** rulesets and environments aren't available
     (`github-setup.md`, section 1). Say so, and recommend upgrading (GitHub
     Pro or Team), making it public, or going on without enforced
     protections. Without them, agents still follow the conventions.
5. **Plan:** the description is the brief's pitch, in one line. The default branch is
   `develop`; `main` is the common alternative.

## 2. License

**Asked: "What license do you want for this repository?"** Say it's
informational, not legal advice, and that IP Counsel (`/sdlc:ip`) can weigh
the options in depth.

| Visibility | Options, recommended first |
|---|---|
| Private | Proprietary, all rights reserved; MIT; Apache-2.0 |
| Public | MIT (simplest permissive); Apache-2.0 (permissive, with a patent grant companies often want); GPL-3.0, or AGPL-3.0 for a hosted service (changes must be shared alike); Proprietary (the source is visible, but no rights are granted) |

- **Proprietary:** `LICENSE` holds the all-rights-reserved text
  (`scaffold.md`), and the copyright header ends "All rights reserved."
- **Open source:** the text comes from `gh api licenses/<key> --jq .body`, with
  the year and the holder filled in. The header carries an
  `SPDX-License-Identifier` line, and the README's License section names the
  license.

## 3. Contributions (public only)

**Asked: "Who can contribute?"** Recommend Anyone, through pull requests.

- **Anyone:** `CONTRIBUTING.md` welcomes contributions, and the Code of
  Conduct's contact is the security contact (4). Contributor terms
  (a CLA or DCO) are left out unless the human asks for them; IP Counsel can
  advise.
- **By invitation:** the default text. Anyone can still fork a public
  repository; only pull requests are by invitation.

## 4. Security

1. **Asked: "How should security defects be reported?"**
   - **Public:** GitHub's private vulnerability reporting (recommended, because
     reports stay private in the Security tab), a security email address, or
     the maintainer's GitHub profile.
   - **Private:** the maintainer's GitHub profile (recommended; private
     reporting needs a public repository), or a security email address.

   The answer fills `SECURITY.md` (Reporting a Vulnerability), the issue
   forms' security contact link, and the Code of Conduct's contact. Private
   reporting is turned on only when it's chosen.
2. **Plan:** acknowledgement in 72 hours and a timeline in 14 days; only the
   latest release is supported; secret scanning and push protection; the
   pre-commit hook. When `docker info` fails, say the hook needs Docker, and
   that CI still scans every push.

## 5. Automation

1. **Asked: "Do you want Renovate or Dependabot to keep dependencies up to
   date?"** Explain each in a line:
   - **Renovate** (the default): one weekly batch of grouped updates, each
     held 7 days after its release, covering every ecosystem and the images CI
     runs. It needs a GitHub App, created once, and two secrets; the browser
     can do most of that.
   - **Dependabot:** built into GitHub, with no App and no secrets, but with
     fewer options; images pinned inside workflows aren't updated.
   - **Neither:** only security alerts and fixes.

   Recommend Renovate for a company. Recommend Dependabot for an individual,
   or for anyone who says they aren't technical, since nothing needs setting
   up. Dependabot alerts and security updates are on in every case.
2. **Asked: "Do you want automatic versioned releases with a changelog?"**
   Recommend Yes: release-please opens a release pull request, and merging it
   tags the release and publishes it. It needs a release GitHub App, created
   once. Until its secrets are set, the workflow passes and does nothing. **No**
   leaves out the release-please files and the release sections of the docs.
3. **Plan:** the merge queue where the owner's plan allows it; otherwise
   auto-merge with the same checks (`github-setup.md`, section 1). Code owners:
   the human's login. Coding agents: Claude Code and GitHub Copilot, with
   `AGENTS.md` serving any other agent too. The Chrome DevTools MCP server only
   when the brief has a user interface. The `.gitignore` additions follow the
   brief's stack, if known.

## 6. Tracking

1. **Asked: "Do you want a GitHub Project board to track the work?"** Recommend
   a new board. The alternatives are an existing Project (list the owner's open
   ones) or no board. Without a board, tickets still carry their type,
   labels, and milestone.
2. **Asked, for an organization without `Priority` and `Effort` issue fields
   (`gh api orgs/<org>/issue-fields`):** "Create them for the organization?"
   Recommend Yes when the human is an organization owner: they then appear on
   every repository's issues there. It needs the `admin:org` scope
   (`SKILL.md`, section 1). The alternative is Project fields for this
   board alone. A personal account always uses Project fields.
3. **Plan:** the areas: `ci`, `config`, `documentation`, and `infra`, plus the
   project's own from the brief (such as `frontend`, `backend`, `mobile`, or
   `api`). The Project's name is the project's name.

## Team

Recommend, from the brief, which roles seed the backlog (`SKILL.md`, section
7). The CPO, PM, and Architect always take part. Ask once, with one
multiSelect option per tree: Product and Technology always recommended,
Marketing and Legal when their rows below apply. Then name the roles the plan
uses within each chosen tree.

| Role | Recommend when the brief has |
|---|---|
| Product Designer | A user interface |
| Data Analyst | Success metrics, or analytics |
| Security Engineer | Accounts, payments, personal data, uploads, or a service on the internet |
| Release Engineer | Something to deploy, publish, or ship to a store |
| QA | Behavior users depend on, or a deadline |
| CMO, with the Brand Designer, Content Writer, and Community Manager as the plan needs them | Users to reach: a launch, a brand, or a community |
| CLO, with Privacy Counsel, Compliance Officer, and IP Counsel as the plan needs them | Personal data (Privacy); children, health, payments, accessibility law, or app stores (Compliance); a name to clear, or third-party assets (IP) |
