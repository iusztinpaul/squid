# Index of specs

Each file is a standalone reference doc describing *opinions*, not *code*. Grouped by role:

**Layout & tooling (foundational)**
- [`monorepo-layout.md`](monorepo-layout.md) — polyglot monorepo tree + component boundaries.
- [`makefile-delegator.md`](makefile-delegator.md) — root Makefile pattern + canonical example.

**Python**
- [`python-backend.md`](python-backend.md) — layout, discipline, testing conventions.
- [`uv-python.md`](uv-python.md) — uv usage (add / sync / run / build / publish).
- [`pyproject.md`](pyproject.md) — `pyproject.toml` structure + canonical example.
- [`ruff-python.md`](ruff-python.md) — ruff configuration opinions.

**Python project types**
- [`fastapi-service.md`](fastapi-service.md) — FastAPI app factory, lifespan, endpoints.
- [`fastmcp-server.md`](fastmcp-server.md) — FastMCP server shape.
- [`cli-tool-python.md`](cli-tool-python.md) — typer/click CLI conventions.

**TypeScript frontend**
- [`typescript-frontend.md`](typescript-frontend.md) — package layout + canonical configs.
- [`react-app.md`](react-app.md) — React SPA specifics.
- [`vue-app.md`](vue-app.md) — Vue SPA specifics.
- [`svelte-app.md`](svelte-app.md) — Svelte SPA specifics.
- [`vanilla-ts-app.md`](vanilla-ts-app.md) — no-framework TypeScript SPA.

**Go TUI**
- [`go-tui.md`](go-tui.md) — layout + framework decision tree; loads one of [`go-tui-bubbletea.md`](go-tui-bubbletea.md) / [`go-tui-tview.md`](go-tui-tview.md) on demand.

**Infrastructure**
- [`docker.md`](docker.md) — slim Dockerfile + docker-compose opinions.
- [`github-actions.md`](github-actions.md) — monorepo CI patterns.
- [`openapi-contracts.md`](openapi-contracts.md) — contract-first OpenAPI 3.1 workflow.
- [`pre-commit-hooks.md`](pre-commit-hooks.md) — project-side hook conventions (`pre-commit` / `lefthook` / `husky`), what runs in `pre-commit` vs `pre-push`, escape-hatch policy.

**Process & documentation**
- [`tracker-workflow.md`](tracker-workflow.md) — file-based task tracker format.
- [`adr.md`](adr.md) — Architecture Decision Records (`docs/adr/NNNN-title.md`), Nygard template, status lifecycle.
- [`ubiquitous-language.md`](ubiquitous-language.md) — project glossary at `docs/glossary.md`; one canonical name per domain concept.

**External services** *(all stubs — flesh out as real projects reveal opinions; delete any category or file you decide isn't worth maintaining, and drop the matching row in `../SKILL.md` Step 2's decision table)*
- Datastore: [`datastore-mongodb.md`](datastore-mongodb.md), [`datastore-postgresql.md`](datastore-postgresql.md), [`datastore-redis.md`](datastore-redis.md), [`datastore-sqlite.md`](datastore-sqlite.md).
- Orchestrator: [`orchestrator-prefect.md`](orchestrator-prefect.md), [`orchestrator-dagster.md`](orchestrator-dagster.md), [`orchestrator-temporal.md`](orchestrator-temporal.md).
- Observability: [`observability-opik.md`](observability-opik.md), [`observability-opentelemetry.md`](observability-opentelemetry.md), [`observability-sentry.md`](observability-sentry.md).
- LLM API: [`llm-anthropic.md`](llm-anthropic.md), [`llm-openai.md`](llm-openai.md), [`llm-gemini.md`](llm-gemini.md).
- Embeddings: [`embeddings-voyageai.md`](embeddings-voyageai.md), [`embeddings-openai.md`](embeddings-openai.md), [`embeddings-sentence-transformers.md`](embeddings-sentence-transformers.md).
- Model serving: [`model-serving-modal.md`](model-serving-modal.md), [`model-serving-replicate.md`](model-serving-replicate.md).
- Scraping: [`scraping-firecrawl.md`](scraping-firecrawl.md), [`scraping-playwright.md`](scraping-playwright.md), [`scraping-requests-bs4.md`](scraping-requests-bs4.md).
