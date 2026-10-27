---
type: llm
---

PASS if the plan caps the agents running at once at 6, or derives the cap from CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS divided by one plus the reviewers per round, and queues the remaining work until running agents return.
FAIL if the plan runs all 20 tickets at once, gives no cap on agents running at once, or states a cap above 6 without tying it to a raised CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS.
