---
name: monorepo-layout
description: Polyglot monorepo layout conventions — `packages/<component>/` tree, `shared/` for cross-language contracts, root-level tooling placement, component boundaries and naming. TRIGGER when bootstrapping a monorepo or adding / moving a component. SKIP for single-package repos or non-polyglot repos where a flat layout is fine.
---

# Polyglot monorepo layout

Opinionated layout for a monorepo holding a Python backend + TypeScript web frontend + Go TUI + OpenAPI contracts. The opinions scale down (one component) and up (more components), but the shape is the same.

## When to use

- Bootstrapping a monorepo that will hold ≥2 components in different languages.
- Adding a new component to an existing monorepo (new package under `packages/`).
- Moving / renaming / splitting a component — to stay inside the invariant.

## When NOT to use

- Single-package repos — keep it flat, don't introduce `packages/` for one thing.
- Monorepos where every component is the same language and tooling natively aggregates them (`uv workspaces`, `pnpm -r`, `go work`). Those tools own the aggregation; this skill duplicates their job.

## Canonical layout

See [`tree.md`](tree.md) for the annotated tree. Headline:

```
<repo-root>/
├── Makefile                     # root delegator — see makefile-delegator
├── docker-compose.yml           # optional; one service per runtime component
├── .github/workflows/           # umbrella + per-component CI — see github-actions-monorepo
├── .pre-commit-config.yaml
├── .env.example                 # cross-cutting secrets (DB URL, LLM keys)
├── AGENTS.md                    # repo-level brief for agents — the single source of truth
├── CLAUDE.md -> AGENTS.md       # symlink so Claude Code loads the same file (see rules.md I4)
├── README.md                    # user-facing
├── .agents/
│   └── skills/                  # project-local skills — the source of truth (empty until you add one)
├── .claude/
│   └── skills -> ../.agents/skills   # symlink so Claude Code discovers them (see rules.md I12)
├── docs/
│   ├── adr/                     # Architecture Decision Records (if chosen)
│   └── glossary.md              # ubiquitous-language glossary (if chosen)
├── tasks/                       # file-based task state — one file per task; done/ archives completed (see tracker-workflow)
└── packages/
    ├── backend/                 # Python service — has its own AGENTS.md (+ CLAUDE.md symlink)
    ├── frontend-web/            # TypeScript SPA (React / Vue / Svelte / vanilla)
    ├── frontend-tui/            # Go terminal UI (bubbletea / tview)
    └── shared/                  # OpenAPI 3.1 spec + codegen (only when backend + ≥1 frontend)
```

## Invariants

### 1. Every runtime component lives under `packages/<name>/`

No exceptions. Don't put the backend at repo root and everything else in `packages/`. Don't introduce `apps/` or `services/` or `libs/` subtrees — one-level-deep uniformity keeps `make <verb>-<component>` predictable.

### 2. Component names are language-and-role specific

Canonical names:

| Name | Role |
|---|---|
| `backend` | Python service (API server, batch pipelines, MCP server, library). |
| `frontend-web` | TypeScript browser SPA. |
| `frontend-tui` | Go terminal UI. |
| `shared` | Cross-language contracts (OpenAPI spec + codegen). |

Why these exact names:

- **Role-scoped, not generic.** `frontend-web` vs `frontend-tui` avoids ambiguity when the user types `make test-frontend` — there's no `frontend`, there's `frontend-web` and `frontend-tui`.
- **Language-hintful.** `backend` implies Python here; a different team might call theirs `api-go` or `api-rust` — pick a convention per org and stick to it.
- **`shared` is contract-only.** No runtime code. No tests beyond validation. The name signals "don't put business logic here."

Introduce a new canonical name (`worker-rust`, `mobile-ios`) when the role is common enough to warrant one. Don't overload existing names.

### 3. `shared/` only exists when there's something to share

Create `packages/shared/` only when a backend + at least one frontend both consume the same contract. Don't seed an empty `shared/` speculatively. When you create it, its job is narrow:

- `openapi/api.yaml` — OpenAPI 3.1 spec, the single source of truth.
- `Makefile` — `validate`, `gen-python`, `gen-ts`, `gen-go`, `gen-all`.
- Nothing else. No runtime code, no TypeScript, no Python.

See [`openapi-contracts`](../openapi-contracts/SKILL.md) for the codegen workflow.

### 4. Root holds orchestration, not code

Root-level files are infrastructure / coordination:

- `Makefile` — delegator (see [`makefile-delegator`](../makefile-delegator/SKILL.md)).
- `docker-compose.yml` — local dev stack.
- `.github/workflows/` — CI (see [`github-actions-monorepo`](../github-actions-monorepo/SKILL.md)).
- `.pre-commit-config.yaml` — git hooks.
- `.env.example` — *cross-cutting* env vars (DB URL, LLM API keys). Component-local env vars live in `packages/<c>/.env.example`.
- `AGENTS.md` — repo-level brief, the single source of truth; `CLAUDE.md` — a symlink to it (`I4`). `README.md` — user-facing docs.
- `.agents/skills/` — project-local skills (source of truth); `.claude/skills` — a symlink to it (`I12`). `docs/`, `tasks/` — agent-team assets.

