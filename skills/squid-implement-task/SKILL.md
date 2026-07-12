---
name: squid-implement-task
description: >-
  Implement one task — or a whole list / an approved Tasks Plan — via the inner SWE↔Tester loop,
  committing each task on PASS. Use when one or more GROOMED tasks are ready to build, or the user
  says "/squid-implement-task". To plan a feature first use /squid-plan; for the full end-to-end
  pipeline use /squid-implement-night.
disable-model-invocation: false
argument-hint: <task-ref | "task description" | plan-ref | list of task-refs>
---

# Implement Task — inner SWE↔Tester loop (1 or N tasks)

Take a task (or a list of tasks / an approved Tasks Plan) and drive each one through the inner **SWE → Tester** loop, committing each task once it passes. This is the implementation core that `/squid-implement-night` runs; you can also run it standalone, on demand.

`$ARGUMENTS` is one of: a single task ref (`NNN-slug` / `#N`), a free-form task description, the feature's pending task files (`tasks/<NNN>-*.md`, `status: pending`), or several refs. If empty, ask the human what to implement.

You are the **orchestrator** — a MANAGER, not an implementer. You launch agents, enforce the Tester gate, and commit on green. You do NOT write code, run tests, or review the diff yourself.

Read `AGENTS.md` first to confirm the active **tracker mode** (`file` or `gh`) and the project's stack + test commands.

**Where this runs:** in whatever working tree it's invoked in. When `/squid-implement-night` invokes it, it runs in the feature worktree `/squid-plan` created (the orchestrator passes `Working directory: {path}` to every agent). Standalone, it runs on your current branch. **It does NOT create branches or worktrees** — that's `/squid-plan`'s job.

**Critical rules:**

- **Never rubber-stamp the Tester.** Spot-check that each AC marked PASS has real evidence (test name, file:line, command output) and that the e2e adversarial section actually attempted break paths. Re-launch with concrete feedback if not.
- **One agent per task.** Never bundle multiple tasks into one agent call.
- **The orchestrator never writes code, never reviews the diff** beyond inspection (`git diff`, `git log`).
- **Commit each task on PASS — do NOT push.** Pushing, PR creation, acceptance, and review are `/squid-review`'s job.

---

## Step 1 — Resolve the task list

Build an ordered list of tasks from `$ARGUMENTS`:

- **Tracker ref(s)** (`NNN-slug` / `#N`) → load each task's `tasks/<NNN>-<slug>.md`.
- **Approved Tasks Plan** → the feature's `tasks/<NNN>-*.md` files with `status: pending`, in `NNN` order (gh mode: the feature's open issues).
- **Free-form description** → a single ephemeral task; don't create a task file unless the human asks.
- **Empty** → ask the human what to implement.

Surface the resolved task list back in one short block before starting.

---

## Step 2 — Per task, in order: SWE → Tester → commit

For each task in the list, run the loop:

### 2a. SWE implements

```
Agent(
  subagent_type="squid:software-engineer",
  prompt="""Implement task {ID}. Read AGENTS.md first. Follow your role definition.
  {Working directory: {path}  — include this line only when orchestrated by /squid-implement-night.}
  Stay on the current branch — do NOT create a per-task branch (no `feat/{ID}-…`). Each task is one commit on this shared feature branch.
  In file mode, set this task's `tasks/<NNN>-<slug>.md` frontmatter `status: in-progress` before you start.
  Write code AND tests. Run the project's format-fix + lint-fix + pre-commit + unit-tests until clean.
  DO NOT commit yet — the Tester goes first. Append a SWE log entry (or include it in your final message for ephemeral tasks)."""
)
```

### 2b. Tester verifies

```
Agent(
  subagent_type="squid:tester",
  prompt="""QA task {ID}. Read AGENTS.md first. Follow your role definition — your headline duty is the e2e adversarial pass.
  {Working directory: {path}.}
  SWE summary: {hand-off message}.
  Run pre-commit + unit-tests + integration-tests, then the e2e adversarial pass (happy path + 2–3 realistic break paths).
  Verify every acceptance criterion with evidence. Append a Tester log entry. Verdict: PASS or FAIL."""
)
```

### 2c. Handle the verdict — `Fails?`

Spot-check the report before accepting it.

- **FAIL** (or a rubber-stamped PASS) → relay concrete feedback to the SWE and re-run 2b on the same task:
  ```
  Agent(
    subagent_type="squid:software-engineer",
    prompt="QA failed on task {ID}. {Working directory: {path}.} Concrete feedback: {failed ACs + break-path failures + fixes}. Apply the fixes, re-run the local QA loop, append a log entry. DO NOT commit."
  )
  ```
- **PASS (verified)** → go to 2d.

**Retry cap — Tester FAIL max 5 per task.** On the 5th FAIL without a PASS: mark the task blocked, surface `USER ACTION REQUIRED` with the failing AC + last Tester report, and STOP — do not continue to later tasks (the foundation is broken). The counter resets when the task changes.

### 2d. Commit the task (on PASS only)

```
Agent(
  subagent_type="squid:software-engineer",
  prompt="""Tester PASSED task {ID}. {Working directory: {path}.} Commit JUST this task per your role definition —
  use the commit-message generator (`/caveman-commit` if the caveman plugin is installed, else the `commit-commands` plugin), specific files only (never `git add -A`). Conventional Commits subject
  (`feat:` / `fix:` / `refactor:` / …). Message ends with `Closes #N` (gh mode) or `Closes-task: NNN-slug` (file mode).
  DO NOT push."""
)
```

In file mode, the SWE also sets the task's frontmatter `status: done` and `git mv`s the file from `tasks/` into `tasks/done/` as part of that commit.

### 2e. `Finished tasks?`

- **More tasks remain** → next task (back to 2a). The Tester FAIL counter resets.
- **All tasks done** → STOP. Output: code + tests, one commit per task on the current branch.

---

## Output

Code + tests, **committed per task** (no push). Report a short summary: tasks done, the commit subject + ref for each, and any task that hit the retry cap. When invoked by `/squid-implement-night`, hand this summary back so it can proceed to `/squid-review`.

---

## Notes

- **Autonomous, not supervised.** This commits each task itself after the Tester passes — it does not stop for a human to commit. The human gates live in `/squid-plan` (plan approval) and at the end of `/squid-implement-night` (merge).
- **No push, no PR, no acceptance here.** `/squid-review` pushes, creates/updates the PR, and runs PA acceptance + PR-Reviewer. `/squid-review-ci` watches CI. Keep this skill to implement → verify → commit.
- **Rollup / fix tasks** handed in by `/squid-review` (or by a human) are just more tasks — feed them in and the same loop applies.
