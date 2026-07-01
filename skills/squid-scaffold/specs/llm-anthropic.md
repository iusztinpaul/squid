---
name: llm-anthropic
description: Claude API usage via `anthropic` SDK — model selection, prompt caching, tool use, extended thinking. TRIGGER when the project calls Claude. SKIP for other LLM providers.
---

# Claude (Anthropic API)

> **Stub — not yet written.** Flesh out as usage patterns reveal opinions worth capturing.

If the Claude Code session has a `claude-api` skill available, defer to that for working code patterns; this spec captures project-level conventions only.

## When to use

- Project calls the Anthropic API directly (not via a proxy / router).

## When NOT to use

- Project uses OpenAI / Gemini / other providers — see sibling specs.
- Project uses a router like LiteLLM — document that at the project level, not here.

## Canonical principles

TODO
