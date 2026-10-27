---
description: A stack trace to diagnose routes to the Engineer.
tags: [routing, smoke]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

This started showing up in production after yesterday's deploy. What's wrong and can you fix it?

```
TypeError: Cannot read properties of undefined (reading 'rating')
    at formatLobbyRow (src/lobby/format.ts:41:28)
    at renderLobby (src/lobby/render.ts:17:15)
```
