---
description: A green PR behind develop goes into the merge queue as it is, without develop merged in first.
tags: [protocol]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

CTO, PR #42 for ticket #41 has green checks and its review converged. GitHub
says the branch is 6 commits behind develop, with no conflicts. develop merges
through a merge queue. Get it merged.
