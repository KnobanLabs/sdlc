# Security Policy

## Supported Versions

Only the latest release receives security fixes. Claude Code updates an
installed plugin when its version changes, so a fix reaches users through a new
release.

## Reporting a Vulnerability

**Do not open a GitHub issue for security vulnerabilities.** Report them
privately through GitHub's
[private vulnerability reporting](https://github.com/KnobanLabs/sdlc/security/advisories/new)
(the repository's **Security** tab, **Report a vulnerability**).

Include as much detail as possible:

- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept, such as the prompt, repository
  content or issue text that leads an agent astray
- The plugin version (`claude plugin details sdlc`) and Claude Code version
  (`claude --version`)
- Any suggested mitigations

You can expect an acknowledgement within 72 hours and a resolution timeline
within 14 days for confirmed issues.

## Patching

A critical advisory in a dependency is patched within 72 hours of reaching the
maintainer. Dependabot alerts report each one, and its security update pull
requests carry the fix where one is published.

## Secrets

Secret scanning and push protection are on for the repository, and the
pre-commit hook and CI scan every change with Trivy (`CONTRIBUTING.md`, _Secret
scan before each commit_). A secret that reaches a commit is treated as leaked:
revoke and replace it first, then remove it from the history.

## Threat Model

The plugin is instructions only: Markdown skills and agent definitions that
Claude Code loads into a user's sessions. It ships no hooks, MCP servers or
executables, and stores nothing of its own beyond the files its agents write in
`~/.sdlc/`. Its agents run inside the user's Claude Code, with that session's
permission settings, and act through the user's own `git` and `gh`
credentials. They read untrusted text as part of their work — repository
files, issues, pull requests, comments and web pages.

Its approval rules (what waits for the user, what an agent may write and
where) are enforced by those instructions, not by hooks; the plugin README's
_Known gaps_ says so. Claude Code's own permission prompts and settings stay the
user's enforced boundary.

### In scope

- Plugin instructions that lead an agent to act beyond its stated approvals:
  writing outside the user's own repositories, running destructive or
  irreversible operations without asking, or posting on the user's behalf
- Plugin instructions that lead an agent to disclose secrets, credentials or
  private data, such as into an issue, a pull request or a commit
- Content in a repository, issue or web page that the plugin's instructions
  make an agent follow as if it were the user's request (prompt injection the
  instructions should guard against)
- This repository's workflows, release process and marketplace catalog, such as
  a way to get unreviewed content into a release or into what `/plugin install`
  fetches

### Out of scope (by design)

- Vulnerabilities in Claude Code itself, or in the model's behavior apart from
  what these instructions ask of it: report those to Anthropic
- Anything a user's own Claude Code permission settings allow, such as
  auto-approved commands
- Unpatched copies: a user who hasn't updated to the latest release
