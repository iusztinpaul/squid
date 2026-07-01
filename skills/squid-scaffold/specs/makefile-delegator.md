---
name: makefile-delegator
description: Root Makefile delegator pattern for monorepos — `help` target, per-component targets that fan out to sub-Makefiles, `$(MAKE)` never literal `make`, PHONY discipline, component-gated targets. TRIGGER when authoring or editing a monorepo root Makefile. SKIP for single-package repos or non-make build systems (just / task / mage).
---

# Root Makefile delegator

Opinionated root-level `Makefile` pattern for polyglot monorepos. The root never reimplements component logic — it delegates.

## When to use

- Authoring or editing the root `Makefile` of a monorepo.
- Adding a new component and wiring its targets into the root.
- Rationalising a Makefile that grew to reimplement per-component logic.

## When NOT to use

- Single-package repos — put the Makefile in the package, not at root (or no Makefile at all).
- Non-make build systems (`just`, `task`, `mage`, `tox`) — use those directly, don't force a make wrapper.
- Monorepos where all components speak the same language — `uv workspaces` / `pnpm -r` / `go work` handle aggregation natively.

## Canonical principles

### 1. Delegate, never reimplement

The root Makefile calls per-component Makefiles with `$(MAKE) -C packages/<c> <target>`. It **never** contains a per-component `uv sync` or `npm install` or `go mod tidy` directly.

```makefile
install: install-backend install-frontend-web install-frontend-tui

install-backend:
	$(MAKE) -C packages/backend install

install-frontend-web:
	$(MAKE) -C packages/frontend-web install

install-frontend-tui:
	$(MAKE) -C packages/frontend-tui install
```

### 2. `$(MAKE)`, never literal `make`

`$(MAKE)` inherits `-j`, `--silent`, variable overrides, and recursion tracking. `make -C ...` loses them. Always write `$(MAKE) -C ...`.

### 3. Aggregate + per-component target pairs

Every verb has two forms:

- **Aggregate:** `make <verb>` — runs the verb across every enabled component.
- **Per-component:** `make <verb>-<component>` — runs the verb on just that component.

```makefile
test: test-backend test-frontend-web test-frontend-tui
test-backend:
	$(MAKE) -C packages/backend test
test-frontend-web:
	$(MAKE) -C packages/frontend-web test
test-frontend-tui:
	$(MAKE) -C packages/frontend-tui test
```

This gives users a fast single-component inner loop (`make test-backend`) and a pre-PR aggregate (`make test`).

### 4. Standard verb set (contract with per-component Makefiles)

Every component Makefile implements, at minimum:

| Target | Semantics |
|---|---|
| `install` | Install/refresh dependencies into the component's environment (`uv sync`, `npm ci`, `go mod tidy`). |
| `test` | Run the component's full test suite. |
| `lint-check` / `lint-fix` | Static checks / auto-fix. |
| `format-check` / `format-fix` | Formatting checks / apply. |
| `pre-commit` | Run the same things `pre-commit` would (format-check + lint-check + light tests). |
| `build` | Produce a deployable artifact (wheel, JS bundle, Go binary). |

Backends additionally implement:

| Target | Semantics |
|---|---|
| `unit-tests` | Unit suite only (`tests/unit/`). |
| `integration-tests` | Integration suite only (`tests/integration/`). |

Frontends additionally implement:

| Target | Semantics |
|---|---|
| `dev` | Run the dev server. |

TUIs additionally implement:

| Target | Semantics |
|---|---|
| `run` | `go run ./cmd/<slug>`. |

See [`canonical.md`](canonical.md) for the full root Makefile these verbs wire into.

### 5. `help` is a first-class target

`make help` (and `make` with no args) prints the target list grouped by concern. Don't rely on `make -pn` — write the help text yourself so it's curated.

```makefile
.DEFAULT_GOAL := help

help: ## Show this help
	@awk 'BEGIN { FS = ":.*?## " } /^[a-zA-Z_\/-]+:.*?## / { printf "  %-30s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
```

The `## comment` convention lets every target self-document. New targets should include one.

### 6. `.PHONY` discipline

Every target that isn't a file goes in `.PHONY`. Miss a target and `make` will treat it as a file-existence check, leading to confusing "nothing to do" behaviours when the working tree happens to contain a matching name.

