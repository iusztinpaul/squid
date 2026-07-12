# AGENTS.md template

`/squid-scaffold` distils this into the project's root `AGENTS.md` — the agent-agnostic memory file every coding agent reads, and the single source of truth. Scaffold also symlinks `CLAUDE.md` to `AGENTS.md` so Claude Code (and any `CLAUDE.md`-only harness) loads the same content — see [`rules.md`](rules.md) `I4`.

This file is the **template body only**. The constraints on composing it — flat scope-based section order (`I5`), size ≤ 250 lines (`I2`), distil-don't-copy (`I3`), gate-sections-on-presence (`I6`), group-Key-Components-per-app (`I7`), fill-placeholders-inline (`I8`) — live in [`rules.md`](rules.md), the single source of truth. Read those `I#` invariants, then fill in the template below.

## Template

````markdown
# {Project name}

{One sentence: what this project is, what it produces, who it's for — from the user's /squid-scaffold description.} {One short clause naming the shape/stack, e.g. "A Python backend + TypeScript web monorepo." Per-component conventions are noted under Key Components.}

# Key Principles You Will Respect All Over Your Work

- Always prioritize removing instructions over adding more.
- Always use the minimum number of words needed to explain what you do, write docs or code that achieve the desired goal.
- Whenever you add a new rule to the memory (such as `AGENTS.md`), support it with a clear, concise explanation plus a set of good and bad examples. Good examples: "a 200-token chunk size", "sub-100ms latency". Bad examples: "a powerful architecture", "a robust pipeline".
- **Loose clean architecture.** Keep infrastructure, serving, app, and domain logic decoupled — but pragmatically: flat structure named by *actionability*, not dogmatic layering. Shared data structures live centrally (`entities/`); types used by a single module stay local to it (`<module>/types.py`). Import infrastructure you won't swap (DB, orchestrator, observability) directly — no interfaces "for swappability" you'll never use. *Good:* a `users/` module holding `users/api.py` + `users/store.py` + `users/types.py`. *Bad:* a 4-layer `services/`+`repositories/`+`adapters/`+`use_cases/` tree for CRUD.
{- 0–3 more project-specific principles, distilled and terse. Omit if none.}

# Key Components

