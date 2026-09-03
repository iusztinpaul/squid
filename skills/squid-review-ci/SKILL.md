---
name: squid-review-ci
description: >-
  Drive CI green on a pushed, review-clean feature PR — On-Call diagnoses failures and hands fix
  tasks to the SWE. Output: a CI-validated feature PR. Trigger after /squid-review passes.
argument-hint: <PR-number | branch>
---

# Review CI — validate the pushed PR's pipeline

Watch CI for the pushed feature PR and drive it to green. On failure, the On-Call engineer **diagnoses and hands a fix task to the SWE** (it does not fix the code itself); once CI is green, the PR is ready to merge.

You are the **orchestrator** — a MANAGER. You launch On-Call and the SWE, enforce the cap, and confirm green. You do NOT read the diff for review (that was `/squid-review`).

Read `AGENTS.md` first.

**Input:** a pushed, review-clean feature PR.
**Output:** a CI-validated "ready to merge" PR (or `USER ACTION REQUIRED` if CI can't be made green within the cap).

---

## The On-Call → SWE → re-check loop

### Watch CI (On-Call)

```
Agent(
  subagent_type="squid:oncall-engineer",
  prompt="""Watch CI for the latest push on feat/{slug} (PR #{N}). {Working directory: {path}.} Read AGENTS.md first. Follow your role definition. CI/CD only — do not review the diff. Report green, or hand back a concrete FIX TASK (root cause + the exact failing command + affected files)."""
)
```

- **Green** → done. The PR is validated and ready to merge.
- **Red (infra / flake)** → On-Call files a NEW infra task and reports it; surface to the human — it does not count against the cap.
- **Red (real failure)** → On-Call hands back a fix task → go to "SWE fixes".

### SWE fixes

```
Agent(
  subagent_type="squid:software-engineer",
  prompt="""CI failed on PR #{N}. {Working directory: {path}.} Fix task from On-Call: {root cause + failing command + files}. Reproduce locally with the same command CI ran, fix the root cause (not the symptom; fix the bug, not the test), re-run the local suite, commit per your Commit section (`Refs #N` — the original task is already closed), and push."""
)
```

Then re-run **Watch CI (On-Call)** to confirm the new run goes green.

### Cap: 5 fix cycles per PR

If CI is still red after 5 On-Call→SWE→re-check cycles, stop, surface `USER ACTION REQUIRED` with the last failing log, and end.

---

## Output

A CI-validated, ready-to-merge feature PR. Hand back to `/squid-implement-night`, or — if run standalone — report that CI is green and the PR is ready.
