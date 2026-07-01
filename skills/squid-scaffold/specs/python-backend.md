---
name: python-backend
description: How to structure a Python 3.12+ backend package — layout, uv, ruff, pytest, logging bootstrap, datetime/types discipline, pipeline idempotency rules. TRIGGER when writing or modifying Python backend code, adding a new Python package or service, or bootstrapping a Python repo. SKIP for one-off Python scripts and notebooks.
---

# Python backend

Opinionated starter for Python 3.12+ backends (HTTP services, ML pipelines, CLIs, libraries). This is the top-level index for Python work; framework-specific skills (`fastapi-service`, `fastmcp-server`, `cli-tool-python`) build on top of it.

Every rule here is enforceable by the `tester` agent — when the code violates a non-negotiable, that's a FAIL.

## When to use

- Writing or modifying Python backend code (services, pipelines, libraries).
- Adding a new Python package to an existing monorepo (under `packages/<name>/` — see [`monorepo-layout`](../monorepo-layout/SKILL.md)).
- Bootstrapping a Python repo from scratch.

## When NOT to use

- One-off scripts that live outside any package structure — put them at the repo root as `script_name.py` with a shebang.
- Jupyter notebooks — they have their own discipline (reproducibility, output cleaning) and this skill doesn't cover it.
- Non-Python projects — use [`typescript-frontend`](../typescript-frontend/SKILL.md) or [`go-tui`](../go-tui/SKILL.md) instead.

## Decision tree

- Building an **HTTP API** → this + [`fastapi-service`](../fastapi-service/SKILL.md).
- Building an **MCP server** → this + [`fastmcp-server`](../fastmcp-server/SKILL.md).
- Building a **CLI tool** → this + [`cli-tool-python`](../cli-tool-python/SKILL.md).
- **Library only** (importable, no server, no CLI) → just this skill.
- Any of the above — also pull [`uv-python`](../uv-python/SKILL.md), [`pyproject`](../pyproject/SKILL.md), [`ruff-python`](../ruff-python/SKILL.md), [`squid-testing-python`](../squid-testing-python/SKILL.md).

## Canonical principles

### Versions & tooling

- **Python 3.12 minimum.** Default to the latest stable the team is using (3.13+ is fine).
- **Package manager:** [`uv`](../uv-python/SKILL.md) only. Never pip, poetry, or conda in project code.
- **Formatter + linter:** [`ruff`](../ruff-python/SKILL.md). Never black / flake8 / isort / pylint.
- **Build backend:** `hatchling` — see [`pyproject`](../pyproject/SKILL.md) for the `[build-system]` block.
- **Testing:** `pytest` + `pytest-asyncio` + `pytest-mock`. Full conventions live in [`squid-testing-python`](../squid-testing-python/SKILL.md).
- **Typing:** stdlib generics (PEP 585) — `list[int]`, `dict[str, Foo]`, never `typing.List`.

### Layout

These realise a **loose clean architecture**: infrastructure / serving / app / domain logic stay decoupled, but pragmatically — actionability over layer dogma. See [`layout.md`](layout.md) for the full tree, rationale, and anti-patterns. Headlines:

- Source under `src/<package_name>/`; **never** at the project root.
- Tests under `tests/{unit,integration}/` mirroring `src/` 1:1.
- Shared domain data structures (ODM / Pydantic models, enums): `entities/`.
- Narrow, module-local types: `<module>/types.py`.
- Domain code organised **flat by actionable concern** (e.g. `ingestion/`, `serving/`), not by dogmatic clean-architecture layers.
- Infrastructure dependencies unlikely to change (the chosen DB, orchestrator, observability tool) are **not** abstracted — no premature interfaces.
- Operator-facing entry points (one-off scripts, backfills, repro commands) under `scripts/`.

### Discipline (non-negotiable)

See [`discipline.md`](discipline.md) for rationale and concrete examples. Rules:

