---
description: A plainly worded bug fix routes to the Engineer, which loads the protocol first.
tags: [routing, smoke]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Fix the off-by-one in the pagination helper: page 2 repeats the last item of page 1. It's issue #57 in this repo.
