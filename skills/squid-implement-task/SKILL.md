---
name: squid-implement-task
description: >-
  Implement one task — or a whole list / an approved Tasks Plan — via the inner SWE↔Tester loop,
  committing each task on PASS. Use when one or more GROOMED tasks are ready to build. To plan a
  feature first use /squid-plan; for the full end-to-end pipeline use /squid-implement-night.
argument-hint: <task-ref | "task description" | plan-ref | list of task-refs>
---

# Implement Task — inner SWE↔Tester loop (1 or N tasks)

Take a task (or a list of tasks / an approved Tasks Plan) and drive each one through the inner **SWE → Tester** loop, committing each task once it passes. Runs in whatever working tree it's invoked in — the feature worktree when `/squid-implement-night` invokes it (pass `Working directory: {path}` to every agent), your current branch when standalone. No worktrees are created here (that's `/squid-plan`'s job) and no human gates run here (those live in `/squid-plan` and at the end of `/squid-implement-night`).

`$ARGUMENTS` is one of: a single task ref (`NNN-slug` / `#N`), a free-form task description, the feature's pending task files (`tasks/<NNN>-*.md`, `status: pending`), or several refs. If empty, ask the human what to implement.

You are the **orchestrator** — a MANAGER, not an implementer. You launch agents, enforce the Tester gate, and commit on green. You do NOT write code, run tests, or review the diff yourself beyond inspection (`git diff`, `git log`).

Read `AGENTS.md` first to confirm the active **tracker mode** (`file` or `gh`) and the project's stack + test commands.

**Critical rules:**

- **Never rubber-stamp the Tester.** Spot-check that each AC marked PASS has real evidence (test name, file:line, command output) and that the e2e adversarial section actually attempted break paths. Re-launch with concrete feedback if not.
- **One agent per task.** Never bundle multiple tasks into one agent call.
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
  Stay on the current feature branch — do NOT create a per-task branch (no `feat/{ID}-…`); if you are on `main`, create ONE `feat/{slug}` branch first per your Branch section. Each task is one commit on that shared feature branch.
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
  Verify every acceptance criterion with evidence. Append a Tester log entry. Verdict: PASS or FAIL."""
)
```

### 2c. Handle the verdict — `Fails?`

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
  prompt="""Tester PASSED task {ID}. {Working directory: {path}.} Commit JUST this task per your Commit section
  (generator, specific files, task reference, file-mode `status: done` + `git mv` to tasks/done/). DO NOT push."""
)
```

### 2e. `Finished tasks?`

- **More tasks remain** → next task (back to 2a).
- **All tasks done** → STOP; see Output.

---

## Output

Code + tests, **committed per task** (no push). Report a short summary: tasks done, the commit subject + ref for each, and any task that hit the retry cap. When invoked by `/squid-implement-night`, hand this summary back so it can proceed to `/squid-review`.

---

## Notes

- **Rollup / fix tasks** handed in by `/squid-review` (or by a human) are just more tasks — feed them in and the same loop applies.