```makefile
.PHONY: help install test test-backend test-frontend-web ...
```

### 7. Component gating (conditional targets)

When a component is not present in the tree, its targets shouldn't be emitted — otherwise `make test-frontend-tui` against a backend-only repo surfaces a confusing error. Gate with a file existence check or (better) generate the Makefile from the component set at scaffold time.

In a live repo the cheap check is:

```makefile
HAS_BACKEND := $(shell test -d packages/backend && echo yes)

test: $(if $(HAS_BACKEND),test-backend)
```

### 8. Cross-cutting targets

Aggregate-only verbs that don't delegate into a single component:

| Target | Semantics |
|---|---|
| `openapi-gen` | Regenerate OpenAPI clients (see [`openapi-contracts`](../openapi-contracts/SKILL.md)). |
| `openapi-validate` | Lint the OpenAPI spec. |
| `docker-up` / `docker-down` | `docker compose up -d` / `docker compose down`. |
| `ci` | The full pre-PR fan: `install test lint-check format-check pre-commit build`. |

### 9. Fix-before-check ordering (manual loop)

When running checks by hand — outside `pre-commit` hooks or CI — run fixers before checkers so auto-fixable issues don't surface as false failures:

```bash
make format-fix && make lint-fix && \
make format-check && make lint-check && \
make pre-commit && make unit-tests
```

The `pre-commit` and `ci` targets run the non-fix variants only — correct for CI, which should fail on drift rather than mutate the tree. Locally, fix-first-check-second is the faster inner loop.

## Anti-patterns

- **Literal `make` calls** (`cd packages/backend && make test`). Loses `$(MAKE)` propagation. Use `$(MAKE) -C ...`.
- **`cd` in a recipe.** Each recipe line is a new shell; `cd` in one line doesn't affect the next. Use `-C` for directories or join with `&&` on one line.
- **Reimplementing component logic at root.** `install-backend: cd packages/backend && uv sync` duplicates what `packages/backend/Makefile` already does. Delegate instead.
- **Missing `.PHONY`.** Leads to mysteries when a target name matches a file.
- **`@echo` spam that drowns the error output.** Keep recipe output terse; let the tool itself print what matters.
- **Hard-coded component list.** When adding a new component means editing 15 places in the Makefile, the design is wrong. Either generate the Makefile from the component set, or use a variable list.


## Canonical root `Makefile` (polyglot monorepo)

Reference Makefile for a monorepo containing `backend` + `frontend-web` + `frontend-tui` + `shared`. Trim per your component selection; the structure holds.

