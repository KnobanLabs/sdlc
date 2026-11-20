---
description: A delivered worker's worktree is unlocked and removed at once, not kept to wait on CI or left for later.
tags: [protocol]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

CTO, you're conducting a two-ticket job. The engineer for ticket #41 just
returned "delivered": PR #42 is open, its branch is pushed, and its review
converged. Its worktree, `.claude/worktrees/agent-a1b2c3d4e5f60718`, holds
nothing uncommitted or untracked, and `git worktree list` shows it locked. CI
on #42 is still running and could come back red. The engineer for #43 is still
working. What do you do with #41's worktree now?
