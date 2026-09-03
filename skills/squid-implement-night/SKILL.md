---
name: squid-implement-night
description: >-
  Run the full agent-team pipeline end-to-end for one feature whose Tasks Plan is already approved
  by /squid-plan, handing the human a validated, ready-to-squash-merge PR. Trigger after
  /squid-plan.
argument-hint: <plan-ref | feature-slug>
---

# Implement Night — end-to-end feature pipeline (thin orchestrator)

Build an **already-approved** feature plan all the way to a validated, ready-to-merge PR. This skill is a thin orchestrator: the real work lives in the sub-skills it invokes — `/squid-implement-task`, `/squid-review`, `/squid-review-ci` — plus the agents those skills launch.

`$ARGUMENTS` is the approved Tasks Plan reference (path or feature slug) produced by `/squid-plan`. If empty, ask the human which plan to build (and remind them to run `/squid-plan` first if none exists).

You are the **orchestrator** — a MANAGER. You sequence the sub-skills, route rollback tasks, and enforce the gates. You do NOT write code, review the diff, or run tests yourself.

Read `AGENTS.md` first (tracker mode, the pipeline map, and the cross-cutting rules). Retry caps live in each sub-skill.

**Input:** an approved Tasks Plan + the feature branch/worktree `/squid-plan` created.
**Output:** a CI-validated feature PR, ready for the human to squash-merge.

**The pipeline blocks on the human only at the very end** (squash-merge). (Plan approval already happened in `/squid-plan`.) Everything between is automated; failures route back into `/squid-implement-task` as rollup tasks rather than stopping the pipeline. **Caps stop the pipeline:** Tester FAIL 5/task, PA REJECT 3, PR-Reviewer 3, On-Call 5 — when a cap fires, surface `USER ACTION REQUIRED` and stop.

**Critical rules:**

- **Never rubber-stamp a sub-skill's result.** When `/squid-review` reports "no blockers" or `/squid-review-ci` reports "green", confirm the evidence is real before advancing.
- **By name, never by path.** Invoke `/squid-implement-task`, `/squid-review`, `/squid-review-ci` by their skill names so it works when installed as a plugin.

---

## Step 0 — Locate the branch worktree + tasks

`/squid-plan` created the feature branch `feat/{slug}` — either in a dedicated worktree at `../{repo}-{slug}` or in the current working tree — and wrote the feature's task files (`tasks/<NNN>-*.md`, `status: pending`) on it. Find where that branch is checked out:

```bash
git worktree list          # find the working tree whose branch is feat/{slug}
```

Confirm that working tree exists and contains pending task files (`tasks/<NNN>-*.md` with `status: pending`); `WORKTREE_PATH` is its path (the dedicated worktree, or the repo root if the branch lives in the current tree). If there's no matching branch or no pending tasks, stop and tell the human to run `/squid-plan` first. Pass `Working directory: {WORKTREE_PATH}` to every sub-skill / agent so all work happens there.

---

## Step 1 — Build the whole plan

Invoke `/squid-implement-task` **once with the feature's pending tasks**. It loops over every task — SWE → Tester → commit on PASS → next. (Do NOT loop here yourself; the per-task iteration lives inside `/squid-implement-task`.)

```
invoke /squid-implement-task with: the feature's pending tasks (tasks/<NNN>-*.md, status: pending), Working directory: {WORKTREE_PATH}
```

---

## Step 2 — Review (loop until clean)

```
invoke /squid-review with: feature {title}, Working directory: {WORKTREE_PATH}
```

`/squid-review` pushes, creates/updates the PR, and runs PA acceptance then PR-Reviewer.

- **Returns "clean" (no blockers)** → proceed to Step 3.
- **Returns a rollup task** (PA REJECT or PR-Reviewer Blockers) → invoke `/squid-implement-task` on that one rollup task (it builds + commits the fix), then **re-invoke `/squid-review`**. Repeat.

---

## Step 3 — Review CI

```
invoke /squid-review-ci with: PR #{N}, Working directory: {WORKTREE_PATH}
```

`/squid-review-ci` watches CI and drives it green (On-Call diagnoses → SWE fixes → re-check).

- **CI green** → the PR is validated and ready to merge. Proceed to the tail.

---

## Tail — hand-off

The validated PR is ready. The orchestrator does NOT squash — per-task commits stay on the branch; the human uses GitHub's "Squash and merge".

Report the final summary:

```markdown
## /squid-implement-night complete — {Feature title}

**PR:** {URL} (validated; ready to squash-merge)
**Branch:** feat/{slug} ({N} per-task commits)
**Worktree:** {WORKTREE_PATH}

**Tasks delivered ({N}):** {table — Tester / PA accept / PR-Reviewer / CI}
**Rollup tasks ({M}):** {list, or "none"}

Next: review the PR, then GitHub's **Squash and merge**. Remove the worktree with `git worktree remove {WORKTREE_PATH}` after merge.
```

`/squid-implement-night` ends here.

---

## Notes on shape

- `/squid-review-ci` handles its own CI fixes internally and does not re-enter `/squid-review`.
- **Don't add mid-pipeline gates.**
