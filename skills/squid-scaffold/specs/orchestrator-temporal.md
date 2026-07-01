---
name: orchestrator-temporal
description: Temporal as the project's orchestrator — workflows, activities, worker lifecycle, `temporal` CLI. TRIGGER when using Temporal. SKIP for other orchestrators.
---

# Temporal

> **Stub — not yet written.** Flesh out as usage patterns reveal opinions worth capturing.

See [`python-backend`](../python-backend/SKILL.md#pipelines-serving-and-triggering-orchestrator-ergonomics) for the generic serve-worker-in-background + trigger-via-make pattern this spec specialises.

## When to use

- Project needs durable, long-running workflows with explicit activity / retry semantics.

## When NOT to use

- Project uses Prefect / Dagster / Airflow — see sibling specs.
- Short-lived batch jobs where Temporal's overhead isn't justified.

## Canonical principles

TODO
