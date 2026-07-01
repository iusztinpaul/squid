---
name: datastore-redis
description: Redis as cache / queue / ephemeral store — key naming, TTL discipline, `redis.asyncio` client, `redis-cli` for local dev. TRIGGER when using Redis. SKIP for durable-primary-store use cases.
---

# Redis

> **Stub — not yet written.** Flesh out as usage patterns reveal opinions worth capturing.

## When to use

- Project uses Redis as cache, queue, or ephemeral store.
- Often pairs with a primary datastore (`datastore-mongodb.md` / `datastore-postgresql.md`).

## When NOT to use

- Project needs durable primary storage — Redis persistence trade-offs are not free.

## Canonical principles

TODO
