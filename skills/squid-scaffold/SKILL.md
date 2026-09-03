---
name: squid-scaffold
description: >-
  Bootstrap a new repo or component from the opinionated spec library (mode=create), or audit an
  existing scaffolded repo for drift against the scaffold rules (mode=evaluate, report-only).
disable-model-invocation: true
argument-hint: "[mode=create|evaluate] [project description | target repo path]"
---

# Scaffold

Interactive bootstrap for a new repo (or a new component in an existing one): read only the specs under [`specs/`](specs/) that apply, distil them into a tailored `AGENTS.md`, lay down an empty skeleton, hand back.

## Modes

`$ARGUMENTS` may lead with `mode=create` (default) or `mode=evaluate`:

- **`mode=create`** (default) — bootstrap a repo / component. The flow in "## Flow" below.
- **`mode=evaluate`** — audit an *existing* scaffolded repo for drift (report-only). For `mode=evaluate`, read [`evaluate.md`](evaluate.md) and follow E1–E4 instead of the Flow.

Every rule both modes honour lives in [`rules.md`](rules.md) — the single source of truth; `mode=create` follows every `P#` + `I#` while composing, `mode=evaluate` audits the `I#`. Do **not** restate any rule in this file.

## When to use

- Bootstrapping a brand-new repo.
- Adding a new runtime component (backend / frontend-web / frontend-tui) to an existing scaffolded repo.
- Re-generating the root `AGENTS.md` after a major stack change (e.g. swapping Vue for React).

## When NOT to use

- Authoring application source or business logic (`P1`).
- Adjusting opinions inside an existing project — edit the generated `AGENTS.md` directly.
- Non-polyglot single-package projects where the full machinery is overkill. (You can still use a single spec as reference, but skip the scaffold flow.)

## Flow

### 1. Gather requirements

Use `AskUserQuestion` to collect answers. Consolidate where possible — one or two prompts, not a twelve-step interview. Minimum set:

1. **Project identity** — name, short description, license (MIT / Apache-2.0 / proprietary). Name becomes the repo / root AGENTS.md title; slug is derived.
2. **Layout** — monorepo (`packages/<c>/` tree) or standalone single-package?
3. **Components** (multi-select; at least one required):
   - `backend` — Python service / pipeline / library
   - `frontend-web` — TypeScript browser SPA
   - `frontend-tui` — Go terminal UI
