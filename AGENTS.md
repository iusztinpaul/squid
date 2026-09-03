# Squid: An Opinionated Software Factory for Claude Code

This repo **is** a Claude Code plugin. The contract layer is markdown — agents and skills; nothing else ships.

Consumers install it two ways:

1. `/plugin marketplace add iusztinpaul/squid && /plugin install squid@iusztinpaul` — global, all Claude Code sessions. The repo is a one-plugin marketplace (`.claude-plugin/marketplace.json`) named `iusztinpaul` (the GitHub account) cataloguing the `squid` plugin (the repo). The plugin's `source` is fixed to `github:iusztinpaul/squid`, so the install always fetches from GitHub even when the marketplace itself was added from a local path — relative-path plugin sources aren't supported on Claude Code v2.1.x when the marketplace lives on the local filesystem.
2. `claude --plugin-dir /path/to/squid` — for plugin-development sessions only; loads the plugin from the working tree without registering or installing anything.

Either way they get an opinionated agent team plus a `/squid-scaffold` flow that bootstraps new repos from a light spec library. The plugin's job is to teach Claude Code how to build software the way this team builds it.

> **For users of this plugin:** read [`README.md`](README.md). This file is for people editing the plugin itself.

## Key Principles You Will Respect All Over Your Work

- Prefer removing instructions over adding them; write docs, code, and rules with the minimum words that achieve the goal.
- Whenever you add a new rule within the memory (such as AGENTS.md), resources or skills, support it with a clear, concise explanation, plus a set of good and bad examples. Good examples: "a 200-token chunk size", "sub-100ms latency". Bad examples: "a powerful architecture", "a robust pipeline".

## What's in the repo

```
.
├── .claude-plugin/
│   ├── plugin.json                    # Claude Code plugin manifest (name, version, description)
│   └── marketplace.json               # one-plugin marketplace catalog so `/plugin install squid@iusztinpaul` works
├── agents/                            # five sub-agents
├── skills/
│   ├── squid-scaffold/                # /squid-scaffold — bootstrap a new repo (create) or audit drift (evaluate)
│   │   ├── evaluate.md                # mode=evaluate flow (E1–E4), loaded on demand
│   │   └── AGENTS_TEMPLATE.md         # template body /squid-scaffold distils into each project's AGENTS.md
│   ├── squid-plan/                    # /squid-plan — feature spec → approved Tasks Plan (+ worktree)
│   ├── squid-implement-task/          # /squid-implement-task — autonomous task loop (SWE↔Tester, commit each)
│   ├── squid-implement-night/         # /squid-implement-night — end-to-end pipeline (thin orchestrator)
│   ├── squid-review/                  # /squid-review — push + PA acceptance + PR-Reviewer
│   ├── squid-review-ci/               # /squid-review-ci — On-Call drives CI green
│   ├── squid-grilling/                # /squid-grilling — stress-test a plan (used inside /squid-plan; adapted from mattpocock/skills, MIT)
│   ├── squid-testing-python/          # test-writing conventions
│   │                                  # below: standalone, not wired into the pipeline
│   ├── squid-refactor/                # /squid-refactor — refactor planner
│   ├── squid-triage-issue/            # /squid-triage-issue — bug intake
│   ├── squid-architecture-review/     # /squid-architecture-review — audit
│   ├── squid-clean-docs/              # /squid-clean-docs — prose cleanup: docs, comments, docstrings
│   ├── squid-clean-memory/            # /squid-clean-memory — memory-file shrink: compress, dedupe, merge
│   ├── squid-clean-harness/           # /squid-clean-harness — .agents shrink: skills + resources, same logic fewer tokens
│   └── squid-write-skill/             # /squid-write-skill — skill-authoring reference (vendored from mattpocock/skills, MIT)
└── README.md                          # user-facing (install + what's inside)
```

The directory layout is what Claude Code's plugin loader expects natively: `agents/` and `skills/` at the plugin root. No custom path overrides in `plugin.json` — the loader scans those defaults.

## Editing conventions

- **Choosing an agent's model** — reasoning roles get `fable`, the code-writing role gets `opus`, the high-tool-call roles get `sonnet`; all pin `effort: high`. The rule is *who plans vs. who generates*: Fable earns its 2× price on judgment that runs once per feature (PA grooming, PR review) and loses money on token-heavy generation (see `README.md` → "Which model runs which agent"). Never put Fable on `software-engineer`. Accepted `model:` values are `sonnet` / `opus` / `haiku` / `fable`, a full model ID, or `inherit`; omitting the field means `inherit`.
- **Frontmatter is YAML, and it fails silently.** An unquoted value containing `": "` (e.g. `description: ... Output: a clean PR`) or starting with `[` (e.g. `argument-hint: [a] [b]`) is a parse error, and Claude Code then loads the skill with **every frontmatter field dropped** — no name, no description, no `disable-model-invocation`. Use a folded block scalar (`description: >-`) for prose, and quote any `argument-hint` that starts with `[`. Validate with `scripts/check-frontmatter.py` (see "Testing the plugin").
- **Editing a skill** — edit `skills/<name>/SKILL.md`. Co-locate supporting docs in the same dir if depth warrants it (but prefer single-file skills).
- **Adding a spec** — write `skills/squid-scaffold/specs/<name>.md`. Update the index in `skills/squid-scaffold/specs/README.md` and the spec-selection table (Step 2 of the flow in `skills/squid-scaffold/SKILL.md`) so `/squid-scaffold` knows when to pull it in.
- **Editing scaffold rules** — edit `skills/squid-scaffold/rules.md`, the single source of truth that both `/squid-scaffold` modes (`create` + `evaluate`) consume. `SKILL.md` and `AGENTS_TEMPLATE.md` only reference rule IDs — never re-inline a rule into them.
- **Editing the lifecycle** — the pipeline is defined by the skills (`squid-plan` / `squid-implement-task` / `squid-implement-night` / `squid-review` / `squid-review-ci`) and the agent contracts. Cross-cutting rules + the pipeline map live in `skills/squid-scaffold/AGENTS_TEMPLATE.md`, which `/squid-scaffold` bakes into each project's `AGENTS.md`.
- **Don't add language-specific build systems for the plugin contract** (no `pyproject.toml`, no `Makefile`, no `tests/`). The contract layer remains markdown.

