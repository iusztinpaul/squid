---
name: orchestrator-dagster
description: Dagster as the project's orchestrator — assets vs jobs, materialisations, `dagster job execute`, streaming logs via `make run-<pipeline>` wrappers. TRIGGER when using Dagster. SKIP for other orchestrators.
---

# Dagster

> **Stub — not yet written.** Flesh out as usage patterns reveal opinions worth capturing.

See [`python-backend`](../python-backend/SKILL.md#pipelines-serving-and-triggering-orchestrator-ergonomics) for the generic serve-worker-in-background + trigger-via-make pattern this spec specialises.

## When to use

- Project's pipelines are modelled as Dagster assets / jobs.

## When NOT to use

- Project uses Prefect / Temporal / Airflow — see sibling specs.

## Canonical principles

TODO
