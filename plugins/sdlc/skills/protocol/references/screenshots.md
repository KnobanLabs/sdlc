# Before and after screenshots

When a PR changes anything a user can see, its description gets a BEFORE/AFTER
screenshot table, unless the repo's PR template, contribution guide, repo skills,
or guidance files say otherwise; repo guidance overrides this default.

**Capture** with an available screenshot-capable MCP tool (Chrome DevTools or
another browser MCP):

1. Run the PR's base in a temporary worktree and the branch in yours, on separate
   slot ports, with the same seed data and test account. Record both in the ledger.
2. Capture each affected screen and state at each supported viewport, with
   identical URL, scroll, data, and theme. Let pages settle; freeze timestamps,
   animations, and random content.
3. Save as `jobs/<job-id>/evidence/<screen>-<viewport>-before.png` (and `-after`).
4. **Check every image before upload; uploads can't be undone.** No secrets,
   tokens, real personal data, or anything outside the app.

**Attach** with `gh` v2.99.0+: reference each image by local path in the body
and pass the same path to `--attach`; gh uploads it and swaps in the URL.
Images max 10 MB.

```markdown
| Screen | Viewport | Before | After |
|---|---|---|---|
| Settings | Mobile | ![Settings, mobile, before](/abs/evidence/settings-mobile-before.png) | ![Settings, mobile, after](/abs/evidence/settings-mobile-after.png) |
```

```
gh pr create --draft --title "..." --body-file body.md \
  --attach /abs/evidence/settings-mobile-before.png \
  --attach /abs/evidence/settings-mobile-after.png
```

Use "New screen" or "Removed" for cells with no image. Show only what changed.

**If it can't be done** (no screenshot tool, `gh` older than 2.99.0, a token that
can't upload, which needs `gh auth login`'s OAuth token or a classic PAT, or an
Enterprise Server host), ask the human how to proceed or whether to skip.
Upgrading `gh` needs approval. Meanwhile, open the PR without the table and add
images later with `gh pr edit --attach` if wanted.

