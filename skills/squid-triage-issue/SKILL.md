---
name: squid-triage-issue
description: >-
  Bug intake — localise the suspected code, capture a deterministic reproducer, and emit a groomed
  bug task with a regression-test acceptance criterion, ready for /squid-implement-task or the
  full pipeline.
disable-model-invocation: true
argument-hint: <bug-description | path/to/report.md | #issue-or-NNN-slug>
---

# Triage — turn a bug report into a groomed, fixable task

`/squid-implement-task` and `/squid-implement-night` both assume the spec is already shaped right. Bug reports rarely are: they read "X is broken" and need a reproducer, expected-vs-actual, code localisation, and a regression-test acceptance criterion before SWE / Tester can do anything useful with them. This skill produces that groomed bug task, then hands off.

You are the **triage orchestrator** — you may delegate exploration to sub-agents (Explore, general-purpose), but you do NOT write production code, do NOT write the regression test, and do NOT start the fix. Your output is the spec.

`$ARGUMENTS` is one of:

- A free-form bug description (paste-in customer report, stack trace, "X is broken when Y").
- A path to a markdown report (`docs/bugs/foo.md`).
- A tracker reference (`NNN-slug` in file mode, `#N` in gh mode).

If empty, ask the user for one before proceeding.

Read `AGENTS.md` first to confirm the active **tracker mode** (`file` or `gh`).

## When to use

- A bug needs to land in the team's pipeline but the description isn't yet groomed (no reproducer, no expected/actual, no AC).
- A flaky test surfaces and you need to capture it as a fixable task before it gets ignored.
- A customer report or postmortem item needs to become a task.

## When NOT to use

- A feature request — use `/squid-plan` (PA grooming) directly.
- A refactor with no observable user impact — use `/squid-refactor`.
- A trivial typo or one-line bug you can fix right now in chat — just fix it.
- An incident still in progress — stabilise first, triage after.

## Step 1 — Resolve the report

Identify what to triage from `$ARGUMENTS`:

1. **File path** → `cat` the report.
2. **Tracker reference** (`NNN-slug` file mode, `#N` gh mode) → load the existing record (`tasks/NNN-*.md` or `gh issue view N --json number,title,body,labels`).
3. **Free-form text** → use as-is.
4. **Empty** → ask: "What bug should I triage? (Paste the report, give me a path, or a tracker reference.)"

Echo the resolved report back to the user in one paragraph as confirmation. Don't block — proceed.

## Step 2 — Localise

Spawn ONE Explore agent (or general-purpose if the report is vague enough that exploration needs interview-style breadth) to:

- Identify the modules/files most likely involved, ranked by confidence.
- Find existing tests that exercise the affected behaviour.
- Note nearby code that has changed recently (`git log --since='4 weeks ago' -- <file>`) — recent changes are correlated with regressions.
- Surface any related closed issues / PRs (`gh search issues "<keyword>" --state closed`).

Prompt sketch (adapt as needed):

```
Agent(
  subagent_type="Explore",
  prompt="""Bug report: {one-paragraph summary}.

  Find: (1) the module(s) most likely responsible — rank top-3 with file:line and a one-sentence reason; (2) existing tests covering this behaviour, by file:line; (3) recent commits (last 4 weeks) touching the implicated files; (4) related closed PRs / issues.

  Be specific. Report back as four bulleted lists. Do NOT propose fixes."""
)
```

Read the top-3 candidate file(s) yourself (cheap) before moving on — you want firsthand familiarity, not just the agent's summary.

## Step 3 — Build the reproducer

A reproducer is the load-bearing artefact. Without one, the Tester can't verify a fix and the SWE is guessing.

Try, in this order:

1. **Re-derive from the report** — if the user already pasted exact steps, formalise them as a numbered list with concrete inputs.
2. **Ask the user** — if the report is vague ("the page is slow sometimes"), use `AskUserQuestion`. Two questions max:
   - What exact input / state triggers it?
   - What's the smallest path to observing it (URL, command, test invocation)?
3. **Synthesise from code** — if the user can't repro and the code makes the failure mode obvious, draft the reproducer as a failing test case (described in prose; you don't write it).

The reproducer must be **deterministic**. If it's only intermittent, mark it explicitly as `flaky-repro` and capture the conditions correlating with reproduction (load, state, time-of-day) — flakies need a different fix posture.

## Step 4 — Write the groomed bug task

Use this exact template. It mirrors the PA's groom output so `/squid-implement-task` and `/squid-implement-night` accept it without re-grooming.