```makefile
## Root Makefile — delegator. Per-component logic lives under packages/<c>/Makefile.
.DEFAULT_GOAL := help

## Detect which components are present. Each HAS_<X> is either "yes" or empty.
HAS_BACKEND       := $(shell test -d packages/backend && echo yes)
HAS_FRONTEND_WEB  := $(shell test -d packages/frontend-web && echo yes)
HAS_FRONTEND_TUI  := $(shell test -d packages/frontend-tui && echo yes)
HAS_SHARED        := $(shell test -d packages/shared && echo yes)

.PHONY: help install test unit-tests integration-tests lint-check lint-fix \
        format-check format-fix pre-commit build ci \
        install-backend install-frontend-web install-frontend-tui \
        test-backend test-frontend-web test-frontend-tui \
        unit-tests-backend integration-tests-backend \
        lint-check-backend lint-check-frontend-web lint-check-frontend-tui \
        lint-fix-backend lint-fix-frontend-web lint-fix-frontend-tui \
        format-check-backend format-check-frontend-web format-check-frontend-tui \
        format-fix-backend format-fix-frontend-web format-fix-frontend-tui \
        pre-commit-backend pre-commit-frontend-web pre-commit-frontend-tui \
        build-backend build-frontend-web build-frontend-tui \
        openapi-gen openapi-validate \
        dev-frontend-web run-frontend-tui \
        docker-up docker-down

## ---------- help ----------

help: ## Show this help
	@awk 'BEGIN { FS = ":.*?## " } /^[a-zA-Z_\/-]+:.*?## / { printf "  %-30s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "Enabled components:"
	@$(if $(HAS_BACKEND),      echo "  - backend";)
	@$(if $(HAS_FRONTEND_WEB), echo "  - frontend-web";)
	@$(if $(HAS_FRONTEND_TUI), echo "  - frontend-tui";)
	@$(if $(HAS_SHARED),       echo "  - shared (openapi)";)

## ---------- aggregate targets ----------

install: $(if $(HAS_BACKEND),install-backend) $(if $(HAS_FRONTEND_WEB),install-frontend-web) $(if $(HAS_FRONTEND_TUI),install-frontend-tui) ## Install all component deps
test: $(if $(HAS_BACKEND),test-backend) $(if $(HAS_FRONTEND_WEB),test-frontend-web) $(if $(HAS_FRONTEND_TUI),test-frontend-tui) ## Run every component's test suite
unit-tests: $(if $(HAS_BACKEND),unit-tests-backend) ## Backend unit tests
integration-tests: $(if $(HAS_BACKEND),integration-tests-backend) ## Backend integration tests
lint-check: $(if $(HAS_BACKEND),lint-check-backend) $(if $(HAS_FRONTEND_WEB),lint-check-frontend-web) $(if $(HAS_FRONTEND_TUI),lint-check-frontend-tui) ## Lint every component
lint-fix: $(if $(HAS_BACKEND),lint-fix-backend) $(if $(HAS_FRONTEND_WEB),lint-fix-frontend-web) $(if $(HAS_FRONTEND_TUI),lint-fix-frontend-tui) ## Apply lint fixes across components
format-check: $(if $(HAS_BACKEND),format-check-backend) $(if $(HAS_FRONTEND_WEB),format-check-frontend-web) $(if $(HAS_FRONTEND_TUI),format-check-frontend-tui) ## Check formatting everywhere
format-fix: $(if $(HAS_BACKEND),format-fix-backend) $(if $(HAS_FRONTEND_WEB),format-fix-frontend-web) $(if $(HAS_FRONTEND_TUI),format-fix-frontend-tui) ## Apply formatting fixes
pre-commit: $(if $(HAS_BACKEND),pre-commit-backend) $(if $(HAS_FRONTEND_WEB),pre-commit-frontend-web) $(if $(HAS_FRONTEND_TUI),pre-commit-frontend-tui) ## Run pre-commit-equivalent checks
build: $(if $(HAS_BACKEND),build-backend) $(if $(HAS_FRONTEND_WEB),build-frontend-web) $(if $(HAS_FRONTEND_TUI),build-frontend-tui) ## Build every deployable artifact

ci: install test lint-check format-check pre-commit build ## Full pre-PR fan — what CI does

## ---------- backend ----------

install-backend:               ## Install backend Python deps via uv
	$(MAKE) -C packages/backend install
test-backend:                  ## Run backend tests (unit + integration)
	$(MAKE) -C packages/backend test
unit-tests-backend:            ## Run backend unit tests only
	$(MAKE) -C packages/backend unit-tests
integration-tests-backend:     ## Run backend integration tests only
	$(MAKE) -C packages/backend integration-tests
lint-check-backend:
	$(MAKE) -C packages/backend lint-check
lint-fix-backend:
	$(MAKE) -C packages/backend lint-fix
format-check-backend:
	$(MAKE) -C packages/backend format-check
format-fix-backend:
	$(MAKE) -C packages/backend format-fix
pre-commit-backend:
	$(MAKE) -C packages/backend pre-commit
build-backend:                 ## Build backend wheel/sdist
	$(MAKE) -C packages/backend build

## ---------- frontend-web ----------

install-frontend-web:          ## Install frontend-web deps via npm
	$(MAKE) -C packages/frontend-web install
test-frontend-web:             ## Run frontend-web tests (vitest)
	$(MAKE) -C packages/frontend-web test
dev-frontend-web:              ## Run frontend-web dev server (vite)
	$(MAKE) -C packages/frontend-web dev
lint-check-frontend-web:
	$(MAKE) -C packages/frontend-web lint-check
lint-fix-frontend-web:
	$(MAKE) -C packages/frontend-web lint-fix
format-check-frontend-web:
	$(MAKE) -C packages/frontend-web format-check
format-fix-frontend-web:
	$(MAKE) -C packages/frontend-web format-fix
pre-commit-frontend-web:
	$(MAKE) -C packages/frontend-web pre-commit
build-frontend-web:            ## Build frontend-web production bundle
	$(MAKE) -C packages/frontend-web build

## ---------- frontend-tui ----------

install-frontend-tui:          ## go mod tidy
	$(MAKE) -C packages/frontend-tui install
test-frontend-tui:             ## Run frontend-tui tests (go test)
	$(MAKE) -C packages/frontend-tui test
run-frontend-tui:              ## Run the TUI binary via go run
	$(MAKE) -C packages/frontend-tui run
lint-check-frontend-tui:
	$(MAKE) -C packages/frontend-tui lint-check
lint-fix-frontend-tui:
	$(MAKE) -C packages/frontend-tui lint-fix
format-check-frontend-tui:
	$(MAKE) -C packages/frontend-tui format-check
format-fix-frontend-tui:
	$(MAKE) -C packages/frontend-tui format-fix
pre-commit-frontend-tui:
	$(MAKE) -C packages/frontend-tui pre-commit
build-frontend-tui:            ## Build TUI binary
	$(MAKE) -C packages/frontend-tui build

## ---------- shared OpenAPI ----------

openapi-gen:                   ## Regenerate per-language OpenAPI clients
	$(if $(HAS_SHARED),$(MAKE) -C packages/shared gen-all)
openapi-validate:              ## Validate OpenAPI spec
	$(if $(HAS_SHARED),$(MAKE) -C packages/shared validate)

## ---------- docker (optional) ----------

docker-up:                     ## Start local compose stack
	docker compose up -d
docker-down:                   ## Stop local compose stack
	docker compose down
```