## Companion plugin: caveman (optional)

Squid integrates with [caveman](https://github.com/JuliusBrussee/caveman) as an **optional** companion — a separate Claude Code plugin (`/plugin marketplace add JuliusBrussee/caveman && /plugin install caveman@caveman`). When it's installed Squid delegates to it at four touchpoints; when it's absent every touchpoint falls back to native behavior (mirroring the existing `commit-commands` pattern). Keep it optional — never make Squid hard-depend on it, and phrase each hook as "if the caveman plugin is installed…".

- **Commits** → `/caveman-commit` — `agents/software-engineer.md` (Commit section).
- **Reviews** → PR-Reviewer posts one-line `/caveman-review` comments on the PR, on top of the rollup — `agents/pr-reviewer.md` (Step 3b). The rollup stays the machine-readable routing artifact.
- **Memory compression** → `/caveman-compress` — offered by `/squid-scaffold` on the `AGENTS.md` it generates, run by `/squid-clean-memory` before de-duplicating, and by `/squid-clean-harness` for its wording pass.
- **Shorter replies** → caveman's own `SessionStart` hook; no Squid wiring. User-facing docs live in `README.md`; downstream projects learn of it via `AGENTS_TEMPLATE.md`.

## Spec-writing style (for `squid-scaffold/specs/`)

- **Opinions, not code.** Each spec states the rules (with rationale); it doesn't ship canonical files except as inline examples in markdown fences.
- **Five-section shape** for foundation specs: `When to use`, `When NOT to use`, `Decision tree`, `Canonical principles`, supporting content inline or in co-located docs.
- **Stubs are fine.** Most specs are still stubs with just the top-matter description. Flesh out as real usage reveals what matters; keep the rest terse until you need them.
- **Cross-reference, don't duplicate.** If `python-backend.md` needs uv guidance, it says "see `uv-python.md`" — don't transclude.

## Testing the plugin

- **Local Claude Code install (uncommitted):** `claude --plugin-dir /path/to/squid` — install path 2 above.
- **Local Claude Code install (committed):** in a scratch session, `/plugin marketplace add /path/to/squid && /plugin install squid@iusztinpaul` — fetches from GitHub (see install path 1), so push first.
- **Validate frontmatter:** `python3 scripts/check-frontmatter.py` (needs `pyyaml`). This is the guard — it parses every `agents/*.md` and `skills/*/SKILL.md`, and rejects unparseable YAML, a `name:` that disagrees with its filename, a missing `description:`, a non-string `argument-hint:`, and any `model:`/`effort:` value that isn't real. CI runs it on every push touching `agents/` or `skills/` (`.github/workflows/frontmatter.yml`).
- **Validate manifest:** `claude plugin validate .` only reads `.claude-plugin/marketplace.json`, never `agents/` or `skills/`, and checks field *types* but not *values* — `model: not-a-real-model` and `effort: banana` both pass. Prefer `scripts/check-frontmatter.py`.
- **Test `/squid-scaffold`:** run it in an empty directory and confirm it produces a sensible `AGENTS.md` (with `CLAUDE.md` symlinked to it, plus a `.agents/skills/` dir and a `.claude/skills → .agents/skills` symlink) and skeleton tree without writing any application source.
- **Test `/squid-implement-task`:** run it against a `/squid-scaffold`-generated project with one or more groomed tasks; confirm the SWE↔Tester loop runs and each task is committed on PASS.
- **Test `/squid-plan` → `/squid-implement-night`:** run `/squid-plan` with a feature spec (free-form text or a path to a `docs/features/*.md` file), approve the plan, then run `/squid-implement-night` and confirm it reaches a validated PR.

Testing this plugin means running the skills against real scratch targets.

## Publishing

Bump `version` in `.claude-plugin/plugin.json` whenever you ship changes that affect end users — without a bump Claude Code keeps the cached copy and `/plugin update` reports "already at the latest version". `scripts/release.sh patch` (or `minor` / `major` / explicit `X.Y.Z`) does the bump, commit, and tag from a clean `main`.

Then smoke-test from another machine (or a fresh Claude Code session): `/plugin marketplace update iusztinpaul && /plugin update squid@iusztinpaul`.

See `CONTRIBUTING.md` → "Releasing (maintainers)" for full usage, the manual fallback, and a note on how git tags actually reach GitHub.
