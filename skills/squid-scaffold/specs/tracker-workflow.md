---
name: tracker-workflow
description: File-based task tracker format — one markdown file per task under `tasks/`, with a `status:` frontmatter tag (pending → in-progress → done; done files are moved into `tasks/done/`) and a `## Log` section. The Tasks Plan IS the set of `tasks/<NNN>-<slug>.md` files. Used by the `/squid-plan`, `/squid-implement-task`, and `/squid-implement-night` pipelines. TRIGGER when creating, updating, or completing task files under `tasks/`, or when the user asks how this project tracks work. SKIP for projects using GitHub Issues as the primary tracker (`TRACKER_MODE: gh` in `AGENTS.md`).
---

# File-based task tracker

The default tracker is plain markdown files under `tasks/`, committed to the repo. **One file per atomic task**, with its state carried in a `status:` frontmatter tag. The **Tasks Plan is the set of these files** — there is no separate plan document. GitHub Issues is the opt-in alternative (`TRACKER_MODE: gh`).

## When to use

- The project chose the file-based tracker at scaffold time (`TRACKER_MODE: file`, the default — declared in `AGENTS.md`'s "Agent Team & Pipeline" section).
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

Only **open** tasks (pending + in-progress) live at the top level of `tasks/`; **completed** tasks are moved into `tasks/done/`. The filename never carries state — the `status:` field does — but `tasks/done/` keeps the active list to just what's still open.

`NNN` is a zero-padded, monotonic counter that is **never reused**. Allocate the next number by scanning **both** locations so a moved-out done task doesn't free its number for reuse:

```bash
ls tasks/ tasks/done/ 2>/dev/null | grep -oE '^[0-9]+' | sort -n | tail -1   # next = this + 1
```

## Task file shape

```markdown
---
id: 003-search-ui
feature: search          # the feature slug this task belongs to
status: pending          # pending | in-progress | done
---

# Search UI

## Scope
{1–2 sentences — one atomic, independently-shippable unit of work.}

## Acceptance criteria
- [ ] ...

## Out of scope
- ...

## Log
### [PA] 2026-04-27 12:30 — Grooming
...
```

## Status lifecycle

`status:` is the single source of truth for state; transitions are edits to that field. Pending and in-progress files stay at the top level of `tasks/`; completing a task additionally moves the file into `tasks/done/`:

- **PA grooming** writes the file with `status: pending` (at the top level of `tasks/`).
- **SWE** starts the task → set `status: in-progress` (file stays put — no move yet).
- After the **Tester** PASSES and the task is committed → set `status: done` **and `git mv` the file into `tasks/done/` in that same commit**.

The **Tasks Plan** for a feature = its `tasks/<NNN>-*.md` files with `status: pending`, processed in `NNN` order. `/squid-implement-night` builds every pending task in the feature's worktree; `/squid-implement-task` can target one or several by ref.

## The `## Log`

Every agent appends timestamped, append-only entries to the task's `## Log`: `### [ROLE] YYYY-MM-DD HH:MM — subject`. Roles: `PA`, `SWE`, `Tester`, `PR Reviewer`, `On-Call`. Never rewrite — only append.

## Index of supporting files

_(None — this spec is self-contained.)_

## Canonical principles

- **The `status:` tag is the state.** pending → in-progress → done, edited in place. The filename never carries state. On completion the file also moves to `tasks/done/` — so the top level of `tasks/` lists only open work — but `status: done` in the frontmatter, not the folder, is what marks it done.
- **`NNN` is never reused.** Allocate the next number by scanning both `tasks/` and `tasks/done/` (`ls tasks/ tasks/done/`), so archiving a done task doesn't free its number.
- **One task = one file.** Rollup tasks (from a PA REJECT or PR-Reviewer Blockers) are new `tasks/<NNN>-<slug>.md` files, `status: pending`.
- **The tasks ARE the plan.** No separate plan document — the per-task files, ordered by `NNN`, are the Tasks Plan.
- **Append, never rewrite, the Log.** It's the cross-pipeline audit trail.
- **`TRACKER_MODE` is the default.** `AGENTS.md` sets the project-wide default (file vs gh); `/squid-plan`'s gate confirms it per feature and can override for a one-off plan without rewriting `AGENTS.md`.
