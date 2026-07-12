---
name: squid-scaffold
description: >-
  Bootstrap a new repo or component from the opinionated spec library (mode=create), or audit an
  existing scaffolded repo for drift against the scaffold rules (mode=evaluate, report-only).
disable-model-invocation: true
argument-hint: "[mode=create|evaluate] [project description | target repo path]"
---

# Scaffold

Interactive bootstrap for a new repo (or a new component in an existing one).

- Ask the user what they want to build.
- Read only the specs under [`specs/`](specs/) that apply.
- Write a tailored `AGENTS.md` at the target project root that **distils** those specs (doesn't copy-paste them) — `AGENTS.md` is the single source of truth, with `CLAUDE.md` symlinked to it for Claude Code.
- Set up the canonical `.agents/skills/` dir (source of truth for project-local skills), with `.claude/skills` symlinked to it.
- Lay down an empty folder skeleton (no source code).
- Hand control back — the user runs `/squid-implement-task` next to have the SWE agent write the first code against the generated AGENTS.md.

## Modes

`$ARGUMENTS` may lead with `mode=create` (default) or `mode=evaluate`:

- **`mode=create`** (default) — bootstrap a repo / component. The flow in "## Flow" below.
- **`mode=evaluate`** — audit an *existing* scaffolded repo against the artifact invariants in [`rules.md`](rules.md) and report drift (no fixes). See "## Evaluate mode".

Every rule both modes honour lives in [`rules.md`](rules.md) — the single source of truth. Do **not** restate any rule in this file.

## When to use

- Bootstrapping a brand-new repo.
- Adding a new runtime component (backend / frontend-web / frontend-tui) to an existing scaffolded repo.
- Re-generating the root `AGENTS.md` after a major stack change (e.g. swapping Vue for React).

## When NOT to use

- Writing application source code (that's the SWE agent's job under `/squid-implement-task` or `/squid-implement-night`).
- Filling in business logic, API handlers, components, etc.
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
11. **External services** (optional, multi-select — skip any category that doesn't apply). Each selection pulls a `specs/<category>-<choice>.md` stub and emits a one-line bullet into the generated AGENTS.md, wrapped in `<!-- stack:<slug> -->` comments so the user can find-and-delete it later:
   - **Datastore:** `mongodb` / `postgresql` / `redis` / `sqlite` / `other` / `none`
   - **Orchestrator:** `prefect` / `dagster` / `temporal` / `other` / `none`
   - **Observability & evals:** `opik` / `opentelemetry` / `sentry` / `other` / `none`
   - **LLM API:** `anthropic` / `openai` / `gemini` / `other` / `none`
   - **Embedding API:** `voyageai` / `openai` / `sentence-transformers` / `other` / `none`
   - **Model serving:** `modal` / `replicate` / `other` / `none`
   - **Web scraping:** `firecrawl` / `playwright` / `requests-bs4` / `other` / `none`

   Ask this as ONE consolidated question: "Which external services will you use? (deselect anything you don't need)." `none` skips the category entirely — no stub read, no bullet emitted. `other` keeps an `AGENT: fill in` placeholder so the SWE can document the real choice on first use.

12. **Reference docs (`llms.txt`)** — ask which tools / frameworks / services this project uses that publish an `llms.txt`, and collect each one's index URL (e.g. Pydantic AI → `https://pydantic.dev/docs/ai/llms.txt`). They become direct links in the generated AGENTS.md "Access Documentation" section; anything the user doesn't name falls back to `context7`. Fully skippable — name none and only the `context7` paragraph is emitted. Governed by [`rules.md`](rules.md) `P5`.

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

Skip any row where the user picked `none` / `other`. `other` is handled at compose time by leaving an `AGENT: fill in` placeholder in the generated AGENTS.md.

`Read` each selected spec end-to-end. Specs are short markdown — full read is fine. Skip reading specs that don't apply; keep context lean.

### 3. Compose `AGENTS.md`

Write the project's root memory file from the canonical template in [`AGENTS_TEMPLATE.md`](AGENTS_TEMPLATE.md) (the template body and section structure). Compose it following the `I#` artifact invariants in [`rules.md`](rules.md) — size, distil-don't-copy, gate-sections-on-presence, group-per-app, fill-placeholders-inline. Read both end-to-end, then emit a tailored `AGENTS.md` at the target project root (or wherever `/squid-scaffold` was invoked).

`AGENTS.md` is the canonical, agent-agnostic memory file — the single source of truth. Alongside it, create `CLAUDE.md` as a **relative symlink** to `AGENTS.md` (`ln -s AGENTS.md CLAUDE.md`) so Claude Code loads the exact same file with zero duplication (see [`rules.md`](rules.md) `I4`).

**Optional — compress with caveman.** If the caveman plugin is installed, offer to run `/caveman-compress AGENTS.md` on the composed file — it rewrites the memory file into caveman-speak (~46% fewer input tokens every session; code, paths, and URLs are byte-preserved). Ask first: the compressed form is terser to read and hand-edit. Skip silently when caveman isn't installed.

### 4. Create the folder skeleton

Create these files / directories, **empty or with minimal placeholders**. Do NOT write application source.

Always:

- `AGENTS.md` — from step 3 (the canonical, agent-agnostic memory file; the single source of truth).
- `CLAUDE.md` — a **relative symlink** to `AGENTS.md` (`ln -s AGENTS.md CLAUDE.md`), the Claude Code adapter for the canonical file (`I4`). Not a copy, not an `@AGENTS.md` import.
- `.agents/skills/` — the canonical, harness-agnostic dir for project-local skills; seed it with an empty `.agents/skills/.gitkeep` (skills land here as the project grows).
- `.claude/skills` — a **relative symlink** to `../.agents/skills` (`ln -s ../.agents/skills .claude/skills`) so Claude Code discovers project-local skills (`I12`).
- `README.md` — one-paragraph project-facing intro pointing at `AGENTS.md`.
- `.gitignore` — language-appropriate (`.venv/`, `node_modules/`, `dist/`, `bin/`, `.DS_Store`, `.env`). Do **not** ignore `.claude/skills` or `.agents/` — the symlink and its target are committed.
- `.env.example` — cross-cutting placeholder keys (one commented sample var).

If monorepo:

- **Root `Makefile`** — delegator, generated dynamically from the chosen components per [`makefile-delegator.md`](specs/makefile-delegator.md). For every enabled component, emit:
  - The standard verb set (each present as both aggregate and per-component form):
    - `install`, `test`, `lint-check`, `lint-fix`, `format-check`, `format-fix`, `pre-commit`, `build`
  - Backend-only extras (if `backend` in components): `unit-tests`, `integration-tests`.
  - Frontend-web extras (if `frontend-web` in components): `dev`.
  - Frontend-tui extras (if `frontend-tui` in components): `run`.
  - Cross-cutting verbs (if applicable): `openapi-gen`, `openapi-validate` (shared chosen), `docker-up`, `docker-down` (docker chosen), `ci` (always), `help` (always).
  - `.PHONY` list built dynamically from emitted verbs (never hardcoded).
  - `help` target that echoes the enabled-component summary + the curated target list.
  - Component-gating: use `HAS_<component> := $(shell test -d packages/<c> && echo yes)` and gate targets via `$(if $(HAS_<X>), <target>)` — so `make test` on a backend-only render doesn't try to run `test-frontend-web`.
  - Every recipe is `$(MAKE) -C packages/<c> <verb>` — **never** a literal `make` or a `cd` chain.

- **Per-component `packages/<c>/Makefile`** — implements the verb set in the chosen language's tooling. Use the canonical sketches from [`makefile-delegator.md`](specs/makefile-delegator.md):
  - **Python backend:** `uv sync`, `uv run pytest`, `uv run ruff check`, `uv run ruff format`, `uv build`.
  - **TypeScript frontend-web:** `npm ci`, `npm run test`, `npm run lint`, `npm run format`, `npm run build`.
  - **Go frontend-tui:** `go mod tidy`, `go test ./...`, `go vet ./...`, `gofmt -l/-w`, `go build`.
  - **Shared OpenAPI:** `uvx openapi-spec-validator`, `uvx openapi-python-client`, `@openapitools/openapi-generator-cli`, `oapi-codegen`.
  - Scaffold writes a **working first-pass Makefile** per component (not `AGENT: fill in` stubs) — the verbs are mechanical, the tooling is standard per language, and having `make install` work out-of-the-box on the fresh scaffold lets the user run `make install && make test` before any SWE work. Real-code placeholders still apply to `src/`, not to the Makefile.

- Each `packages/<c>/` also gets:
  - `AGENTS.md` — one-paragraph component brief + "see root AGENTS.md for conventions"; plus a `CLAUDE.md` **symlink** to it (`ln -s AGENTS.md CLAUDE.md`) so Claude Code loads it (`I4`).
  - `.env.example` — component-local placeholder.
  - *No source files.* (Those are SWE agent's job on first `/squid-implement-task` run.)

- If shared OpenAPI chosen: `packages/shared/openapi/api.yaml` with a minimal `/health` endpoint seed.

If docker chosen:

- `docker-compose.yml` — one service block per runtime component with `AGENT: fill in` placeholders for image / ports / healthcheck.
- Component-level `Dockerfile` stub with `AGENT: fill in` multi-stage build.

If github-actions chosen:

- `.github/workflows/ci.yml` — umbrella workflow with `dorny/paths-filter` routing.
- `.github/workflows/ci-<c>.yml` — one reusable workflow stub per component.
- `.github/dependabot.yml` — one ecosystem per component.

If agent team + tracker chosen:

- `tasks/README.md` describing the one-file-per-task model (`tasks/<NNN>-<slug>.md` with a `status:` frontmatter field — `pending` / `in-progress` / `done` — and a `feature:` field). State lives in the frontmatter, not the filename; on completion the file is `git mv`'d into `tasks/done/`, so the top level of `tasks/` lists only open work (pending + in-progress) and `NNN` is allocated by scanning both `tasks/` and `tasks/done/`. (The agent-team lifecycle + cross-cutting rules are baked into the generated `AGENTS.md` from `AGENTS_TEMPLATE.md` — there is no separate `docs/PROCESS.md`.)
- `.claude/` plugin assets (the squid agents/skills themselves) — only if the user isn't installing the plugin globally; otherwise skip (the global install provides them). This is separate from the `.claude/skills` symlink in the Always block, which points at *project-local* skills under `.agents/skills/` and is always created.

If `adr` chosen (Process & documentation):

- `docs/adr/0001-record-architecture-decisions.md` — drop the canonical ADR-0001 boilerplate verbatim from [`adr.md`'s Bootstrap section](specs/adr.md), with `{YYYY-MM-DD}` replaced by today's date. This is the only ADR scaffold writes — subsequent ADRs are authored by the PA during `/squid-plan` grooming as decisions arise. Do **not** emit a `docs/adr/.gitkeep` (ADR-0001 already keeps the directory non-empty).

If `ubiquitous-language` chosen (Process & documentation):

- `docs/glossary.md` — minimal seed: a one-paragraph header declaring the discipline ("The canonical vocabulary for {project}. When code, docs, specs, or conversation use a domain concept, use the term as it appears here.") + an empty 3-column table (`| Term | Definition | Notes |`) with a single commented-out example row so the format is unambiguous. Do **not** invent domain terms — the SWE / PA populate it as the first feature lands. Recommended seed body:

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

## Rules

All scaffold rules — create-time process rules (`P#`) and artifact invariants (`I#`) — live in [`rules.md`](rules.md), the single source of truth. While composing in `mode=create`, follow **every** `P#` and `I#`. Do not restate them here.

## Evaluate mode

`mode=evaluate` audits an *existing* scaffolded repo against the artifact invariants in [`rules.md`](rules.md) and reports drift. **You are the auditor — you do NOT apply fixes, you report.** The flow is read-only on the target repo; the report is printed to chat (no file is written).

### E1 — Resolve target

`$ARGUMENTS` after `mode=evaluate` is the target repo root (default: the current working directory). Echo it back in one line. If there is no `AGENTS.md` there, stop with a clear message: *"Nothing scaffolded to evaluate at `{path}` — run `mode=create` first."*

### E2 — Spawn the audit sub-agent

Launch a single `Explore` sub-agent. It reads the rules from the **plugin's** scaffold skill dir and audits the artifacts in the **target** repo — keep those two locations distinct in the prompt:

```
Agent(
  subagent_type="Explore",
  prompt="""Scaffold-conformance audit of the repo at {target path}.

  AUTHORITATIVE RULES (read from the squid plugin's scaffold skill dir, NOT the target repo):
  read `skills/squid-scaffold/rules.md` end to end, and `skills/squid-scaffold/AGENTS_TEMPLATE.md` for
  structure questions. Audit ONLY the `I#` artifact invariants — skip every `P#` (those are
  create-time and not checkable from a checkout).

  ARTIFACTS UNDER AUDIT (in the target repo at {target path}): read `AGENTS.md` and the root
  `Makefile`; verify with `ls -l` / `readlink` (not by reading bodies — a symlink read follows
  transparently to `AGENTS.md`) that the root `CLAUDE.md` and every `packages/*/CLAUDE.md` are
  symlinks to their sibling `AGENTS.md` (`I4`) and that `.claude/skills` is a symlink to
  `../.agents/skills` with `.agents/skills/` a real directory (`I12`); and scan the skeleton
  tree (`ls -R`, not file bodies).

  For EACH `I#` rule, run its `Check:` procedure and return one row:
    `rule id | PASS | VIOLATED | N/A | evidence (file:line or command output) | one-line remediation`.
  Mark a rule N/A (not VIOLATED) when it doesn't apply — e.g. monorepo-only rules (I7, I10) on a
  standalone single-package repo. Quote rules by ID only — do NOT paste rule text into your output.
  Do NOT propose code changes beyond the one-line remediation. Return the table plus a 2–3 sentence
  health summary."""
)
```

### E3 — Compose the report (to chat)

Read the target's `AGENTS.md` yourself first — the judgment-call invariants (`I2` size, `I3` distil, `I5` structure) need a firsthand read, not just the sub-agent's grep. Then print:

- A 2–3 sentence headline summary (the main drift, or "no drift").
- **Violations** — one block per VIOLATED rule: reference the rule by ID (e.g. `see rules.md#I2` — do **not** restate the rule text), the evidence (`file:line`), and a one-paragraph remediation describing the *shape* of the fix (not a patch).
- **Passing** — a terse one-line list of the PASS rule IDs.
- **N/A** — an explicit list of N/A rules with the one-line reason (e.g. "I7, I10 — standalone repo, no monorepo Makefile/per-app grouping").

Findings are naturally bounded by the fixed rule set — no arbitrary cap.

### E4 — Hand off

Single block: result counts, the violated IDs, and the recommended next step — either *"Edit AGENTS.md to resolve {IDs} — see remediations above, then re-run `/squid-scaffold mode=evaluate` to confirm"* or *"No drift — AGENTS.md still conforms."*

## Index of specs

The spec library lives at [`specs/`](specs/). Each file is a standalone reference doc describing *opinions*, not *code*. Grouped by role:

**Layout & tooling (foundational)**
- [`monorepo-layout.md`](specs/monorepo-layout.md) — polyglot monorepo tree + component boundaries.
- [`makefile-delegator.md`](specs/makefile-delegator.md) — root Makefile pattern + canonical example.

**Python**
- [`python-backend.md`](specs/python-backend.md) — layout, discipline, testing conventions.
- [`uv-python.md`](specs/uv-python.md) — uv usage (add / sync / run / build / publish).
- [`pyproject.md`](specs/pyproject.md) — `pyproject.toml` structure + canonical example.
- [`ruff-python.md`](specs/ruff-python.md) — ruff configuration opinions.

**Python project types**
- [`fastapi-service.md`](specs/fastapi-service.md) — FastAPI app factory, lifespan, endpoints.
- [`fastmcp-server.md`](specs/fastmcp-server.md) — FastMCP server shape.
- [`cli-tool-python.md`](specs/cli-tool-python.md) — typer/click CLI conventions.

**TypeScript frontend**
- [`typescript-frontend.md`](specs/typescript-frontend.md) — package layout + canonical configs.
- [`react-app.md`](specs/react-app.md) — React SPA specifics.
- [`vue-app.md`](specs/vue-app.md) — Vue SPA specifics.
- [`svelte-app.md`](specs/svelte-app.md) — Svelte SPA specifics.
- [`vanilla-ts-app.md`](specs/vanilla-ts-app.md) — no-framework TypeScript SPA.

**Go TUI**
- [`go-tui.md`](specs/go-tui.md) — layout, Bubbletea, and tview in one doc.

**Infrastructure**
- [`docker.md`](specs/docker.md) — slim Dockerfile + docker-compose opinions.
- [`github-actions.md`](specs/github-actions.md) — monorepo CI patterns.
- [`openapi-contracts.md`](specs/openapi-contracts.md) — contract-first OpenAPI 3.1 workflow.
- [`pre-commit-hooks.md`](specs/pre-commit-hooks.md) — project-side hook conventions (`pre-commit` / `lefthook` / `husky`), what runs in `pre-commit` vs `pre-push`, escape-hatch policy.

**Process & documentation**
- [`tracker-workflow.md`](specs/tracker-workflow.md) — file-based task tracker format.
- [`adr.md`](specs/adr.md) — Architecture Decision Records (`docs/adr/NNNN-title.md`), Nygard template, status lifecycle.
- [`ubiquitous-language.md`](specs/ubiquitous-language.md) — project glossary at `docs/glossary.md`; one canonical name per domain concept.

**External services** *(all stubs — flesh out as real projects reveal opinions; delete any category or file you decide isn't worth maintaining, and drop the matching row in Step 2's decision table)*
- Datastore: [`datastore-mongodb.md`](specs/datastore-mongodb.md), [`datastore-postgresql.md`](specs/datastore-postgresql.md), [`datastore-redis.md`](specs/datastore-redis.md), [`datastore-sqlite.md`](specs/datastore-sqlite.md).
- Orchestrator: [`orchestrator-prefect.md`](specs/orchestrator-prefect.md), [`orchestrator-dagster.md`](specs/orchestrator-dagster.md), [`orchestrator-temporal.md`](specs/orchestrator-temporal.md).
- Observability: [`observability-opik.md`](specs/observability-opik.md), [`observability-opentelemetry.md`](specs/observability-opentelemetry.md), [`observability-sentry.md`](specs/observability-sentry.md).
- LLM API: [`llm-anthropic.md`](specs/llm-anthropic.md), [`llm-openai.md`](specs/llm-openai.md), [`llm-gemini.md`](specs/llm-gemini.md).
- Embeddings: [`embeddings-voyageai.md`](specs/embeddings-voyageai.md), [`embeddings-openai.md`](specs/embeddings-openai.md), [`embeddings-sentence-transformers.md`](specs/embeddings-sentence-transformers.md).
- Model serving: [`model-serving-modal.md`](specs/model-serving-modal.md), [`model-serving-replicate.md`](specs/model-serving-replicate.md).
- Scraping: [`scraping-firecrawl.md`](specs/scraping-firecrawl.md), [`scraping-playwright.md`](specs/scraping-playwright.md), [`scraping-requests-bs4.md`](specs/scraping-requests-bs4.md).