- **Datetimes are timezone-aware, UTC by default.** Reject naive `datetime` objects at every system boundary. Type them explicitly.
- **Type-annotate everything** — parameters, return types (including `-> None`), class attributes, module-level variables where inference is non-obvious.
- **Model data with Pydantic.** Every data structure that carries domain meaning — entities, DTOs, API/event payloads, config — is a `pydantic.BaseModel` (v2), or a Pydantic-based ODM `Document` for persisted entities. Not a `@dataclass`, `TypedDict`, or `NamedTuple` — reach for those only when a protocol or library contract forces it. Pydantic validates and coerces at every boundary; the alternatives silently accept garbage.
- **Logging first.** Any entry-point module (CLI, script, server main) calls `init_logger()` at module level before any logic. `print()` is banned in library code — always the project logger.
- **Pipelines are idempotent, retryable, and checkpointed.** If a run is killed halfway, re-running it is either a no-op or resumes from the last checkpoint.
- **Async for I/O, sync for CPU.** Mix only where a profile justifies it.

### Testing (headline; see [`squid-testing-python`](../squid-testing-python/SKILL.md) for depth)

- `tests/` mirrors `src/` 1:1.
- Files `test_*.py`, functions `test_*`.
- AAA pattern. Shared fixtures in `conftest.py`. Mocking via `pytest-mock` (`mocker`) — never hand-rolled.
- `@pytest.mark.parametrize` for table-driven tests.
- **Zero warnings.** `filterwarnings = ["error"]` in pytest config promotes them to errors; curate ignores, don't silence wholesale.
- **Do NOT unit-test infrastructure components** (orchestrator adapters, model-serving runtime, observability client). Those belong in integration tests.


## Python backend — module layout

Canonical tree for a Python backend package (inside a monorepo under `packages/<name>/`, or standalone at the repo root).

```
packages/<name>/                # or repo root for a single-package project
├── pyproject.toml              # hatchling + uv — see `pyproject` skill
├── Makefile                    # component targets (install / test / lint / build) — see `makefile-delegator`
├── .env.example                # component-local secrets + config surface
├── src/
│   └── <package_name>/         # importable module root; underscore_style, lower_case
│       ├── __init__.py
│       ├── logging.py          # init_logger() — called at module level by every entry point
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py     # pydantic-settings Settings loaded once at import
│       ├── entities/           # shared ODM / Pydantic models + enums (cross-module)
│       │   └── __init__.py
│       ├── <domain_a>/         # actionable concerns, flat
│       │   ├── __init__.py
│       │   ├── types.py        # module-local types; never imported upward
│       │   └── ...
│       └── <domain_b>/
│           ├── __init__.py
│           └── types.py
├── scripts/                    # operator-facing entry points; each calls init_logger()
│   └── run_*.py
└── tests/
    ├── conftest.py             # shared fixtures only
    ├── unit/
    │   └── <package_name>/     # mirrors src/<package_name>/ 1:1
    │       ├── test_*.py
    │       └── <domain>/
    │           └── test_*.py
    └── integration/
        └── <package_name>/     # mirrors src/<package_name>/ 1:1
            └── test_*.py
```

### Why this shape

- **`src/` layout (not flat).** Prevents accidental imports of an uninstalled package during development; forces the install step to work, which catches packaging bugs early.
- **`tests/` mirrors `src/` 1:1.** Easy to find tests for any module — `src/foo/bar.py` → `tests/unit/<pkg>/foo/test_bar.py`.
- **`entities/` vs per-module `types.py`.** `entities/` holds types that cross module boundaries (ODM models, shared enums). Per-module `types.py` holds narrow types used only within that module and its downstream callers. A type that only `foo/` uses goes in `foo/types.py`. If `bar/` ever needs it, move it to `entities/`.
- **Flat domain structure, not layered clean-architecture.** Don't mandate `services/` / `repositories/` / `use_cases/` / `adapters/` unless the domain actually needs them. Actionability beats dogma — a `users/` module that contains `users/store.py`, `users/api.py`, `users/types.py` is fine; forcing it into 4 layers is overhead.
- **Infrastructure is not abstracted.** The chosen DB, orchestrator, and observability tool are stable dependencies. Wrapping them behind interfaces "for swappability" is premature. Import them directly. Swap them by search-and-replace when the time comes.
- **`scripts/` for operator entry points.** Anything a human or a cron job invokes directly — not library code. Every file in `scripts/` calls `init_logger()` at module level before any logic.
- **`.env.example` is the config surface.** Every secret or runtime knob the service reads from the environment is listed here with a safe dummy value. `config/settings.py` reads them via `pydantic-settings`.

### Anti-patterns