### Per-component Makefile sketches

#### `packages/backend/Makefile` (Python)

```makefile
.PHONY: install test unit-tests integration-tests lint-check lint-fix format-check format-fix pre-commit build publish

install:
	uv sync
unit-tests:
	uv run pytest tests/unit -q
integration-tests:
	uv run pytest tests/integration -q
test: unit-tests integration-tests
lint-check:
	uv run ruff check src tests
lint-fix:
	uv run ruff check --fix src tests
format-check:
	uv run ruff format --check src tests
format-fix:
	uv run ruff format src tests
pre-commit: format-check lint-check
	uv run pytest tests/unit -q
build:
	uv build
publish: build
	uv publish --token $(UV_PUBLISH_TOKEN)
```

#### `packages/frontend-web/Makefile` (TypeScript)

```makefile
.PHONY: install test dev lint-check lint-fix format-check format-fix pre-commit build

install:
	npm ci
test:
	npm run test
dev:
	npm run dev
lint-check:
	npm run lint
lint-fix:
	npm run lint:fix
format-check:
	npm run format:check
format-fix:
	npm run format
pre-commit: format-check lint-check test
build:
	npm run build
```

#### `packages/frontend-tui/Makefile` (Go)

```makefile
PROJECT_SLUG := my-tui

.PHONY: install test run lint-check lint-fix format-check format-fix pre-commit build

install:
	go mod tidy
test:
	go test ./...
run:
	go run ./cmd/$(PROJECT_SLUG)
lint-check:
	go vet ./...
lint-fix: lint-check
format-check:
	@test -z "$$(gofmt -l .)" || (gofmt -l . && exit 1)
format-fix:
	gofmt -w .
pre-commit: format-check lint-check test
build:
	go build -o bin/$(PROJECT_SLUG) ./cmd/$(PROJECT_SLUG)
```

#### `packages/shared/Makefile` (OpenAPI codegen)

```makefile
SPEC := openapi/api.yaml

.PHONY: validate gen-python gen-ts gen-go gen-all

validate:
	uvx openapi-spec-validator $(SPEC)

gen-python:
	@test -d ../backend || (echo "skipping: no backend"; exit 0)
	uvx openapi-python-client generate --path $(SPEC) --output-path ../backend/src/generated_client --overwrite

gen-ts:
	@test -d ../frontend-web || (echo "skipping: no frontend-web"; exit 0)
	npx -y @openapitools/openapi-generator-cli generate -i $(SPEC) -g typescript-fetch -o ../frontend-web/src/api

gen-go:
	@test -d ../frontend-tui || (echo "skipping: no frontend-tui"; exit 0)
	go run github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen@latest -generate types,client,spec -package api -o ../frontend-tui/internal/api/client.go $(SPEC)

gen-all: gen-python gen-ts gen-go
```
