---
name: squid-refactor
description: >-
  Plan a refactor as an ordered, commit-grain Tasks Plan with structural acceptance criteria
  (suite green at every step, no behaviour diff) that `/squid-implement-night` can execute
  end-to-end.
disable-model-invocation: true
argument-hint: <refactor-goal | path/to/squid-refactor-spec.md | tracker-ref>
---

# Refactor — plan a no-behaviour-change structural improvement

A refactor is **not** a feature and **not** a bug, so the Product Architect's feature-grooming flow doesn't fit. This skill produces a Tasks Plan whose tasks are **commit-grain** (each one keeps `main` shippable, suite green at every commit) and whose AC are structural: imports, types, signatures, dependency direction, public surface, test coverage ("module X no longer imports module Y"). The output feeds `/squid-implement-night` directly.

You are the **planner** — you may delegate exploration but do NOT write code, do NOT execute steps. Your output is the plan file plus a hand-off message.

`$ARGUMENTS` is one of:

- A free-form refactor goal ("extract `auth.session` into its own package", "replace ad-hoc retries with `tenacity`", "rename `User.id` to `User.uid` repo-wide").
- A path to a markdown spec.
- A tracker reference.

If empty, ask the user for one.

Read `AGENTS.md` first to confirm the active **tracker mode** (`file` or `gh`) and the pipeline map this plan plugs into.

## When NOT to use

- A feature with new user-visible behaviour — use `/squid-plan` (PA grooming) instead.
- A rewrite — it's a feature whose user-visible behaviour is "the new system, but the same"; don't smuggle it in here.
- A bug fix — use `/squid-triage-issue`, then `/squid-implement-task` or `/squid-implement-night`.
- A one-file rename you can finish in five minutes — just do it; don't ceremony.

## Step 1 — Resolve and frame the refactor