- **Flat source at repo root** (`<package_name>/` directly under the repo with no `src/`). Makes `pip install -e .` / `uv sync` work lazily and hides packaging bugs.
- **`utils/` and `helpers/` modules.** These are dumping grounds that accumulate unrelated code. Put helpers next to their callers; if the same helper is needed in three places, promote it to `entities/` or a named module (`text/`, `time/`, …).
- **`types.py` at the package root.** Module-local types live in `<module>/types.py`. Cross-module types live in `entities/`. A root-level `types.py` conflates the two and becomes a grab bag.
- **One module per file.** Python is happy with many classes/functions per module. Split only when a file exceeds ~500 lines or when the responsibilities are genuinely orthogonal.
- **Tests grouped by type (`tests/unit/test_models.py`, `tests/unit/test_services.py`, `tests/unit/test_api.py`).** Mirror the source tree instead — grouping by type flattens the hierarchy and makes it hard to find the test for a specific module.
- **Shell scripts under `scripts/`.** Python packages are for Python. Shell helpers go under `bin/` at the repo root or in the Makefile directly.

## Python backend — discipline

The rules in the top-level SKILL.md, with rationale and concrete good-vs-bad examples. Every rule is enforceable by the `tester` agent.

### Datetimes are timezone-aware (UTC by default)

Naive datetimes are silent correctness bugs: they compare wrong across timezones, serialize ambiguously, and break when your dev machine's TZ differs from prod.

**Bad**

```python
from datetime import datetime

def created_before(ts: datetime) -> bool:
    return ts < datetime.now()          # naive; wrong after DST / across TZs
```

**Good**

```python
from datetime import datetime, UTC

def created_before(ts: datetime) -> bool:
    if ts.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return ts < datetime.now(UTC)
```

At every system boundary (HTTP request parsing, DB read, file import) either coerce to UTC or reject. Pydantic: use `datetime` with `AwareDatetime` or a validator that asserts `.tzinfo is not None`.

### Type-annotate everything

Annotations are cheap and they're the first line of defence the Tester reads. `ruff` / `mypy` / editor features all work off them.

