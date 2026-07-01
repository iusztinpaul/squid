---
name: pyproject
description: pyproject.toml opinions — `[project]` metadata, `[build-system]`, entry points / scripts, `[tool.*]` configuration for ruff / pytest / mypy, dependency groups. TRIGGER when authoring or editing pyproject.toml. SKIP for setup.py-only or conda-only projects.
---

# pyproject.toml

Opinionated `pyproject.toml` structure for Python packages. Pairs with [`uv-python`](../uv-python/SKILL.md) (the tool that reads it) and [`ruff-python`](../ruff-python/SKILL.md) (owns the `[tool.ruff]` block in depth).

## When to use

- Authoring a new `pyproject.toml`.
- Adding `[tool.*]` configuration for ruff / pytest / mypy / coverage.
- Wiring `[project.scripts]` entry points.
- Switching a project from setup.py to pyproject.toml.

## When NOT to use

- `setup.py`-only projects — the opinions don't transfer 1:1.
- conda-forge recipes — those have their own metadata convention.
- Non-Python projects.

## Canonical skeleton

See [`canonical.md`](canonical.md) for a full reference file. Headline structure:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "..."
version = "0.1.0"
description = "..."
requires-python = ">=3.12"
dependencies = [...]

[project.scripts]     # if the package exposes CLIs
my-cli = "my_pkg.cli:main"

[dependency-groups]   # PEP 735 — for dev/test/lint deps
dev = [...]

[tool.hatch.build.targets.wheel]
packages = ["src/my_pkg"]

[tool.ruff]
# line-length, target-version, lint rules — see ruff-python skill

[tool.pytest.ini_options]
# testpaths, asyncio_mode, filterwarnings — see below
```

## Canonical opinions (headline)

### `[build-system]`

- **`hatchling`** is the default build backend. Don't reach for `setuptools` unless you need a C extension or a feature hatchling doesn't cover.
- `requires = ["hatchling"]` — no version pin; hatchling itself is ABI-stable enough.

### `[project]`

- **Dynamic version via hatch** is allowed but not required. Static `version = "0.1.0"` is fine; bump manually on release.
- **`requires-python = ">={major}.{minor}"`** — match the team's minimum supported version (3.12 currently).
- **`dependencies`** is the runtime dependency list. Keep it minimal. Dev tools go in `[dependency-groups].dev`.
- **`authors` / `maintainers`** — fine to include; not required for internal packages.

### `[project.scripts]` / entry points

Expose CLIs as entry points so `uv run <cli-name>` works without specifying the module:

```toml
[project.scripts]
my-cli = "my_pkg.cli:main"
```

After `uv sync`, users run `uv run my-cli --help`. See [`cli-tool-python`](../cli-tool-python/SKILL.md) for the CLI conventions themselves.

### `[dependency-groups]` (PEP 735)

**Use these for dev/test/lint deps.** Do **not** use `[project.optional-dependencies]` for them — that's for downstream consumers.

```toml
[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-asyncio",
    "pytest-mock",
    "ruff>=0.15",
    "pre-commit",
]
```

Additional groups (`docs`, `type`, etc.) are fine — install per-group via `uv sync --group docs`.

### `[tool.hatch.build.targets.wheel]`

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/my_pkg"]
```

Declares the src/ layout to hatchling. Non-negotiable when your source is under `src/` (which it should be — see [`python-backend/layout`](../python-backend/layout.md)).

### `[tool.ruff]`

Full config in [`ruff-python`](../ruff-python/SKILL.md). Headline: `target-version` pinned to the same Python minor as `requires-python` (e.g. `py312`).

### `[tool.pytest.ini_options]`

Opinionated, non-negotiable:

```toml
[tool.pytest.ini_options]
testpaths = ["tests/unit", "tests/integration"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-ra --strict-markers"
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
pythonpath = ["src"]
filterwarnings = ["error"]
```

Rationale:

- **`testpaths`** — pytest doesn't crawl the whole repo looking for tests.
- **`-ra`** — show summary of all non-passing outcomes at the end; fast feedback.
- **`--strict-markers`** — unknown `@pytest.mark.foo` becomes an error, not a silent no-op.
- **`asyncio_mode = "auto"`** — `async def test_*` functions run automatically; no decorator needed.
- **`asyncio_default_fixture_loop_scope = "function"`** — each test gets its own event loop; avoids cross-test pollution. Override per-fixture when you want a session loop.
- **`pythonpath = ["src"]`** — imports resolve against `src/` without requiring an editable install first.
- **`filterwarnings = ["error"]`** — warnings promote to errors. Curate exceptions explicitly; don't silence wholesale.

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

- [`uv-python`](../uv-python/SKILL.md) — how `uv` reads this file and what `uv add/sync/build/publish` do.
- [`ruff-python`](../ruff-python/SKILL.md) — the full `[tool.ruff]` block.
- [`python-backend`](../python-backend/SKILL.md) — the broader package layout.


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

## ----- ruff -----

[tool.ruff]
target-version = "py312"
line-length = 100
extend-exclude = ["tests/fixtures"]

[tool.ruff.lint]
select = [
    "E", "F", "W",   # pycodestyle + pyflakes basics
    "I",             # isort
    "B",             # flake8-bugbear
    "UP",            # pyupgrade
    "SIM",           # flake8-simplify
    "RUF",           # ruff-specific
]
ignore = [
    # curate as needed
]

[tool.ruff.format]
quote-style = "double"

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

- **Don't put dev tools in `[project.optional-dependencies]`.** Use `[dependency-groups]` (PEP 735). Optional-deps are a consumer-facing install surface (`pip install my-pkg[extras]`), not a dev convenience.
- **Don't omit `pythonpath = ["src"]`** in the pytest config when using src-layout. Without it, pytest can't import `my_pkg` unless you've run `pip install -e .` or `uv sync` first.
- **Don't ship `filterwarnings = ["error"]` and a pile of hand-curated ignores with no dates.** Every ignore should have a `TODO:` and a target date to revisit.
- **Don't set `version = "0.0.0"`.** Start at `0.1.0` — 0.0.x reads as "not started" on PyPI and in dependency resolvers.
- **Don't duplicate ruff / pytest config in separate files** (`ruff.toml`, `pytest.ini`) when you already have `pyproject.toml`. One config surface.
