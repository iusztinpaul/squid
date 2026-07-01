---
name: cli-tool-python
description: Python CLI tool conventions — Click/typer choice, entry points in pyproject.toml, `init_logger()` at module level, --help discipline, exit codes, config via settings module (not Click env-var magic). TRIGGER when building a command-line tool in Python. SKIP for library-only packages or full HTTP services.
---

# Python CLI tool

Opinionated starter for Python command-line tools. Builds on [`python-backend`](../python-backend/SKILL.md) (layout, logging, types, testing) and [`pyproject`](../pyproject/SKILL.md) (entry-point config).

## When to use

- Building a CLI that users invoke as `my-tool <command>`.
- Adding a CLI surface to an existing Python package.

## When NOT to use

- Library-only packages (no `__main__`) — just use [`python-backend`](../python-backend/SKILL.md).
- HTTP APIs — use [`fastapi-service`](../fastapi-service/SKILL.md).
- MCP servers — use [`fastmcp-server`](../fastmcp-server/SKILL.md).
- One-off scripts — those live under `scripts/` per [`python-backend`](../python-backend/SKILL.md), not a framework-wrapped CLI.

## Decision tree

- Simple flag/arg parsing, no nested subcommands → `argparse` (stdlib, no dep).
- Nested subcommands, rich `--help`, shell completion → **Click** (default choice).
- Heavy type-hint-driven API, FastAPI-style dev experience → `typer` (wraps Click with better annotations).
- Full interactive UI → wrong spec; look at `textual` or [`go-tui`](../go-tui/SKILL.md).

## Canonical principles

### 1. Entry point lives in `pyproject.toml`

Never rely on `python -m my_pkg.cli` for user-facing invocation. Declare the script:

```toml
[project.scripts]
my-tool = "my_pkg.cli:cli"
```

Users install the package and get `my-tool` on their PATH. `uv run my-tool` works inside the project venv. See [`pyproject`](../pyproject/SKILL.md) for the full file shape.

### 2. `init_logger()` at module level, before any project import

Same rule as [`python-backend`](../python-backend/SKILL.md#logging-first-init_logger-at-module-level):

```python
## src/my_pkg/cli.py
from my_pkg.logging import init_logger

init_logger()                                  # before any project / framework import

import click                                   # noqa: E402
from my_pkg.commands import run_validation    # noqa: E402

@click.group()
def cli() -> None:
    """my-tool — short one-liner that renders as --help."""
```

### 3. One command = one Click function = one project function

Click command bodies are thin — they parse flags and delegate. Real work lives in a pure function the unit tests can call:

```python
@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--strict/--lenient", default=True)
def validate(path: Path, strict: bool) -> None:
    """Validate a config file."""
    result = run_validation(path, strict=strict)   # pure function — easy to unit-test
    if not result.ok:
        click.echo(result.message, err=True)
        raise click.exceptions.Exit(code=1)
```

Unit tests target `run_validation`. The Click wrapper gets one integration smoke test via `click.testing.CliRunner`.

### 4. Exit codes are explicit

| Code | Meaning |
|---|---|
| `0` | Success. |
| `1` | Application error (validation failed, file missing, API returned 4xx). |
| `2` | Usage error — Click emits this automatically for bad flags. |
| `>2` | Reserved for specific failure modes callers script around. Document per-command. |

Always `raise click.exceptions.Exit(code=N)` — never `sys.exit(N)` — so Click's cleanup (context teardown, resource close) runs.

### 5. Config via the project's settings module, not Click env-var magic

Click offers `envvar=` and `auto_envvar_prefix`. Don't use them in this project. Env-var-driven config goes through [`python-backend`](../python-backend/SKILL.md#config-via-pydantic-settings)'s `config/settings.py` (pydantic-settings). Single source of truth for env vars; the CLI reads from `settings`.

```python
from my_pkg.config import settings

@cli.command()
@click.option("--timeout", type=int, default=None)
def fetch(timeout: int | None) -> None:
    effective_timeout = timeout if timeout is not None else settings.default_timeout
    ...
```

CLI flags override settings when explicitly passed. Settings own the env-var surface and `.env.example` documents it.

### 6. `--help` is a first-class API

- Every command and every option gets a one-line `help=` description.
- The command's docstring is the primary `--help` output — treat it like documentation.
- `cli --help` and `cli <cmd> --help` must both render cleanly. Verify in code review.

### 7. Output: `click.echo`, not `print`

- `click.echo(msg)` for stdout; `click.echo(msg, err=True)` for stderr.
- Never mix `print()` with Click — `print` bypasses Click's stream handling and breaks `CliRunner` capture.
- Structured output (JSON for piping) goes through `json.dumps` + `click.echo`; don't hand-format.

### 8. Testing

```python
from click.testing import CliRunner
from my_pkg.cli import cli

def test_validate_rejects_bad_config(tmp_path):
    bad = tmp_path / "bad.yml"
    bad.write_text("not: [valid")
    result = CliRunner().invoke(cli, ["validate", str(bad)])
    assert result.exit_code == 1
    assert "invalid" in result.output.lower()
```

One `CliRunner` smoke test per command confirms the wiring. Real behavioural assertions target the underlying function (`run_validation`) — faster, clearer failures.

## Anti-patterns

- **Entry point via `python -m`.** Forces users to know the package path and disables shell completion. Always `[project.scripts]`.
- **Using Click's `envvar=` / `auto_envvar_prefix`.** Splits env-var config across two places (Click decorators + `settings.py`). Centralise in `settings.py`.
- **`print()` instead of `click.echo`.** Bypasses Click's stream handling and breaks `CliRunner` tests.
- **Deeply nested command groups for their own sake.** `my-tool foo bar baz qux` usually means the surface is too granular. Flatten.
- **Business logic inside the Click function body.** Pulls test assertions through `CliRunner`, which adds friction and hides coverage gaps.
- **`sys.exit(1)` instead of `raise click.exceptions.Exit(1)`.** Skips Click's cleanup; leaks resources in long-running groups.