{One bullet per enabled component. If the project has multiple apps, group them under a `## <app-name>` subheading per app. Each bullet: directory link, one-line role, language, and a SHORT design-conventions note (1–2 phrases distilled from the component's spec — link the spec for depth).}

- **Backend** — [`packages/backend/`](packages/backend/): {role}. Python ({fastapi-service / fastmcp-server / cli-tool / library}); {2–3 headline conventions, e.g. Pydantic models (not dataclasses/TypedDicts), async I/O, infra imported directly, `entities/` for shared models}. Depth: the squid `python-backend` spec.
- **Web frontend** — [`packages/frontend-web/`](packages/frontend-web/): {role}. TypeScript ({framework}); {Vite + strict tsconfig, one exported component per file}. Depth: the squid `typescript-frontend` spec.
- **TUI frontend** — [`packages/frontend-tui/`](packages/frontend-tui/): {role}. Go ({bubbletea / tview}); {thin `cmd/<slug>/main.go`, logic in `internal/`}. Depth: the squid `go-tui` spec.
- **Shared contracts** — [`packages/shared/`](packages/shared/): OpenAPI 3.1 spec + per-language codegen. *Only if shared chosen.*

## Component dependencies

*Only for multi-component projects.* How modules/components may call each other:

- Cross-component contracts flow through `packages/shared/` (OpenAPI 3.1 → generated clients: `frontend-web/src/api/`, `frontend-tui/internal/api/client.go`, `backend/src/<pkg>/generated_client/` — never hand-edited). A component **never** imports another component's source directly.
- The backend may consume `shared/` but **never imports from `frontend-*`**.

# Project Structure

{ASCII tree pulled from `monorepo-layout.md`, trimmed to the chosen components. Include `tasks/` when the agent team is chosen.}

**Scripts & entrypoints.**
- Python: operator scripts in `scripts/`; CLI entrypoints in `pyproject.toml` `[project.scripts]`; server/MCP mains at `scripts/serve_*.py`. **Every entrypoint module (script, server main, CLI root) calls `init_logger()` at module level before any logic or project import.**
- Go: `cmd/<slug>/main.go` is thin — wires the framework, calls `run()`.
- Run entrypoints via the wired `make run-*` targets where available.

# Tech Stack

Multi-language — each component brings its own toolchain:

{- **Python 3.12+** (backend) — `uv`, `ruff`, `pytest`.}
{- **Node.js 20+** (frontend-web) — `bun`, `vite`, `vitest`, `eslint` 9, `prettier` 3.}
{- **Go 1.22+** (frontend-tui) — `go mod`, `gofmt`, `go test`.}
{- **OpenAPI 3.1 + codegen** (shared) — `openapi-spec-validator`, `openapi-python-client`, `@openapitools/openapi-generator-cli`, `oapi-codegen`.}

## Access Documentation

Use the `context7` MCP server (when connected) to look up authoritative usage for any tech-stack item or external service above; falls back to web search otherwise.

{Emit the block below only if the user named one or more `llms.txt`-publishing tools at scaffold time (rules.md P5); otherwise omit it entirely and rely on `context7` alone.}

**Reference docs (`llms.txt` — fetch on demand).** Each link below is an *index* of doc pages. Fetch the index first, then fetch only the specific page(s) you need. Do **not** pull whole `llms-full.txt` files into context unless a task truly requires the full reference.

{One bullet per tool the user named, as `**<Tool>:** <index llms.txt URL> — <optional note>`. Use the user's URLs verbatim — never invent one. The notes below show the format:}
{- **Pydantic AI:** https://pydantic.dev/docs/ai/llms.txt — append `.md` to any doc page for raw markdown.}
{- **Modal:** https://modal.com/llms.txt — full reference at https://modal.com/llms-full.txt (large; only if needed).}

## Running commands

All core verbs run at the repo root via the [`Makefile`](Makefile), which **delegates** to each component (`$(MAKE) -C packages/<c> <verb>`) — never reimplementing per-component logic:

| Verb | What it does |
|---|---|
| `make install` | Install/refresh every component's deps. |
| `make test` | Run every component's test suite. |
{| `make unit-tests` / `make integration-tests` | Backend unit / integration tests. |}
| `make lint-check` / `make lint-fix` · `make format-check` / `make format-fix` | Static / formatting checks + auto-fix. |
| `make pre-commit` | `format-check + lint-check + light tests`. |
| `make build` | Build every deployable artifact (one component: `make build-<component>`). |
| `make help` | Curated target list. |

Each verb has a `-<component>` form for the fast inner loop (`make test-backend`). **Manual QA order:** `format-fix → lint-fix → format-check → lint-check → pre-commit → unit-tests`.

Commands not wrapped by `make` — use the per-component runner:
{- **Python:** `uv run …`, `uvx <tool>` (from root: `uv --directory packages/<c> run …`).}
{- **TypeScript:** `bun run <script>`, `bunx <tool>`.}
{- **Go:** `go run ./cmd/<slug>`, `go test ./...`.}

**Dependencies & env vars.** Add deps to the component-specific manifest ({`pyproject.toml`}{ / `package.json`}{ / `go.mod`}) — never mix languages' deps. New env vars → the component's `.env.example` + config module; cross-cutting secrets → the root `.env.example`.

## Infrastructure & external services

Access infra and external services **CLI-only** (no web UIs), so the orchestrator can spot-check by re-running commands.

- **Git / GitHub:** `git`; `gh` for PRs, issues, Actions logs.
{- **Docker:** `docker compose up -d` / `down` / `logs -f <svc>`.}
{- **Orchestrator (e.g. Prefect):** `uv run prefect ...` — *AGENT: fill in the deploy/run commands.*}
- **Project MCP servers:** *AGENT: fill in any MCP server this project's code talks to and the config it needs.*

For each external-service slug the user selected, emit one bullet below wrapped in `<!-- stack:<slug> -->` / `<!-- /stack:<slug> -->` comments (one-line summary from the spec's frontmatter `description`, with its CLI). Emit nothing for categories left `none`. Grep `<!-- stack:` to find and delete a block.

```
<!-- stack:mongodb -->
- **MongoDB** — async ODM (Beanie / PyMongo); `mongosh "$MONGODB_URL"` for local queries. Spec: squid `datastore-mongodb`.
<!-- /stack:mongodb -->
```

# Developing New Features & Bug Fixes

*Only emit if agent team + tracker chosen.*

This project uses the **squid** agent team (`/plugin marketplace add iusztinpaul/squid && /plugin install squid@iusztinpaul`) — per-role rules in `agents/`, per-phase rules in the skills. Direct chat for trivial edits; for one or a few groomed tasks use **`/squid-implement-task`**; for a whole feature use **`/squid-plan`** then **`/squid-implement-night`** (or run **`/squid-review`** / **`/squid-review-ci`** standalone).

| Role | Responsibility |
|---|---|
| Product Architect (PA) | Grooms a feature into a Tasks Plan; authors ADRs + glossary; user-POV acceptance. |
| Software Engineer | Implements code + tests; commits each task after the Tester passes. |
| Tester | Full suite + **e2e adversarial QA**. |
| PR Reviewer | Diff review — correctness, simplicity, tests, standards, docs. |
| On-Call | Watches CI; diagnoses failures and hands fix tasks to the SWE. |

```
/squid-plan  →  approved Tasks Plan (+ optional ADR) + branch/worktree
/squid-implement-night (in the worktree):  /squid-implement-task → /squid-review → /squid-review-ci  →  human squash-merges
```

Engineering discipline — TDD-first, branch off the active branch, run the feature end-to-end before hand-off, regression-test-first for bugs, the format/lint/unit/integration cadence — lives in the squid `software-engineer` + `tester` agent contracts and is enforced automatically by the pipelines.

**Optional — caveman.** If the [caveman](https://github.com/JuliusBrussee/caveman) plugin is installed, the SWE writes each commit with `/caveman-commit`, the PR-Reviewer posts one-line `/caveman-review` comments on the PR (on top of its rollup), and you can shrink this file with `/caveman-compress AGENTS.md` to cut per-session tokens. Everything works without it — the integrations fall back to native behavior.

**Tracker:** `TRACKER_MODE: file` *(or `gh` for GitHub Issues)*. File mode: one `tasks/<NNN>-<slug>.md` per task with a `status:` frontmatter field (`pending` → `in-progress` → `done`); completing a task moves the file into `tasks/done/`, leaving only open tasks at the top level. See [`tasks/README.md`](tasks/README.md).

Project-specific invariants the agents can't infer:

{- **Shared contracts:** edit `packages/shared/openapi/api.yaml` and run `make openapi-gen`; **never hand-edit** generated clients. After spec edits, `make openapi-validate && make openapi-gen` and confirm clients compile.}
{- **`docker-compose.yml` edits:** `make docker-up` then `docker compose ps` — every service `healthy` within 30s.}
{- **Orchestrator pipeline edits:** serve the worker (`make serve-workflows &`), trigger via `make run-<pipeline>`; re-serve after code changes.}

# Testing E2E

{AGENT: fill in the concrete way to exercise THIS project end-to-end — per e2e-testable surface, give: the exact entrypoint/command, any service that must be running first (`make run-<component>` / `make docker-up`), required env / seed data, and what "working" looks like (expected output, status code, row written). Keep it project-specific and runnable. The generic "use it like a user, then try to break it" method is the Tester's job — see the squid `tester` agent contract.}

# Documentation Conventions

*Only emit if `adr` and/or `ubiquitous-language` were chosen.*

{If `adr`:}
- **ADRs** at [`docs/adr/`](docs/adr/) — `NNNN-kebab-title.md`, Nygard template (Status / Context / Decision / Diagram / Consequences; the Diagram a coloured Mermaid system diagram of the change). One ADR per feature, capturing its whole design (a feature's related architectural choices go in a single ADR — not one per task or per choice). Spec: squid `adr`.

{If `ubiquitous-language`:}
- **Glossary** at [`docs/glossary.md`](docs/glossary.md) — one canonical name per concept, used identically in code / OpenAPI schemas / DB columns / UI; update it in the same PR that introduces or renames a concept. PA grooming and `/squid-grilling` read it as the tie-breaker. Spec: squid `ubiquitous-language`.
````
