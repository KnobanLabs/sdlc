# Repo profile

`~/.sdlc/<owner>/<repo>/profile.md`: the org's shared facts about a repo, read
by every role. Owned by the Architect (a conductor without one writes sections 1
to 4 and flags the rest). Record the commit SHA it reflects; refresh sections
when the stack, CI, docs tooling, or repo skills change.

1. **Identity:** `owner/repo`, host, default branch; `gh` installed,
   authenticated, and its version (2.94.0+ for sub-issues, 2.99.0+ for
   `--attach`; Enterprise Server has no uploads); ownership result and matching
   rule (`approvals.md`); milestones in use; and the related GitHub Project
   (owner, number, title, fields and their options, built-in workflows, which
   one if several are linked, and whether `gh` has the `project` scope).
   - **Finding the Project:** those linked to the repo
     (`gh api graphql -f query='query($o:String!,$r:String!){repository(owner:$o,name:$r){projectsV2(first:20){nodes{number title closed owner{...on Organization{login} ...on User{login}}}}}}' -F o=<owner> -F r=<repo>`),
     otherwise the owner's Projects that already hold its issues
     (`gh issue list --state all --limit 50 --json number,projectItems`).
     Ignore closed ones. If several qualify and the repo doesn't make the main
     one clear, ask. If none do, work without one; never create a Project
     unless the human asks.
   - **Access:** `gh project` needs the `project` scope. If it's missing, ask
     the human to run `gh auth refresh -s project` (never change credentials
     yourself) and work without the Project meanwhile.
2. **Stack and commands:** languages, frameworks, package managers, versions;
   exact install, build, test (full and focused), lint, format, type-check, and
   run commands; test frameworks and locations.
3. **CI and protections:** workflows, required checks, branch protection or
   rulesets.
4. **Conventions:** branch names, commit and PR title style (Conventional Commits
   unless the repo uses another), issue types and fields in use, PR and issue
   templates, labels, style configs,
   CODEOWNERS, `CONTRIBUTING.md` rules, and any guidance on showing UI changes in
   PRs (overrides the screenshot default).
5. **Repo skills and guidance:** each skill and guidance file (name, purpose,
   path); for external repos, the human's decision per skill and when; standing
   order conflicts and their resolution.
6. **Docs system:** tooling (markdown, Docusaurus, MkDocs, Sphinx, VitePress,
   Starlight, wiki, none), location, format, frontmatter, navigation
   registration, link style, build command (strict if available), whether and
   where published, existing ADR convention, and where ADRs, standards, and the
   architecture overview live. Defaults with no docs system: `docs/adr/NNNN-title.md`,
   `docs/standards.md`, `docs/architecture/`.
7. **Runtime:** ports, databases, containers, compose files, queues, and external
   services; untracked files needed (for `.worktreeinclude`); how to override
   ports and database names.
8. **UI:** whether there is one and how to start it; supported viewports
   (default mobile, tablet, desktop); available browser MCP tools; test accounts
   (names only).
9. **Releases and environments:** version scheme and location; release mechanism
   (tags, workflows, registries); environments and which count as **deployed**
   (beyond local and human-designated dev); readable logs and monitoring.
10. **Security tooling:** available scanners and audits, those in CI, and whether
    private advisories are used.
11. **Data sources:** each source, its read-only access method, whether it holds
    personal data, and the human's approval for agents to query it.
12. **Creative tooling:** video (Remotion, ffmpeg, recording, text-to-speech),
    image and font tools present, and tools approved for install.
13. **Legal and compliance:** the repo's license, LICENSE and NOTICE files,
    contributor terms (CLA or DCO), privacy policy and terms locations,
    distribution model (shipped binaries, packages, hosted service, mobile apps),
    where users are, license scanners available, and pointers into `legal/`.
14. **Pointers:** `exploration-log.md`; jobs with delivered, unaccepted tasks.