```markdown
# Bug: {one-line title — observable user-visible symptom}

**Severity:** {S1 outage / S2 broken feature / S3 degraded / S4 cosmetic}
**Affected component(s):** {file paths or module names}
**First observed:** {date or commit ref, if knowable}

## Summary

One paragraph. What the user sees. Don't speculate on the cause here.

## Reproducer (deterministic)

1. {exact command / URL / inputs}
2. {next step}
3. ...

Expected: {what should happen}
Actual: {what does happen — include exact error message, status code, or output}

> If the bug is non-deterministic, replace this section with a `Flaky-repro` block listing the correlating conditions.

## Suspected localisation

- `path/to/file.py:42` — {one-sentence reason}
- `path/to/other.py:117` — {one-sentence reason}

> Hypotheses, not conclusions. The SWE will confirm or refute during fix.

## Out of scope

- {Things that look related but aren't part of this bug — explicit so the SWE doesn't expand scope.}

## Acceptance criteria

- [ ] **Regression test** added at `tests/.../test_<slug>.py` that fails on `main` and passes on the fix branch. Test name describes the symptom, not the implementation.
- [ ] Reproducer steps from above produce the expected behaviour after the fix.
- [ ] No unrelated behaviour changes (full unit + integration suite green).
- [ ] If `Severity ≤ S2`, a one-line note added to the project changelog / release notes.

## Notes for the SWE

- {Optional: hints from your localisation — e.g. "the bug appears only when feature flag X is on; check the branching in module Y".}
- {Optional: explicitly forbidden fix shapes — e.g. "do not add a try/except that swallows the underlying exception; surface it properly".}
```

**Severity heuristic** (don't over-think — the user can correct):

- **S1** — production outage / data loss / security exposure.
- **S2** — a documented feature is broken; users hit it on the golden path.
- **S3** — a documented feature is degraded; workarounds exist.
- **S4** — cosmetic / docs / typo.

## Step 5 — File the task

Where it lands depends on tracker mode (read from `AGENTS.md`).

### File mode

Pick the next sequential ID (`ls tasks/ tasks/done/ 2>/dev/null | grep -oE '^[0-9]+' | sort -n | tail -1`, +1, zero-padded to the project's existing width — scanning `tasks/done/` too so a completed task's number isn't reused). Write to:

```
tasks/NNN-bug-<slug>.md
```

Open the file with YAML frontmatter (`status: pending`, `feature: bug-<slug>`), then the groomed body from Step 4. `status: pending` signals "groomed, can enter the inner loop" — both `/squid-implement-task` and `/squid-implement-night` accept it directly.

### gh mode

```
gh issue create \
  --title "Bug: {one-line title}" \
  --label "bug,triaged" \
  --body "$(cat <<'EOF'
{the entire groomed-bug body, minus the # H1}
EOF
)"
```

Capture the issue number for Step 6.

## Step 6 — Hand-off recommendation

Surface a single decision block to the user:

```markdown
## Triage complete — {bug title}

**Filed:** {tracker path or issue URL}
**Severity:** {S1–S4}
**Suspected files:** {top 1–3}

### Recommended next step

{Pick ONE based on severity + scope:}

- **Severity S1 / S2, narrow scope (≤2 files), reproducer is deterministic** → `/squid-implement-task {ref}` — supervise the fix in real time. Fastest path; you watch the diff.
- **Severity S3 / S4, OR scope spans multiple files / tasks, OR a regression test will need its own design conversation** → `/squid-plan {ref}` then `/squid-implement-night` — full pipeline. The PA decomposes into tasks; you only gate the plan and the merge.
- **Severity S1 production-down** → fix live yourself; this groomed task becomes the postmortem record, not the entry point.

### Open questions for the human

- {if any — list them. Otherwise omit this section.}
```

Hand control back. Do NOT auto-invoke `/squid-implement-task` or `/squid-implement-night` — the user picks.

## Notes on shape

- **Hypotheses, not fixes.** Triage names suspects; the SWE confirms. Skipping ahead to "the fix is X" pre-commits the team to one branch of the search tree before the test suite has had a chance to argue.
- **Regression test is non-negotiable.** Every triaged bug ships with a test that didn't exist before. This is the single highest-ROI invariant in the whole pipeline — it's why bugs don't return.
- **Don't expand scope.** If you find three other related issues during localisation, file them as separate triage tasks (one bug per task). The "Out of scope" section in the groomed file exists to keep the SWE honest about this too.
- **Flaky-repro tasks need a posture, not a fix.** When you can't reproduce, the task changes shape — the AC becomes "instrument so we can capture it next time," not "fix the bug." Be explicit about the difference.
- **Triage is a research output, not a code output.** The user must approve the groomed task before any agent touches code. This skill stops at filing.
