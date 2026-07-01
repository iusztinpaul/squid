---
name: orchestrator-prefect
description: Prefect as the project's orchestrator — deployments, workers, `uv run prefect deployment run`, streaming logs via `make run-<pipeline>` wrappers. TRIGGER when using Prefect. SKIP for other orchestrators.
---

# Prefect

> **Stub — not yet written.** Flesh out as usage patterns reveal opinions worth capturing.

See [`python-backend`](../python-backend/SKILL.md#pipelines-serving-and-triggering-orchestrator-ergonomics) for the generic serve-worker-in-background + trigger-via-make pattern this spec specialises.

## When to use

- Project's batch / streaming pipelines are orchestrated by Prefect.

## When NOT to use

- Project uses Dagster / Temporal / Airflow — see sibling specs.
- Project has no pipelines at all.

## Canonical principles

TODO
