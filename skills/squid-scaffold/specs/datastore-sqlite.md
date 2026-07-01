---
name: datastore-sqlite
description: SQLite as the project's datastore — WAL mode, single-writer reality, when to use vs Postgres, `sqlite3` CLI. TRIGGER for small / embedded / single-node projects. SKIP for multi-writer / high-concurrency workloads.
---

# SQLite

> **Stub — not yet written.** Flesh out as usage patterns reveal opinions worth capturing.

## When to use

- Single-node apps, CLI tools, local-first or embedded data.
- Projects where a managed Postgres feels like overkill.

## When NOT to use

- Multi-writer / high-concurrency workloads — see `datastore-postgresql.md`.
- Document modelling — see `datastore-mongodb.md`.

## Canonical principles

TODO