No source code at root. No `src/` at root. If code exists that doesn't belong to any component, it's either a script (root `scripts/`) or it's genuinely shared and becomes a new component.

### 5. Component boundaries = uniform Makefile target set

Every component exposes the same verbs (see [`makefile-delegator`](../makefile-delegator/SKILL.md)). The root Makefile composes them. A component that "can't" expose `lint-check` or `format-check` is the wrong shape — either fix its tooling or revisit whether it belongs as a component.

### 6. Cross-component dependencies flow through `shared/`, not direct imports

- Frontend web imports the generated TS client from `packages/frontend-web/src/api/` (generated from `shared/openapi/api.yaml`).
- Frontend TUI imports the generated Go client from `packages/frontend-tui/internal/api/client.go`.
- Backend can import from `shared` at build time (generated Python client), but never imports from `frontend-*` — backends don't depend on frontends.

**Rule:** a component never directly imports another component's source. All cross-component contracts are code-generated from `shared/`.

### 7. Per-component `AGENTS.md` (with a `CLAUDE.md` symlink)

Each `packages/<c>/` has its own `AGENTS.md` describing that component's scope, conventions, and commands, plus a `CLAUDE.md` symlinked to it (`I4`). The root `AGENTS.md` is about the repo as a whole; component `AGENTS.md`s are local briefs. This keeps each brief scannable and lets agents load only the one they need.

## Adding a new component

1. **Pick the name.** Language-and-role specific (`worker-python`, `mobile-rn`, `infra-terraform`).
2. **Create `packages/<name>/`** with the standard skeleton for that language (see the relevant `python-backend` / `typescript-frontend` / `go-tui` skill).
3. **Wire the Makefile.** Add per-component and aggregate targets in the root Makefile (see [`makefile-delegator`](../makefile-delegator/SKILL.md)).
4. **Wire CI.** Add a per-component workflow dispatched from `ci.yml` via `dorny/paths-filter` (see [`github-actions-monorepo`](../github-actions-monorepo/SKILL.md)).
5. **Wire docker-compose** if the component has a runtime.
6. **Write `packages/<name>/AGENTS.md`** and symlink `CLAUDE.md` to it (`ln -s AGENTS.md CLAUDE.md`).
7. **Update root `AGENTS.md`** to list the new component.

## Anti-patterns

- **`apps/` + `libs/` split.** Works for some teams (Nx, Turborepo). Introduces ambiguity: is `api-client` an app or a lib? Our convention: one level, role-scoped names, no app/lib distinction.
- **Deep nesting (`packages/backend/services/auth/`).** That's a subdirectory inside `backend`, not a new component. Keep `packages/` one level deep.
- **`common/` / `utils/` as a component.** Nebulous. Dumping ground. Either it's a real contract (`shared/`) or it belongs inside a specific component.
- **Per-component lockfiles that share dependencies.** Each component has its own lockfile by design. If two components share a Python dep, they each declare it independently. Workspaces are an optimisation; don't prematurely adopt them.
- **Monorepo tooling without a need.** Turborepo, Nx, Bazel — all valuable at scale. At <10 components, the Makefile delegator is faster to reason about.


## Monorepo — annotated tree

Full canonical tree for a `backend` + `frontend-web` + `frontend-tui` + `shared` monorepo. Trim per the components you actually have.