Identify what to refactor from `$ARGUMENTS` (same resolution rules as `/squid-triage-issue`'s Step 1).

Capture three things explicitly — ask the user via `AskUserQuestion` if any are missing, one round of questions max:

1. **Goal** — one sentence, structural. ("Move all auth code out of `core/` and into `auth/`.")
2. **Definition of done** — concrete, testable structural invariants. ("`grep -r 'from core.auth' src/` returns nothing"; "`auth/` has no imports from `core/` except types"). At least 2.
3. **Hard constraints** — what *must not* change. ("Public API of `core.session.Session` unchanged"; "no DB schema changes"; "feature flag X stays toggleable throughout").

If the user can't answer (1)–(3), the refactor isn't ready to plan. Surface that and stop — the user does the thinking, not you.

## Step 2 — Map the blast radius

Spawn 1 Explore agent (parallel calls if scope is large enough to need 2):

```
Agent(
  subagent_type="Explore",
  prompt="""Refactor scope: {goal from Step 1}.

  Map: (1) every file that will be touched (rough count + paths); (2) every module/package that imports the affected code (call sites — file:line); (3) every test that exercises the affected code; (4) any public API surface (functions / classes / endpoints / CLI commands) that callers outside the codebase might depend on; (5) the depth of the existing test coverage on the affected modules — coarse estimate (good / thin / none).

  Be exhaustive on (1)–(3); a missed import becomes a broken commit. Report as five sections."""
)
```

When the agent returns:

- **Read the plan-critical files yourself.** Don't trust a summary on the load-bearing modules.
- **Test-coverage gate.** If coverage is `none` or `thin` on the affected modules, surface this to the user as a prerequisite task ("expand test coverage to cover the current behaviour of `core/auth/*` before refactoring") and ask: "Add this as the first task, or stop?" Do not silently plan a refactor on top of weak tests.

## Step 3 — Decompose into commit-grain tasks

Each task must satisfy three rules:

1. **Reversible alone.** Reverting just this commit leaves `main` green.
2. **Tests green at the boundary.** The full unit + integration suite passes after this task and after every prior task.
3. **One coherent intention.** "Move file X and update its imports" is one task. "Move file X, rename function Y, fix bug Z" is three.

Common refactor shapes and their canonical decomposition:

| Refactor shape | Typical task sequence |
|---|---|
| **Extract module** | (1) copy code to new location with old still in place + re-export shim; (2) move call sites in batches by package; (3) delete shim + old file. |
| **Rename across codebase** | (1) introduce new name as alias of old; (2) migrate call sites in batches; (3) deprecate old name; (4) delete old name. |
| **Library swap** | (1) introduce new lib alongside old behind an internal facade; (2) migrate call sites; (3) remove old lib. |
| **Layer cleanup** (e.g., remove cycle) | (1) introduce the seam (new module / interface); (2) move responsibilities one batch at a time; (3) enforce direction with an architectural test. |
| **Dead-code removal** | (1) delete callers; (2) delete leaves; (3) re-run unused-detector. Each in its own task only if the ordering matters; often this is one task. |
| **De-abstraction / simplification** | (1) inline the single-implementation interface / factory / wrapper at its one call site; (2) swap hand-rolled logic for the stdlib / native / framework equivalent; (3) drop the now-unused dependency. Structural AC: the abstraction (or dep) is gone, public behaviour unchanged, suite green. Feeds directly from `/squid-architecture-review` over-engineering findings. |

3–8 tasks is a healthy plan size. Fewer than 3 → it's too small for a Tasks Plan; do it as a single `/squid-implement-task` task. More than 8 → either decompose into multiple sequential refactors (file separate `/squid-refactor` plans), or you're sneaking feature work in.

## Step 4 — Write the Tasks Plan

Use this template. Frontmatter follows `squid-scaffold/specs/tracker-workflow.md`, so `/squid-implement-task` and `/squid-implement-night` accept it without re-grooming.

```markdown
# Refactor: {one-line goal}

**Type:** refactor
**Definition of done:**
- {invariant 1}
- {invariant 2}
- ...

**Hard constraints (must not change):**
- {constraint 1}
- ...

**Test-suite anchor:** `make pre-commit && make unit-tests && make integration-tests`. Every task ends with this command green.

## Tasks

### 1. {one-line task title}

**Scope:** {1–2 sentences on what this commit does and only what it does.}

**Files touched (expected):** `path/a.py`, `path/b.py`, ...

**Acceptance criteria:**
- [ ] {Structural assertion. e.g. `grep -r 'from core.auth' src/auth/ | wc -l` is 0.}
- [ ] {Behavioural invariant. e.g. Public API of `Session.login()` unchanged — verified by existing tests at `tests/auth/test_session.py`.}
- [ ] Test suite anchor green.
- [ ] No new unit tests required (this is a refactor) — but if you find a coverage gap that blocks the move, add the test before doing the move and call that out in the SWE log.

**Out of scope:**
- {explicit list — adjacent things that look related but belong to other tasks.}

### 2. ...

(Repeat for each task.)

## Rollback story

If task N goes sideways and the team needs to ship before it's resolved, revert commits {N..} only. Tasks {1..N-1} are independently shippable by construction.

## Notes for the SWE

- This is a refactor — **add no behaviour, fix no bugs**, even if you spot one. File a `/squid-triage-issue` for any bug found mid-refactor; do not let it ride along.
- If a task's AC turns out to be wrong (e.g., a hidden import the planner missed), update the plan via the orchestrator before adapting code — drift between plan and reality is the source of "refactor went off the rails" stories.
```

## Step 5 — File the plan

Where it lands depends on tracker mode (per `AGENTS.md`).

### File mode

There is no separate plan document — the Tasks Plan *is* the set of task files, same as `/squid-plan`'s output. Write one `tasks/<NNN>-<refactor-slug>-<k>.md` per task (frontmatter `status: pending`, `feature: refactor-<slug>`; allocate `NNN` per `squid-scaffold/specs/tracker-workflow.md`). Each file carries its task's Scope, Files touched, Acceptance criteria, and Out of scope from the template; fold the **hard constraints** into every task's Out of scope, and the **definition-of-done invariants** into the final task's acceptance criteria so the PA acceptance review verifies them.

### gh mode

Open one parent issue (label `refactor,plan`) with the full plan in the body, then one issue per task linked back to the parent (label `refactor,task`). Capture all numbers for the hand-off message.

## Step 6 — Hand-off

Single markdown block:

```markdown
## Refactor plan ready — {goal}

**Plan:** {tracker path or parent issue URL}
**Tasks ({N}):**
1. {NNN-slug or #N} — {title}
2. ...

**Definition of done:** {bulleted DoD from the plan}

### Recommended next step

`/squid-implement-night {plan-ref}` — the inner loop runs each task, the Tester gate enforces "tests green at every step", and the PA acceptance review verifies the structural DoD. The human still gates the merge.

If the refactor is small enough (≤ 2 tasks) and you'd rather supervise:

`/squid-implement-task {first-task-ref}` then `/squid-implement-task {next-task-ref}` — manual, one task at a time.

### Pre-flight checklist (before /squid-implement-night)

- [ ] Test-suite anchor is green on `main` *right now*. Do not start a refactor on a red base.
- [ ] No in-flight feature branches conflict with the affected files (avoidable merge churn).
- [ ] If the refactor touches the public API, the deprecation / migration story for downstream callers is captured in the plan or in an ADR (spec: `squid-scaffold/specs/adr.md`).
```
