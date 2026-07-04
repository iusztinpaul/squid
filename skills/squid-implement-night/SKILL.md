---
name: squid-implement-night
description: Run the full agent-team pipeline end-to-end for one feature whose Tasks Plan is already approved (by /squid-plan). A thin orchestrator — runs INSIDE the feature worktree and invokes /squid-implement-task (build + commit every task), then /squid-review (push + PA acceptance + PR-Reviewer), then /squid-review-ci (CI), then a human-gated squid-self-improve, and hands the validated PR to the human to squash-merge. Trigger after /squid-plan, or say "/squid-implement-night".
disable-model-invocation: false
argument-hint: <plan-ref | feature-slug>
---

# Implement Night — end-to-end feature pipeline (thin orchestrator)

Build an **already-approved** feature plan all the way to a validated, ready-to-merge PR. This skill is a thin orchestrator: the real work lives in the sub-skills it invokes **by name** — `/squid-implement-task`, `/squid-review`, `/squid-review-ci` — plus the agents those skills launch.

`$ARGUMENTS` is the approved Tasks Plan reference (path or feature slug) produced by `/squid-plan`. If empty, ask the human which plan to build (and remind them to run `/squid-plan` first if none exists).

You are the **orchestrator** — a MANAGER. You sequence the sub-skills, route rollback tasks, and enforce the gates. You do NOT write code, review the diff, or run tests yourself.

Read `AGENTS.md` first (tracker mode, retry caps, the pipeline map, and the cross-cutting rules).

**Input:** an approved Tasks Plan + the feature branch/worktree `/squid-plan` created.
**Output:** a CI-validated feature PR, ready for the human to squash-merge.

**The pipeline blocks on the human only at the very end** (squash-merge), plus the one optional squid-self-improve prompt. (Plan approval already happened in `/squid-plan`.) Everything between is automated; failures route back into `/squid-implement-task` as rollup tasks rather than stopping the pipeline. **Caps stop the pipeline:** Tester FAIL 5/task, PA REJECT 3, PR-Reviewer 3, On-Call 5 — when a cap fires, surface `USER ACTION REQUIRED` and stop.

**Critical rules:**

- **Never rubber-stamp a sub-skill's result.** When `/squid-review` reports "no blockers" or `/squid-review-ci` reports "green", confirm the evidence is real before advancing.
- **By name, never by path.** Invoke `/squid-implement-task`, `/squid-review`, `/squid-review-ci` by their skill names so it works when installed as a plugin.
- **The orchestrator never writes code, never merges, never squashes.**

---

## Step 0 — Locate the branch worktree + tasks

`/squid-plan` created the feature branch `feat/{slug}` — either in a dedicated worktree at `../{repo}-{slug}` or in the current working tree — and wrote the feature's task files (`tasks/<NNN>-*.md`, `status: pending`) on it. Find where that branch is checked out:

```bash
git worktree list          # find the working tree whose branch is feat/{slug}
```

Confirm that working tree exists and contains pending task files (`tasks/<NNN>-*.md` with `status: pending`); `WORKTREE_PATH` is its path (the dedicated worktree, or the repo root if the branch lives in the current tree). If there's no matching branch or no pending tasks, stop and tell the human to run `/squid-plan` first. Pass `Working directory: {WORKTREE_PATH}` to every sub-skill / agent so all work happens there.

---

## Step 1 — Build the whole plan

Invoke `/squid-implement-task` **once with the feature's pending tasks**. It loops over every task — SWE → Tester (FAIL max 5/task) → commit on PASS (flipping each task's `status` pending → in-progress → done) → next. (Do NOT loop here yourself; the per-task iteration lives inside `/squid-implement-task`.)

```
invoke /squid-implement-task with: the feature's pending tasks (tasks/<NNN>-*.md, status: pending), Working directory: {WORKTREE_PATH}
```

If `/squid-implement-task` hits its Tester FAIL cap on a task, it stops with `USER ACTION REQUIRED` — propagate that and stop.

---

## Step 2 — Review (loop until clean)

```
invoke /squid-review with: feature {title}, Working directory: {WORKTREE_PATH}
```

`/squid-review` pushes, creates/updates the PR, and runs PA acceptance then PR-Reviewer.

- **Returns "clean" (no blockers)** → proceed to Step 3.
- **Returns a rollup task** (PA REJECT or PR-Reviewer Blockers) → invoke `/squid-implement-task` on that one rollup task (it builds + commits the fix), then **re-invoke `/squid-review`**. Repeat.
- The PA REJECT (3) and PR-Reviewer (3) caps live inside `/squid-review`; if it surfaces `USER ACTION REQUIRED`, stop.

---

## Step 3 — Review CI

```
invoke /squid-review-ci with: PR #{N}, Working directory: {WORKTREE_PATH}
```

`/squid-review-ci` watches CI and drives it green (On-Call diagnoses → SWE fixes → re-check, max 5, self-contained).

- **CI green** → the PR is validated and ready to merge. Proceed to the tail.
- **`USER ACTION REQUIRED`** (cap hit) → stop.

---

## Tail — squid-self-improve (human-gated) + hand-off

The validated PR is ready. The orchestrator does NOT squash — per-task commits stay on the branch; the human uses GitHub's "Squash and merge".

Prompt the human:

```
Feature {title} is validated and ready to squash-merge: {PR URL}
Optional: run squid-self-improve to capture corrections from this run into AGENTS.md? (y/N)
```

- **N (default)** → skip to the final summary.
- **y** → **invoke the `squid-self-improve` skill** on this run; it proposes AGENTS.md updates the human reviews/accepts. When it returns, continue.

Then report the final summary:

```markdown
## /squid-implement-night complete — {Feature title}

**PR:** {URL} (validated; ready to squash-merge)
**Branch:** feat/{slug} ({N} per-task commits — GitHub squashes on merge)
**Worktree:** {WORKTREE_PATH}

**Tasks delivered ({N}):** {table — Tester / PA accept / PR-Reviewer / CI}
**Rollup tasks ({M}):** {list, or "none"}
**Self-Improve:** {ran / skipped}

Next: review the PR, then GitHub's **Squash and merge**. Remove the worktree with `git worktree remove {WORKTREE_PATH}` after merge.
```

The human squash-merges via GitHub. `/squid-implement-night` ends here.

---

## Notes on shape

- **Thin by design.** This file owns only the outer sequence + rollback routing. The SWE↔Tester loop, push/PR/acceptance/squid-review, and CI handling all live in the sub-skills and the agent contracts — edit those, not this.
- **Rollups re-enter through `/squid-implement-task`.** A `/squid-review` rollup is built and committed like any other task, then `/squid-review` re-runs. `/squid-review-ci` handles its own CI fixes internally and does not re-enter `/squid-review`.
- **One human gate (merge) + one optional prompt (squid-self-improve).** Plan approval already happened in `/squid-plan`. Don't add mid-pipeline gates.