```
<repo-root>/
│
├── Makefile                              # Root delegator. See makefile-delegator.
├── docker-compose.yml                    # Local dev stack. One service per runtime component.
├── docker-compose.ci.yml                 # CI overrides (e.g. test DB creds).
├── .env.example                          # CROSS-CUTTING env vars only (DB URL, LLM keys).
├── .github/
│   └── workflows/
│       ├── ci.yml                        # Umbrella — dispatches per-component via paths-filter.
│       ├── ci-backend.yml                # Reusable workflow.
│       ├── ci-frontend-web.yml
│       ├── ci-frontend-tui.yml
│       ├── ci-shared.yml                 # OpenAPI validate + codegen drift check.
│       ├── build.yml                     # Multi-arch image builds (optional).
│       ├── publish.yml                   # PyPI publish (optional).
│       └── dependabot.yml                # Per-ecosystem update schedule.
├── .pre-commit-config.yaml
├── .gitignore
├── .gitattributes
├── README.md                             # User-facing project docs.
├── AGENTS.md                             # Repo-level brief for agents — the single source of truth.
├── CLAUDE.md -> AGENTS.md                # Symlink so Claude Code loads the same file (I4).
├── LICENSE
│
├── docs/
│   ├── adr/                              # Architecture Decision Records (if chosen).
│   └── glossary.md                       # Ubiquitous-language glossary (if chosen).
│
├── tasks/                                # File-based task state. One file per task. See tracker-workflow.
│   ├── README.md
│   ├── 001-*.md                          # status: pending | in-progress (open tasks live at the top level)
│   └── done/                             # completed tasks moved here on completion
│       └── 000-*.md                      # status: done
│
├── .agents/                              # Harness-agnostic agent assets — the source of truth.
│   └── skills/                           # Project-local skills (empty until you add one).
│       └── .gitkeep
├── .claude/                              # Claude Code adapter (the squid agents/skills come from the global plugin install).
│   └── skills -> ../.agents/skills       # Symlink to the canonical skills dir (I12).
│
└── packages/
    │
    ├── backend/                          # See python-backend, fastapi-service, cli-tool-python.
    │   ├── pyproject.toml                # See pyproject skill.
    │   ├── Makefile
    │   ├── Dockerfile                    # See docker-slim.
    │   ├── .dockerignore
    │   ├── .env.example                  # COMPONENT-LOCAL env vars.
    │   ├── AGENTS.md                     # Backend-specific brief — the source of truth.
    │   ├── CLAUDE.md -> AGENTS.md        # Symlink (I4).
    │   ├── configs/
    │   │   └── default.yaml
    │   ├── scripts/
    │   │   └── run_example.py            # Operator-facing entry points.
    │   ├── src/
    │   │   └── <python_package_name>/
    │   │       ├── __init__.py
    │   │       ├── logging.py
    │   │       ├── config/
    │   │       ├── entities/
    │   │       ├── <domain>/
    │   │       └── ...
    │   ├── tests/
    │   │   ├── conftest.py
    │   │   ├── unit/
    │   │   └── integration/
    │   └── docker/                       # Sidecar configs (mongodb, postgres init, etc.).
    │
    ├── frontend-web/                     # See typescript-frontend + react/vue/svelte/vanilla skill.
    │   ├── package.json
    │   ├── tsconfig.json
    │   ├── vite.config.ts
    │   ├── eslint.config.js
    │   ├── .prettierrc
    │   ├── Makefile
    │   ├── Dockerfile                    # Optional; frontend serves static bundle.
    │   ├── .dockerignore
    │   ├── .env.example                  # VITE_* vars only (browser-visible).
    │   ├── AGENTS.md                     # Frontend-web brief — the source of truth.
    │   ├── CLAUDE.md -> AGENTS.md        # Symlink (I4).
    │   ├── index.html
    │   ├── public/                       # Static assets.
    │   ├── src/
    │   │   ├── main.ts(x)
    │   │   ├── App.(tsx|vue|svelte)
    │   │   ├── api/                      # GENERATED from shared/openapi — don't hand-edit.
    │   │   └── ...
    │   └── tests/
    │       └── **/*.test.ts(x)
    │
    ├── frontend-tui/                     # See go-tui + bubbletea/tview.
    │   ├── go.mod
    │   ├── go.sum
    │   ├── Makefile
    │   ├── .env.example
    │   ├── AGENTS.md                     # Frontend-tui brief — the source of truth.
    │   ├── CLAUDE.md -> AGENTS.md        # Symlink (I4).
    │   ├── cmd/
    │   │   └── <project_slug>/
    │   │       └── main.go               # Tiny. Wires framework, calls run().
    │   ├── internal/
    │   │   ├── ui/                       # Framework-specific (bubbletea or tview).
    │   │   ├── api/                      # GENERATED — don't hand-edit.
    │   │   └── config/
    │   ├── pkg/                          # Externally importable (often empty).
    │   └── tests/                        # or *_test.go beside code.
    │
    └── shared/                           # See openapi-contracts.
        ├── Makefile                      # validate, gen-python, gen-ts, gen-go, gen-all.
        ├── README.md
        ├── AGENTS.md                     # Shared/contract brief — the source of truth.
        ├── CLAUDE.md -> AGENTS.md        # Symlink (I4).
        └── openapi/
            └── api.yaml                  # OpenAPI 3.1 — single source of truth.
```

### Key invariants (enforce via review)

- Every `packages/<c>/` has `Makefile`, `AGENTS.md` (with a `CLAUDE.md` symlink), `.env.example`.
- Every runtime component has `Dockerfile` + `.dockerignore` when the monorepo uses Docker.
- `packages/shared/` exists iff there is at least one backend ↔ frontend contract to share.
- Generated code locations: `packages/frontend-web/src/api/` (TypeScript), `packages/frontend-tui/internal/api/client.go` (Go), `packages/backend/src/<pkg>/generated_client/` (Python, if backend consumes its own spec).
- Root-level `.env.example` lists cross-cutting secrets; component-level `.env.example` lists component-local settings. The union is what a developer needs to run everything locally.
- No source code lives at repo root. Scripts are under `packages/<c>/scripts/` or at root if truly cross-cutting (`scripts/bootstrap.sh`).