- Annotate **every** parameter and return type, including `-> None`.
- Use PEP 585 built-ins (`list[int]`, `dict[str, Foo]`). Don't import `typing.List` / `typing.Dict`.
- Class attributes that aren't inferred from `__init__` get annotated at class level.
- Avoid `Any` unless you're at an external boundary you don't own. If you reach for `Any`, ask whether a `Protocol` (structural typing) or a narrow `TypedDict` (an external dict shape you don't own) would work — but model your *own* domain data with Pydantic (below), never `TypedDict`.

**Bad**

```python
def load(path, *, strict=True):
    ...
```

**Good**

```python
def load(path: Path, *, strict: bool = True) -> Config:
    ...
```

### Model data with Pydantic (not dataclasses / TypedDicts)

Domain data is modelled with `pydantic.BaseModel` (v2) — entities in `entities/`, request/response and event payloads, anything that crosses a process or I/O boundary. A `BaseModel` validates and coerces at construction, (de)serialises to/from JSON, and emits a JSON schema; a `@dataclass` or `TypedDict` does none of that and lets malformed data flow downstream until it crashes somewhere unrelated.

Escape hatch — use `@dataclass` / `TypedDict` / `NamedTuple` **only** when a protocol or library contract forces it: a `TypedDict` shape a third-party SDK's signature requires, a frozen `@dataclass` an external framework instantiates for you, or a hot-loop value object where you've *profiled* Pydantic's overhead and it actually matters. Leave a one-line comment naming the constraint.

**Bad**

```python
from dataclasses import dataclass

@dataclass
class Order:                        # no validation: total can be negative, currency can be ""
    id: str
    total: float
    currency: str
```

**Good**

```python
from decimal import Decimal
from pydantic import BaseModel, Field

class Order(BaseModel):
    id: str
    total: Decimal = Field(ge=0)    # rejected at construction if negative
    currency: str = Field(min_length=3, max_length=3)
```

### Logging first (`init_logger()` at module level)

Every entry point — `scripts/*.py`, the server `main.py`, the CLI root command — calls `init_logger()` **at module level** before any logic. This guarantees the first log line anyone emits (including third-party libs that log on import) goes through the project's formatter.

**Bad**

```python
## scripts/backfill.py
import my_service

def main() -> None:
    init_logger()            # too late; my_service already logged on import
    run_backfill()

if __name__ == "__main__":
    main()
```

**Good**

```python
## scripts/backfill.py
from my_service.logging import init_logger

init_logger()                # module-level, before any other project import

import my_service            # noqa: E402  (intentional post-logger import)

def main() -> None:
    my_service.run_backfill()

if __name__ == "__main__":
    main()
```

Library code never calls `print()`. Use the project logger (`logger = logging.getLogger(__name__)`). The only `print` allowed is a CLI's `rich.print`-equivalent for user-facing output — and even then, prefer `click.echo`, `typer` output, or direct writes to `sys.stdout`.

### Pipelines: idempotent, retryable, checkpointed

"Pipeline" = any batch/streaming job that ingests, transforms, or emits data. Three properties, non-negotiable:

- **Idempotent.** Running the same input twice produces the same output. Use deterministic IDs (hash of input, UUID5 from a namespace, composite natural keys) — not `uuid4()` unless you persist the mapping.
- **Retryable.** Every external call (DB write, API call, queue publish) is wrapped in a retry with backoff. Transient failures must not kill a run.
- **Checkpointed.** A run that is killed and restarted resumes from the last completed batch. Persist a cursor / watermark / last-processed-ID to durable storage between stages.

If you can't satisfy all three, you don't have a pipeline — you have a script, and it goes in `scripts/` with a big warning in the docstring.

### Pipelines: serving and triggering (orchestrator ergonomics)

Pipelines are executed by an orchestrator (Prefect / Airflow / Dagster / Temporal). Two rules for the dev loop, tool-agnostic:

- **Serve the worker in the background, trigger via `make`.** The orchestrator worker — the process that picks up deployments — runs as a background task (`make serve-workflows &`). Triggers go through wrapped `make run-<pipeline>` targets, never the raw orchestrator CLI, so `stdout`/`stderr` stream to the current terminal. If you edit pipeline code, kill the worker and re-serve — running workers don't auto-reload.
- **Make targets own the trigger, not the orchestrator CLI.** Rationale: debuggability. The Make-wrapped script streams logs back to your terminal; the orchestrator UI is for post-hoc inspection, not first-pass debugging.

Orchestrator-specific CLI usage (deployment names, worker config, UI endpoints) belongs in the project's own `CLAUDE.md` — this spec stays framework-agnostic.

### Async for I/O, sync for CPU

- I/O-bound code (HTTP, DB, queue, file) → `async def` + `await`. Use `asyncio.gather` for concurrency; avoid `asyncio.run_in_executor` unless wrapping sync libs.
- CPU-bound code (parsing, numerics, transformation) → plain `def`. Reaching for `async` here adds overhead for no benefit.
- Mixed workloads → split the module. Don't `await` around blocking code — it blocks the loop.
- Don't use `asyncio` for simple scripts where a blocking requests call would do. Async is a cost; it pays off only when concurrency matters.

### Config via pydantic-settings

- Define a single `Settings` class in `config/settings.py`.
- Load from environment variables (via `.env` in dev). Every variable has a default appropriate for the *test* environment, not prod.
- Export a module-level singleton: `settings = Settings()`.
- Never pass the whole `settings` object to deep call sites — pass the specific value. Makes tests easier.

```python
## config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://localhost:5432/test"
    max_retries: int = 3

settings = Settings()
```

### Infrastructure is imported, not abstracted

Don't write a `DatabaseAdapter` interface with a `PostgresAdapter` implementation unless you have a second adapter coming in the next sprint. Import `sqlalchemy` / `psycopg` / `beanie` directly. If the DB ever changes, grep and replace.

The same goes for orchestrators (Prefect / Airflow / Dagster), observability (OpenTelemetry / logfire), and model-serving (vLLM / TGI / Ollama). Wrap only the parts you actually customise.

This is not anti-abstraction — it's anti-premature abstraction. If a real swap happens, introduce the interface then. You'll design it better with a real second implementation in hand.

### Testing discipline (reminder)

- **Unit tests never touch infrastructure.** No real DB, no real network, no real clock. Use `mocker`.
- **Integration tests do touch infrastructure** — real Postgres / Mongo / Redis via testcontainers or a dev-compose stack. Keep them under `tests/integration/`, run separately from unit tests.
- **Zero warnings.** If a test emits a `DeprecationWarning`, fix it or add a narrow `filterwarnings` ignore with a `TODO:` and a date.
- See [`squid-testing-python`](../../squid-testing-python/SKILL.md) for depth.
