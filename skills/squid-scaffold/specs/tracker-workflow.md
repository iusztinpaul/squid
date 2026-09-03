---
name: tracker-workflow
description: File-based task tracker — one markdown file per task under `tasks/`, state in a `status:` frontmatter tag, done files moved into `tasks/done/`. TRIGGER when creating, updating, or completing task files under `tasks/`, or when the user asks how this project tracks work. SKIP for projects using GitHub Issues as the primary tracker (`TRACKER_MODE: gh` in `AGENTS.md`).
---

# File-based task tracker

## When to use

- `TRACKER_MODE: file` — the default, declared in `AGENTS.md`'s "Agent Team & Pipeline" section.
- You are creating, picking up, or completing a task.

## When NOT to use

- `TRACKER_MODE: gh` — use `gh issue ...` instead; issue state + labels carry status, one issue per task.

## Decision tree

```
Need to track a unit of work?
├── TRACKER_MODE: gh   → gh issue create / comment / close   (labels carry status)
└── TRACKER_MODE: file → a tasks/<NNN>-<slug>.md file with a status: tag (below)
```

## One file per task

`/squid-plan` splits a feature into atomic tasks and writes one file per task under `tasks/`:

```
tasks/
├── 002-search-endpoint.md      # status: in-progress
├── 003-search-ui.md            # status: pending
├── done/
│   └── 001-add-pagination.md   # status: done — moved here on completion
└── README.md                   # what this directory is
```

## Task file shape

```markdown
---
status: pending          # pending | in-progress | done
feature: search          # the feature slug this task belongs to
---

# Search UI

{Body = the PA's groomed spec: Tags / Depends on / Blocks, `## Scope`, `## Acceptance Criteria`,
`## User Stories` — the template lives in `agents/product-architect.md` → "Write the groomed spec".
The task id is the filename (`003-search-ui`).}

## Log
### [PA] 2026-04-27 12:30 — Grooming
...
```

## Status lifecycle

- **PA grooming** writes the file with `status: pending` (at the top level of `tasks/`).
- **SWE** starts the task → set `status: in-progress` (file stays put — no move yet).
- After the **Tester** PASSES and the task is committed → set `status: done` **and `git mv` the file into `tasks/done/` in that same commit**.

## Canonical principles

- **The `status:` tag is the state.** pending → in-progress → done, edited in place. The filename never carries state. On completion the file also moves to `tasks/done/` — so the top level of `tasks/` lists only open work — but `status: done` in the frontmatter, not the folder, is what marks it done.
- **`NNN` is never reused.** Zero-padded, monotonic. Allocate the next number by scanning **both** `tasks/` and `tasks/done/`, so archiving a done task doesn't free its number: `ls tasks/ tasks/done/ 2>/dev/null | grep -oE '^[0-9]+' | sort -n | tail -1` → next = this + 1.
- **One task = one file.** Rollup tasks (from a PA REJECT or PR-Reviewer Blockers) are new `tasks/<NNN>-<slug>.md` files, `status: pending`.
- **The tasks ARE the plan.** A feature's Tasks Plan = its `tasks/<NNN>-*.md` files with `status: pending`, processed in `NNN` order — no separate plan document.
- **Append, never rewrite, the Log.** Every agent appends `### [ROLE] YYYY-MM-DD HH:MM — subject` entries to `## Log` (roles: `PA`, `SWE`, `Tester`, `PR Reviewer`, `On-Call`). It's the cross-pipeline audit trail.
- **`TRACKER_MODE` is the default.** `AGENTS.md` sets the project-wide default (file vs gh); `/squid-plan`'s gate confirms it per feature and can override for a one-off plan without rewriting `AGENTS.md`.