4. **Backend variant** (if backend chosen): `fastapi-service` / `fastmcp-server` / `cli-tool-python` / `library-only`.
5. **Frontend-web framework** (if frontend-web chosen): `react` / `vue` / `svelte` / `vanilla`.
6. **Frontend-tui framework** (if frontend-tui chosen): `bubbletea` (default) / `tview`.
7. **Shared OpenAPI contracts** (only if backend + ≥1 frontend): yes / no.
8. **Infra** (multi-select): `docker`, `github-actions`, `pre-commit-hooks`.
9. **Agent team + tracker?** yes (recommended) / no. Also: file-based tracker or GitHub Issues?
10. **Process & documentation** (multi-select, optional): `adr` (Architecture Decision Records under `docs/adr/`), `ubiquitous-language` (project glossary at `docs/glossary.md`). Recommend `adr` for any project expected to live > 6 months; recommend `ubiquitous-language` for backend services with named domain entities.
11. **External services** (optional, multi-select — skip any category that doesn't apply). Each selection pulls a `specs/<category>-<choice>.md` stub and emits a one-line bullet into the generated AGENTS.md, wrapped per `I9`:
   - **Datastore:** `mongodb` / `postgresql` / `redis` / `sqlite` / `other` / `none`
   - **Orchestrator:** `prefect` / `dagster` / `temporal` / `other` / `none`
   - **Observability & evals:** `opik` / `opentelemetry` / `sentry` / `other` / `none`
   - **LLM API:** `anthropic` / `openai` / `gemini` / `other` / `none`
   - **Embedding API:** `voyageai` / `openai` / `sentence-transformers` / `other` / `none`
   - **Model serving:** `modal` / `replicate` / `other` / `none`
   - **Web scraping:** `firecrawl` / `playwright` / `requests-bs4` / `other` / `none`

   Ask this as ONE consolidated question: "Which external services will you use? (deselect anything you don't need)." `none` skips the category entirely — no stub read, no bullet emitted. `other` keeps an `AGENT: fill in` placeholder so the SWE can document the real choice on first use.

12. **Reference docs (`llms.txt`)** — which tools / frameworks / services publish an `llms.txt`, and each one's index URL (e.g. Pydantic AI → `https://pydantic.dev/docs/ai/llms.txt`)? Governed by `P5`; fully skippable.

Before proceeding to step 2, echo the picked configuration back to the user in a two-line summary and confirm.

### 2. Select specs

Always include:

- [`monorepo-layout.md`](specs/monorepo-layout.md) — unless the user chose standalone single-package.
- [`makefile-delegator.md`](specs/makefile-delegator.md) — unless standalone.

Conditionally include (from answers):

| Answer | Specs to read |
|---|---|
| `backend` (any variant) | [`python-backend.md`](specs/python-backend.md) + [`uv-python.md`](specs/uv-python.md) + [`pyproject.md`](specs/pyproject.md) + [`ruff-python.md`](specs/ruff-python.md) |
| backend = `fastapi-service` | + [`fastapi-service.md`](specs/fastapi-service.md) |
| backend = `fastmcp-server` | + [`fastmcp-server.md`](specs/fastmcp-server.md) |
| backend = `cli-tool-python` | + [`cli-tool-python.md`](specs/cli-tool-python.md) |
| `frontend-web` | [`typescript-frontend.md`](specs/typescript-frontend.md) + the chosen framework spec ([`react-app.md`](specs/react-app.md) / [`vue-app.md`](specs/vue-app.md) / [`svelte-app.md`](specs/svelte-app.md) / [`vanilla-ts-app.md`](specs/vanilla-ts-app.md)) |
| `frontend-tui` | [`go-tui.md`](specs/go-tui.md) (already covers both bubbletea and tview) |
| shared OpenAPI contracts | [`openapi-contracts.md`](specs/openapi-contracts.md) |
| docker | [`docker.md`](specs/docker.md) |
| github-actions | [`github-actions.md`](specs/github-actions.md) |
| pre-commit-hooks | [`pre-commit-hooks.md`](specs/pre-commit-hooks.md) |
| agent team + tracker | [`tracker-workflow.md`](specs/tracker-workflow.md) |
| process: `adr` | [`adr.md`](specs/adr.md) |
| process: `ubiquitous-language` | [`ubiquitous-language.md`](specs/ubiquitous-language.md) |
| datastore = `mongodb` / `postgresql` / `redis` / `sqlite` | + [`datastore-<choice>.md`](specs/) |
| orchestrator = `prefect` / `dagster` / `temporal` | + [`orchestrator-<choice>.md`](specs/) |
| observability = `opik` / `opentelemetry` / `sentry` | + [`observability-<choice>.md`](specs/) |
| llm-api = `anthropic` / `openai` / `gemini` | + [`llm-<choice>.md`](specs/) |
| embeddings = `voyageai` / `openai` / `sentence-transformers` | + [`embeddings-<choice>.md`](specs/) |
| model-serving = `modal` / `replicate` | + [`model-serving-<choice>.md`](specs/) |
| scraping = `firecrawl` / `playwright` / `requests-bs4` | + [`scraping-<choice>.md`](specs/) |

Skip any row where the user picked `none` / `other`. `Read` each selected spec end-to-end.

### 3. Compose `AGENTS.md`

Write the project's root memory file from the canonical template in [`AGENTS_TEMPLATE.md`](AGENTS_TEMPLATE.md) (the template body and section structure). Compose it following the `I#` artifact invariants in [`rules.md`](rules.md). Read both end-to-end, then emit a tailored `AGENTS.md` at the target project root (or wherever `/squid-scaffold` was invoked).

**Optional — compress with caveman.** If the caveman plugin is installed, offer to run `/caveman-compress AGENTS.md` on the composed file (ask first — the result is terser to hand-edit). Skip silently when caveman isn't installed.

### 4. Create the folder skeleton

Create these files / directories, **empty or with minimal placeholders** (`P1`).

Always:

- `AGENTS.md` — from step 3.
- `CLAUDE.md` — relative symlink to `AGENTS.md` (`I4`).
- `.agents/skills/` (seeded with `.gitkeep`) and `.claude/skills` — relative symlink to it (`I12`).
- `README.md` — one-paragraph project-facing intro pointing at `AGENTS.md`.
- `.gitignore` — language-appropriate (`.venv/`, `node_modules/`, `dist/`, `bin/`, `.DS_Store`, `.env`). Do **not** ignore `.claude/skills` or `.agents/` — the symlink and its target are committed.
- `.env.example` — cross-cutting placeholder keys (one commented sample var).

If monorepo:

- **Root `Makefile`** and **per-component `packages/<c>/Makefile`** — generate from [`makefile-delegator.md`](specs/makefile-delegator.md) for the chosen components (`I10`). Write a **working first-pass Makefile**, not `AGENT: fill in` stubs: the verbs are mechanical, the tooling is standard per language, and `make install && make test` must work on the fresh scaffold. Real-code placeholders still apply to `src/`, not to the Makefile.

- Each `packages/<c>/` also gets:
  - `AGENTS.md` — one-paragraph component brief + "see root AGENTS.md for conventions"; plus a `CLAUDE.md` symlink to it (`I4`).
  - `.env.example` — component-local placeholder.
  - *No source files* (`P1`).

- If shared OpenAPI chosen: `packages/shared/openapi/api.yaml` with a minimal `/health` endpoint seed.

If docker chosen:

- `docker-compose.yml` — one service block per runtime component with `AGENT: fill in` placeholders for image / ports / healthcheck.
- Component-level `Dockerfile` stub with `AGENT: fill in` multi-stage build.

If github-actions chosen:

- `.github/workflows/ci.yml` — umbrella workflow with `dorny/paths-filter` routing.
- `.github/workflows/ci-<c>.yml` — one reusable workflow stub per component.
- `.github/dependabot.yml` — one ecosystem per component.

If agent team + tracker chosen:

- `tasks/README.md` describing the model in [`tracker-workflow.md`](specs/tracker-workflow.md).

If `adr` chosen (Process & documentation):

- `docs/adr/0001-record-architecture-decisions.md` — drop the canonical ADR-0001 boilerplate verbatim from [`adr.md`'s Bootstrap section](specs/adr.md), with `{YYYY-MM-DD}` replaced by today's date. This is the only ADR scaffold writes — subsequent ADRs are authored by the PA during `/squid-plan` grooming as decisions arise. Do **not** emit a `docs/adr/.gitkeep` (ADR-0001 already keeps the directory non-empty).

If `ubiquitous-language` chosen (Process & documentation):

- `docs/glossary.md` — this seed, verbatim. Do **not** invent domain terms — the SWE / PA populate it as the first feature lands.

  ```markdown
  # Glossary

  The canonical vocabulary for {project name}. When code, docs, specs, or conversation use a domain concept, use the term as it appears here. PRs that introduce or rename a domain concept update this file in the same change.

  | Term | Definition | Notes |
  |---|---|---|
  <!-- | **OrderLine** | One line item within an Order, identified by `order_line_id`. | Distinct from "Item" (the catalogue entry). | -->
  ```

### 5. Report back

Summarise for the user:

- File tree created (full list, relative paths).
- Which specs informed the AGENTS.md (named).
- **Exact next step** — e.g. `/squid-implement-task "bootstrap packages/backend with a minimal FastAPI app and a /health endpoint"`. The SWE agent will read AGENTS.md and the spec references, and write the first real code.
