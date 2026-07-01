---
name: pre-commit-hooks
description: Project-side git hook conventions — which framework (`pre-commit` for Python-led repos, `lefthook` for polyglot, `husky` + `lint-staged` for TS-only), what runs in `pre-commit` vs `pre-push`, the escape-hatch policy. TRIGGER when adding hooks to a freshly scaffolded project, or when retrofitting hooks into a repo that doesn't have any. SKIP for the Claude Code agent guardrails — those live in `.claude/settings.json` (see the [`git-guardrails`](../../git-guardrails/SKILL.md) skill).
---

# Pre-commit hooks

Project-side hooks fire on the developer's machine **and** in CI when the same hook framework runs as a check. They catch lint/format/type errors before they hit the PR, keep the diff focused, and make `make pre-commit` a meaningful target. They are **not** the same thing as Claude Code's `PreToolUse` hooks (those block agent commands; see [`git-guardrails`](../../git-guardrails/SKILL.md)).

## When to use

- Bootstrapping a new repo where the team agrees lint/format errors should not enter PR review.
- Retrofitting hooks into an existing repo that has been getting noisy PRs.
- Standardising hooks across a polyglot monorepo where each language already has a fixer.

## When NOT to use

- Solo prototypes where ceremony exceeds value — just run `make format-fix` manually.
- Repos where the team has already decided they prefer CI-only enforcement (slower feedback, but skips the local-install friction).

## Decision tree

```
1) Is the repo Python-only or Python-led (polyglot but Python is the dominant language)?
   → use pre-commit (https://pre-commit.com). It's the de-facto Python ecosystem standard
     and works across languages too.

2) Is the repo TypeScript-only?
   → use husky + lint-staged. Native to the npm ecosystem, no Python prerequisite.

3) Is the repo polyglot with no dominant language (e.g., Python + Go + TS)?
   → use lefthook (https://github.com/evilmartians/lefthook). Single binary, language-
     agnostic, faster than pre-commit on large polyglot trees.

4) None of the above feel right?
   → don't ship hooks. Pick CI checks instead. Hook frameworks impose install friction;
     don't pay it without a clear reason.
```

## Canonical principles

### What runs in `pre-commit` vs `pre-push`

The split exists because **fast checks belong on every commit**, **slow checks belong before the network round-trip to origin**.

| Stage | What runs | Why |
|---|---|---|
| `pre-commit` | format check, lint check, **only on changed files**, max ~5s | Cheap; runs constantly. If it's slow, devs disable it. |
| `pre-push` | full unit-test suite, type-check, **on the whole repo** | Slower; runs once per `git push`. Good gate before CI sees it. |
| `commit-msg` | conventional-commit / message-format lint, if the team enforces one | Single regex; effectively free. |

**Never run integration tests, e2e tests, or full builds in either hook.** That belongs in CI. Hooks must finish in seconds; otherwise `--no-verify` becomes muscle memory and the whole layer is dead.

### Scope hooks to changed files

`lint-staged` (TS) / `pre-commit` with `pass_filenames: true` / `lefthook` with `{staged_files}` — all support file-scoping. Use it. A 30-second `eslint .` pre-commit on a large repo trains people to bypass; a 1-second `eslint $(staged-ts)` does not.

### Escape-hatch policy

`--no-verify` exists. Don't take it away. Make it a deliberate choice:

- **Allowed:** when the dev knows the hook is wrong (e.g., format check disagrees with prettier-fix).
- **Allowed:** when committing WIP to a personal branch they're about to rebase.
- **Not allowed:** as standard practice. CI re-runs the same hooks; bypassing local just defers the failure.

The [`git-guardrails`](../../git-guardrails/SKILL.md) skill blocks `git push --no-verify` (see Rule 3) — that's deliberate. The dev still has the local commit-time escape hatch; what they can't do is *push* unverified.

### Hook config lives at the repo root

- `pre-commit`: `.pre-commit-config.yaml` at the root.
- `lefthook`: `lefthook.yml` at the root.
- `husky`: `.husky/` directory at the root + `lint-staged` config in `package.json`.

For monorepos: hooks invoke per-component fixers via the root `Makefile` (`make format-check-<component>`, `make lint-check-<component>`). Don't write hook configs that duplicate Makefile logic — call into it.

## Canonical configs (sketches)

### `pre-commit` (Python-led)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: format-check
        name: format check
        language: system
        entry: make format-check
        pass_filenames: false
      - id: lint-check
        name: lint check
        language: system
        entry: make lint-check
        pass_filenames: false
      - id: unit-tests
        name: unit tests
        language: system
        entry: make unit-tests
        pass_filenames: false
        stages: [pre-push]   # not pre-commit — too slow
```

Bootstrap: `uvx pre-commit install --hook-type pre-commit --hook-type pre-push`. Add to `make install` so first-time setup wires it automatically.

### `lefthook` (polyglot)

```yaml
# lefthook.yml
pre-commit:
  parallel: true
  commands:
    format-check:
      glob: "*.{py,ts,tsx,go}"
      run: make format-check
    lint-check:
      glob: "*.{py,ts,tsx,go}"
      run: make lint-check

pre-push:
  commands:
    unit-tests:
      run: make unit-tests
```

Bootstrap: `lefthook install`. Distributed via `go install` (Go projects) or `npm i -D lefthook` (others).

### `husky` + `lint-staged` (TS-only)

```json
// package.json
{
  "scripts": {
    "prepare": "husky"
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"]
  }
}
```

```sh
# .husky/pre-commit
npx lint-staged

# .husky/pre-push
npm run test
```

Bootstrap: `npm i -D husky lint-staged && npx husky init`.

## Anti-patterns

- **Running the full test suite in `pre-commit`.** Anything > 5s makes `--no-verify` standard. Move it to `pre-push` or CI.
- **Hooks that auto-fix without telling you.** `lint-staged` re-stages files it modified; that's fine. But a hook that silently rewrites code and lets the commit succeed produces commits with diffs the dev didn't review. Prefer `--check` modes that block; let the dev re-run the fixer explicitly.
- **Different hook frameworks per component in one monorepo.** Pick one. The friction of "which hook runner is this folder using" exceeds whatever per-language gain you got.
- **Skipping the install step in `make install`.** If hooks aren't installed, they don't run. New contributors must hit them on day one.
- **Mixing project-side hooks with Claude Code agent guardrails.** Different layers, different concerns. Don't put `git push --force` blocking in `pre-push` (it would also fire for legitimate force-pushes by humans on feature branches); use [`git-guardrails`](../../git-guardrails/SKILL.md) instead.
