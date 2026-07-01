---
name: observability-opentelemetry
description: OpenTelemetry for observability — OTLP exporter, span attributes, automatic instrumentation, trace/metric/log split. TRIGGER when using OTel. SKIP for LLM-specific or error-tracking-only stacks.
---

# OpenTelemetry

> **Stub — not yet written.** Flesh out as usage patterns reveal opinions worth capturing.

## When to use

- General-purpose distributed tracing / metrics / logs to a vendor-neutral backend (Grafana, Honeycomb, Datadog, etc.).

## When NOT to use

- LLM-specific evals — see `observability-opik.md`.
- Error tracking only — see `observability-sentry.md`.

## Canonical principles

TODO
