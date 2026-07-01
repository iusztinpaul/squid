---
name: uv-python
description: uv conventions for Python projects — `uv add` vs `uv sync`, lockfile discipline, workspaces, `uv run` for entry-point commands, `uvx` for one-shot tools. TRIGGER when managing Python dependencies or bootstrapping a uv-managed project. SKIP for pip / poetry / conda projects.
---

# uv for Python

Opinionated `uv` usage. uv is the only supported package/project manager in this team — not pip, poetry, or conda.

## When to use

- Adding, removing, or upgrading Python dependencies.
- Bootstrapping a Python project (new `pyproject.toml`, first install).
- Running Python scripts or tools (`uv run`, `uvx`).
- Building wheels / publishing packages.

## When NOT to use

- Projects already standardised on pip / poetry / conda — the cost of the switch needs its own decision.
- Non-Python ecosystems.
- Global Python version management — that's `uv python install`, covered but rarely needed per-project.

## Canonical commands

### Project lifecycle

| Command | When |
|---|---|
| `uv sync` | **Install/refresh** the venv from `pyproject.toml` + `uv.lock`. Run on checkout, after pulling changes that touched deps, and after `uv add/remove`. |
| `uv add <pkg>` | Add a runtime dependency. Edits `pyproject.toml` under `[project.dependencies]`, updates `uv.lock`, and syncs the venv. |
| `uv add --group dev <pkg>` | Add a dev/test dependency under `[dependency-groups].dev` (PEP 735). **Do not** use `[project.optional-dependencies]` — groups are the modern replacement. |
| `uv remove <pkg>` | Inverse of `uv add`. |
| `uv lock` | Regenerate `uv.lock` without syncing. Usually you don't need this explicitly — `uv add/remove/sync` locks for you. |
| `uv build` | Build wheel + sdist into `dist/`. Backend is whatever `[build-system]` declares (`hatchling` in our template). |
| `uv publish --token $UV_PUBLISH_TOKEN` | Publish `dist/*` to PyPI. CI-only — never locally. |

### Running things

| Command | When |
|---|---|
| `uv run python <args>` | Run Python inside the project venv without activating it. Replaces `source .venv/bin/activate && python`. |
| `uv run pytest` / `uv run ruff` / `uv run <tool>` | Run any dev dependency installed via `[dependency-groups].dev`. |
| `uv run <script>` | If `[project.scripts]` declares an entry point, `uv run <script-name>` invokes it with the venv. |
| `uvx <tool>` | Run a tool **from PyPI** without adding it to the project — one-shot. Equivalent to `pipx run`. Use for `uvx copier`, `uvx ruff` (when the project doesn't own ruff), `uvx openapi-spec-validator`. |
| `uv tool install <tool>` | Install a CLI tool persistently for the user (not the project). Use when you want `copier` in your PATH without typing `uvx`. |

### Running from a monorepo root

In a monorepo, target a component's environment without `cd`:

```bash
uv --directory packages/<c> run <cmd>            # from repo root
cd packages/<c> && uv run <cmd>                  # equivalent, stateful
```

Prefer `--directory` inside `make` recipes and in one-shot commands; prefer `cd` once at the start of an interactive session.

### Python version management

| Command | When |
|---|---|
| `uv python install 3.12` | Install a specific Python interpreter. |
| `uv python pin 3.12` | Pin the project to a Python version — writes `.python-version`. |

## Lockfile discipline

- **`uv.lock` is committed.** It's deterministic (given the same `uv` version and `requires-python`), reproducible across machines, and is the source of truth for `uv sync`.
- Don't edit `uv.lock` by hand. `uv add/remove/lock` is the only writer.
- If `uv.lock` conflicts during a merge, resolve by re-running `uv lock` on the merged `pyproject.toml`. Don't cherry-pick hunks.
- Lockfile drift is a CI gate: `uv lock --check` in CI fails the build if the lockfile is stale relative to `pyproject.toml`.

## Dependency groups, not optional-dependencies

PEP 735 `[dependency-groups]` is the modern way to declare dev/test/lint deps. `[project.optional-dependencies]` is for *consumers* who `pip install my-pkg[extra]`; it's the wrong place for dev tools.

```toml
# pyproject.toml
[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-asyncio",
    "pytest-mock",
    "ruff>=0.15",
    "pre-commit",
]
```

`uv sync` installs the default groups automatically. To add more groups (say `docs`), use `uv add --group docs sphinx` and `uv sync --group docs` when you need them.

## Workspaces: not used by default

uv supports `[tool.uv.workspace]` for multi-package monorepos. **We do not use it by default** — in our monorepo, each component has an independent `pyproject.toml` and lockfile. Workspaces make sense when multiple packages share a common dep graph and iterate together; most monorepos where languages differ per component don't benefit.

If a project *does* want workspaces, document it in the project's root `CLAUDE.md`, not here.

## Common recipes

**Bootstrap a new Python package:**

```bash
uv init --package --name my-pkg --python 3.12
cd my-pkg
uv add httpx pydantic
uv add --group dev pytest ruff pre-commit
uv sync
```

**Run the full dev loop:**

```bash
uv sync                           # ensure venv matches lockfile
uv run ruff format
uv run ruff check
uv run pytest -q
uv build                          # if publishing
```

**Clean a stale venv:**

```bash
rm -rf .venv && uv sync
```

**One-shot a tool without installing it:**

```bash
uvx copier copy <src> <dst>
uvx openapi-spec-validator api.yaml
```

## Anti-patterns

- **`pip install` inside a uv project.** Breaks lockfile discipline. Use `uv add` or `uv pip install` (if you really must) — never plain `pip`.
- **Activating the venv (`source .venv/bin/activate`).** Works, but `uv run` is less error-prone — no state in your shell.
- **Committing `.venv/`.** Never. It's a build artifact, gitignored.
- **Using `[project.optional-dependencies]` for dev tools.** That's for downstream consumers. Use `[dependency-groups]`.
- **Forgetting to `uv sync` after pulling a `pyproject.toml` change.** The venv silently lags. Tests fail mysteriously. `uv sync` as part of your `make install`.
- **Mixing `uv` and `poetry` in the same repo.** Pick one per project. The tools don't share lockfile formats; keeping both is a recipe for drift.
