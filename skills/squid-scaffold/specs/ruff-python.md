---
name: ruff-python
description: ruff configuration opinions — line length, selected rules, format defaults, lint/format split, pyproject vs ruff.toml placement. TRIGGER when writing or editing ruff config, or when a new Python project needs lint/format setup. SKIP for flake8 / black / pylint projects.
---

# ruff for Python

Opinionated `ruff` setup for Python 3.12+ projects. ruff replaces black, flake8, isort, pyupgrade — one tool, one config block, two commands.

## When to use

- Bootstrapping lint/format in a new Python project.
- Editing an existing `[tool.ruff]` block.
- Rationalising a project still running black + flake8 + isort separately.

## When NOT to use

- Projects standardised on black / flake8 / pylint that aren't ready to switch.
- Non-Python ecosystems.

## Decision tree

- **Config in `pyproject.toml`** (default) — one file, one source of truth, works with `uv` / hatchling out of the box.
- **Standalone `ruff.toml` / `.ruff.toml`** — only when the project doesn't have a `pyproject.toml` (monorepo root with no package, shared tooling dir).

## Canonical principles

### 1. One ruff, two commands

```bash
uv run ruff format <paths>      # the formatter (replaces black)
uv run ruff check  <paths>      # the linter  (replaces flake8 / isort / pyupgrade)
```

They're separate passes with separate rules — don't blur them in your head or your Makefile.

### 2. Fix before check

During an inner dev loop, run the `--fix` / writing variants first so auto-fixable issues don't surface as false errors:

```bash
uv run ruff format                # writes
uv run ruff check --fix           # writes
uv run ruff format --check        # asserts (no write)
uv run ruff check                 # asserts (no write)
```

CI runs only the asserting variants — drift is a failure, not something CI should silently paper over. See [`makefile-delegator`](../makefile-delegator/SKILL.md#9-fix-before-check-ordering-manual-loop) for how this wires into `make`.

### 3. Canonical `[tool.ruff]` block

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
extend-exclude = ["migrations", "generated_client"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "UP",   # pyupgrade (PEP 585, PEP 604)
    "SIM",  # flake8-simplify
    "RUF",  # ruff-specific
]
ignore = [
    "E501",    # line too long — the formatter owns this
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py"   = ["S101"]   # assert is the whole point of tests
"scripts/**/*.py" = ["T201"]   # operator scripts may print if they really must

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

- **`line-length = 100`** — modern screens, cheap horizontal space. Pick one and stop arguing.
- **`target-version` must match `requires-python`** in `[project]`; otherwise ruff's `UP` rules will suggest syntax the runtime can't parse.
- **`select` is an allow-list, not a deny-list.** Adding a rule family is a deliberate choice; review it together, don't cargo-cult.
- **`extend-exclude`** — generated files (OpenAPI clients, DB migrations) should never be lint-gated.

### 4. Format rules are not opinionated — accept the defaults

ruff's formatter is a black-compatible reimplementation. Accept the defaults. The only options worth setting are `quote-style = "double"` and `indent-style = "space"`. Don't try to recreate black's idiosyncrasies (`skip-string-normalization`, custom trailing-comma rules); let the tool win.

### 5. Keep the config small

If `[tool.ruff.lint]` grows past ~30 lines, it's doing too much. Prune:

- Remove `ignore` entries once the codebase is clean.
- Remove `per-file-ignores` that no longer match any file.
- Prefer `# noqa: RULE  # reason` with a rationale on the one offending line over a project-wide ignore.

## Anti-patterns

- **Running black alongside ruff.** They'll fight on edge cases. Pick one — ruff is the team default.
- **Wholesale `ignore = ["E", "W", "F"]` to quiet a noisy codebase.** Mask real bugs. Narrow the rules you actually want to keep; fix the rest.
- **`select = ["ALL"]`.** ruff has hundreds of rules. Opt in deliberately. `ALL` produces noise that buries signal.
- **Hand-tuning the formatter** (custom quote rules, disabling string normalisation). You lose the benefit of a standard formatter. Accept defaults.
- **Stale `per-file-ignores`** that outlive the files they pointed at. Lint your lint config periodically.
- **Running `ruff check` without `--fix` during local dev.** Slower inner loop; auto-fixable issues show up as errors you then fix by hand. Fix before check.
