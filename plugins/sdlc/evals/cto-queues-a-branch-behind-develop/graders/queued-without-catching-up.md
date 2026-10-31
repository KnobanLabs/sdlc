---
type: llm
weight: 2
---

The reply may be unable to run commands; judge what it does or plans to do with #42, not whether it got there.
PASS if it queues #42 as it is, or plans to (for example with `gh pr merge 42`), and says not to bring develop into the branch first because the queue tests it on the latest develop.
FAIL if it merges or rebases develop into #42's branch, updates the branch, or plans to do any of these before queueing it.
