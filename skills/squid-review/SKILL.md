---
name: squid-review
description: >-
  Push the committed feature branch, create or update its PR, then run Product Architect
  acceptance and PR-Reviewer on it. Output: a clean PR with no blockers, or ONE rollup task.
  Trigger after a feature's tasks are implemented and committed.
argument-hint: <feature-title | plan-ref>
---

# Review — push, PA acceptance, PR review

Take the committed feature branch and turn it into a clean, pushed feature PR — or a rollup task describing what to fix. Both gates run on the **pushed PR**, sequentially: Product Architect (PA) acceptance first, then PR-Reviewer.

You are the **orchestrator** — a MANAGER. You push, launch the review agents, enforce the gates, and route failures back as rollup tasks. You do NOT review the diff, write code, or merge.

Read `AGENTS.md` first (tracker mode). Retry caps are below; the Severity Rule lives in the PR-Reviewer's role definition.

**Input:** a feature branch whose tasks are implemented and committed (the worktree when orchestrated by `/squid-implement-night`; the current branch when run standalone).
**Output:** a pushed feature PR with **NO blockers** (Nits appended to the PR description), OR **ONE rollup task**.

**Critical rules:**

- **Never rubber-stamp** an ACCEPT or NO BLOCKERS — spot-check the evidence; re-launch with feedback if it's thin.
- **One rollup task per failed gate**, never one ticket per issue.

---

## Step 1 — Push + create/update the PR

```
Agent(
  subagent_type="squid:software-engineer",
  prompt="""Push feature {title} and open/update its PR per your Push / open PR section. {Working directory: {path}.}
  The PR description summarizes the feature and lists each task by ID. Hand back the PR number."""
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
  Walk the feature from the user's perspective against the Tasks Plan's acceptance criteria. Verdict: ACCEPT or REJECT. On REJECT, write ONE rollup task capturing ALL product issues."""
)
```

- **ACCEPT (verified)** → Step 3.
- **REJECT** → the PA filed ONE rollup task. **Return it** (see Output).
- **Cap: PA REJECT max 3 per feature.** On the 4th would-be REJECT, stop and surface `USER ACTION REQUIRED`.

---

## Step 3 — PR-Reviewer (Any Blockers?)

```
Agent(
  subagent_type="squid:pr-reviewer",
  prompt="""Review PR #{N} (branch feat/{slug}). Read AGENTS.md first. Follow your role definition.
  {Working directory: {path}.}
  Walk every review dimension, including the Simplicity / anti-over-engineering pass. Produce ONE rollup task if there are Blockers; else report NO BLOCKERS and append the Nits to the PR description."""
)
```

- **NO BLOCKERS** → done. Nits are already on the PR description. Output: the clean pushed PR (#{N}).
- **Blockers** → the PR-Reviewer filed ONE rollup task (Blockers + Nits). **Return it** (see Output).
- **Cap: PR-Reviewer max 3 per feature.** On the 4th would-be Blockers verdict, stop and surface `USER ACTION REQUIRED`.

---

## Output

- **Pass** → "Feature PR #{N} clean (no blockers)." Hand to `/squid-review-ci` (or the human) for CI validation.
- **Fail** → ONE rollup task. The caller (`/squid-implement-night`) routes it back through `/squid-implement-task`, then re-invokes `/squid-review`.
