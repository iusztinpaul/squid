---
name: pyproject
description: pyproject.toml opinions — `[project]` metadata, `[build-system]`, entry points / scripts, `[tool.*]` configuration for ruff / pytest / mypy, dependency groups. TRIGGER when authoring or editing pyproject.toml. SKIP for setup.py-only or conda-only projects.
---

# pyproject.toml

Opinionated `pyproject.toml` structure for Python packages. Pairs with [`uv-python`](uv-python.md) (the tool that reads it) and [`ruff-python`](ruff-python.md) (owns the `[tool.ruff]` block in depth).

## When to use

- Authoring a new `pyproject.toml`.
- Adding `[tool.*]` configuration for ruff / pytest / mypy / coverage.
- Wiring `[project.scripts]` entry points.
- Switching a project from setup.py to pyproject.toml.

## When NOT to use

- `setup.py`-only projects — the opinions don't transfer 1:1.
- conda-forge recipes — those have their own metadata convention.
- Non-Python projects.

## Canonical opinions

Reference file: [canonical `pyproject.toml`](#canonical-pyprojecttoml-python-backend) below. Section by section:

### `[build-system]`

- **`hatchling`** is the default build backend. Don't reach for `setuptools` unless you need a C extension or a feature hatchling doesn't cover.
- `requires = ["hatchling"]` — no version pin; hatchling itself is ABI-stable enough.

### `[project]`

- **Dynamic version via hatch** is allowed but not required. Static `version = "0.1.0"` is fine; bump manually on release.
- **`requires-python = ">={major}.{minor}"`** — match the team's minimum supported version (3.12 currently).
- **`dependencies`** is the runtime dependency list. Keep it minimal. Dev tools go in `[dependency-groups].dev`.
- **`authors` / `maintainers`** — fine to include; not required for internal packages.

### `[project.scripts]` / entry points

Expose CLIs as entry points (`my-cli = "my_pkg.cli:main"`) so `uv run <cli-name>` works without specifying the module. After `uv sync`, users run `uv run my-cli --help`. See [`cli-tool-python`](cli-tool-python.md) for the CLI conventions themselves.

### `[dependency-groups]` (PEP 735)

**Use these for dev/test/lint deps.** Do **not** use `[project.optional-dependencies]` for them — that's a consumer-facing install surface (`pip install my-pkg[extras]`), not a dev convenience. Group contents: [`uv-python`](uv-python.md). Additional groups (`docs`, `type`, etc.) are fine — install per-group via `uv sync --group docs`.

### `[tool.hatch.build.targets.wheel]`

`packages = ["src/my_pkg"]` declares the src/ layout to hatchling. Non-negotiable when your source is under `src/` (which it should be — see [`python-backend`](python-backend.md)).

### `[tool.ruff]`

Full config in [`ruff-python`](ruff-python.md). Headline: `target-version` pinned to the same Python minor as `requires-python` (e.g. `py312`).

### `[tool.pytest.ini_options]`

Opinionated, non-negotiable (block in the canonical file):

- **`testpaths`** — pytest doesn't crawl the whole repo looking for tests.
- **`-ra`** — show summary of all non-passing outcomes at the end; fast feedback.
- **`--strict-markers`** — unknown `@pytest.mark.foo` becomes an error, not a silent no-op.
- **`asyncio_mode = "auto"`** — `async def test_*` functions run automatically; no decorator needed.
- **`asyncio_default_fixture_loop_scope = "function"`** — each test gets its own event loop; avoids cross-test pollution. Override per-fixture when you want a session loop.
- **`pythonpath = ["src"]`** — imports resolve against `src/` without requiring an editable install first; without it pytest can't import `my_pkg` until `uv sync` has run.
- **`filterwarnings = ["error"]`** — warnings promote to errors. Curate exceptions explicitly, each with a `TODO:` and a target date; don't silence wholesale.

## Environment-specific dependency gating

When optional runtime deps depend on project choices (datastore, orchestrator, LLM adapter), declare them in a dedicated group and install per-project:

```toml
[dependency-groups]
mongo = ["beanie>=1.26", "pymongo[srv]>=4.8"]
postgres = ["sqlalchemy>=2.0", "psycopg[binary]>=3.2"]
prefect = ["prefect>=3"]
```

Then the Makefile's `install` target picks the right group:

```makefile
install:
    uv sync --group mongo --group prefect
```

## Cross-references

- [`uv-python`](uv-python.md) — how `uv` reads this file and what `uv add/sync/build/publish` do.
- [`ruff-python`](ruff-python.md) — the full `[tool.ruff]` block.
- [`python-backend`](python-backend.md) — the broader package layout.


## Canonical `pyproject.toml` (Python backend)

Copy this, adjust the placeholders, keep the structure.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-pkg"
version = "0.1.0"
description = "A short sentence describing the package."
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }                       # or "Apache-2.0", "Proprietary", ...
authors = [
    { name = "Your Name", email = "you@example.com" },
]
keywords = []
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

## Runtime deps only. Dev/test go in [dependency-groups].
dependencies = [
    "pydantic>=2.8",
    "pydantic-settings>=2.4",
    "httpx>=0.27",
]

## ----- CLI entry points (optional) -----

[project.scripts]
my-cli = "my_pkg.cli:main"

## ----- Dev/test/lint deps (PEP 735) -----

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.23",
    "pytest-mock>=3.12",
    "ruff>=0.15",
    "pre-commit>=4",
]

## Additional groups for environment-specific deps (install with `uv sync --group mongo`)
## mongo = ["beanie>=1.26", "pymongo[srv]>=4.8"]
## postgres = ["sqlalchemy>=2.0", "psycopg[binary]>=3.2"]
## prefect = ["prefect>=3"]

## ----- Build backend config -----

[tool.hatch.build.targets.wheel]
packages = ["src/my_pkg"]

## ----- ruff: paste the [tool.ruff] blocks from ruff-python.md; target-version matches requires-python -----

## ----- pytest -----

[tool.pytest.ini_options]
testpaths = ["tests/unit", "tests/integration"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-ra --strict-markers"
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
pythonpath = ["src"]
filterwarnings = ["error"]

## ----- (optional) coverage -----

## [tool.coverage.run]
## source = ["src/my_pkg"]
## branch = true

## [tool.coverage.report]
## show_missing = true
## skip_covered = true
## exclude_lines = [
##     "pragma: no cover",
##     "if TYPE_CHECKING:",
## ]
```

### Pitfalls to avoid

- **Don't set `version = "0.0.0"`.** Start at `0.1.0` — 0.0.x reads as "not started" on PyPI and in dependency resolvers.
- **Don't duplicate ruff / pytest config in separate files** (`ruff.toml`, `pytest.ini`) when you already have `pyproject.toml`. One config surface.
