---
name: squid-review
description: Push the committed feature branch, create or update its PR, then run Product Architect acceptance and PR-Reviewer on the pushed PR (sequentially). Each gate retries up to 3×; on failure each writes ONE rollup task to route back to /squid-implement-task. Output: a clean feature PR with no blockers, or a rollup task. Trigger after a feature's tasks are implemented and committed, or say "/squid-review".
disable-model-invocation: false
argument-hint: <feature-title | plan-ref>
---

# Review — push, PA acceptance, PR review

Take the committed feature branch and turn it into a clean, pushed feature PR — or a rollup task describing what to fix. Both gates run on the **pushed PR**, sequentially: Product Architect (PA) acceptance first, then PR-Reviewer.

You are the **orchestrator** — a MANAGER. You push, launch the review agents, enforce the gates, and route failures back as rollup tasks. You do NOT review the diff or write code yourself.

Read `AGENTS.md` first (tracker mode, retry caps; the Severity Rule lives in the PR-Reviewer's role definition).

**Input:** a feature branch whose tasks are implemented and committed (the worktree when orchestrated by `/squid-implement-night`; the current branch when run standalone).
**Output:** a pushed feature PR with **NO blockers** (Nits appended to the PR description), OR **ONE rollup task** routed back to `/squid-implement-task`.

**Critical rules:**

- **Never rubber-stamp** an ACCEPT or NO BLOCKERS — spot-check the evidence; re-launch with feedback if it's thin.
- **One rollup task per failed gate**, never one ticket per issue.
- The orchestrator never writes code, never merges.

---

## Step 1 — Push + create/update the PR

```
Agent(
  subagent_type="squid:software-engineer",
  prompt="""Push feature {title} and open/update its PR. {Working directory: {path}.}
  Push the branch (`git push -u origin feat/{slug}` the first time, else `git push`). Then create the PR if none exists on this branch (`gh pr create`), or update it and its description (`gh pr edit`). The description summarizes the feature and lists each task by ID. Hand back the PR number."""
)
```

Capture the PR number for the gates below.

---

## Step 2 — PA acceptance (Any product issues?)

```
Agent(
  subagent_type="squid:product-architect",
  prompt="""Acceptance review for feature {title} on PR #{N}. Read AGENTS.md first. Follow your acceptance-review role.
  {Working directory: {path}.}
  Walk the feature from the user's perspective against the Tasks Plan's acceptance criteria. Verdict: ACCEPT or REJECT. On REJECT, write ONE rollup task capturing ALL product issues — never one ticket per issue."""
)
```

Spot-check: an ACCEPT must cite concrete evidence matching the ACs, not just "ACCEPTED".

- **ACCEPT (verified)** → Step 3.
- **REJECT** → the PA filed ONE rollup task. **Return it** — the caller routes it back through `/squid-implement-task`, then re-runs `/squid-review`.
- **Cap: PA REJECT max 3 per feature.** On the 4th would-be REJECT, stop and surface `USER ACTION REQUIRED`.

---

## Step 3 — PR-Reviewer (Any Blockers?)

```
Agent(
  subagent_type="squid:pr-reviewer",
  prompt="""Review PR #{N} (branch feat/{slug}). Read AGENTS.md first. Follow your role definition.
  {Working directory: {path}.}
  Read the entire diff (`git diff $(git merge-base HEAD origin/main)...HEAD`). Walk every review dimension, including the Simplicity / anti-over-engineering pass. Tag each finding Blocker or Nit per the Severity Rule in your role definition. Produce ONE rollup task if there are Blockers; else report NO BLOCKERS and append the Nits to the PR description.
  Do NOT read CI status (that's /squid-review-ci). When the caveman plugin is installed, also post one-line caveman-review comments on the PR (see your role definition, Step 3b); otherwise do NOT comment on the PR. Do NOT merge."""
)
```

- **NO BLOCKERS** → done. Nits are already on the PR description. Output: the clean pushed PR (#{N}).
- **Blockers** → the PR-Reviewer filed ONE rollup task (Blockers + Nits). **Return it** — routes back through `/squid-implement-task`, then re-run `/squid-review`.
- **Cap: PR-Reviewer max 3 per feature.** On the 4th would-be Blockers verdict, stop and surface `USER ACTION REQUIRED`.

---

## Output

- **Pass** → "Feature PR #{N} clean (no blockers)." Hand to `/squid-review-ci` (or the human) for CI validation.
- **Fail** → ONE rollup task. The caller (`/squid-implement-night`) routes it back through `/squid-implement-task`, then re-invokes `/squid-review`.

---

## Notes

- **Post-push, sequential.** Both gates review the *pushed PR*; PA goes first (is it the right product?), then PR-Reviewer (is the code clean, correct, and simple?). CI is the *next* skill (`/squid-review-ci`), not run in parallel here.
- **Rollups go back to implementation, not patched inline.** A rejected gate produces one coordinated "fix everything we flagged" task.
