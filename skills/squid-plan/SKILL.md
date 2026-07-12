---
name: squid-plan
description: >-
  Turn a raw feature spec into an approved Tasks Plan — grill the spec, have the Product Architect
  groom draft tasks (+ optional ADR and glossary additions), then run ONE human gate that decides
  everything touching the repo: tasks + storage, ADR, glossary, worktree, and which build to run.
disable-model-invocation: true
argument-hint: <feature-spec | path/to/spec.md | tracker-ref>
---

# Plan — feature spec → per-task files (+ optional ADR, + worktree)

Anchor a feature in shared understanding and prior decisions, then produce the artifact `/squid-implement-night` consumes: an **approved Tasks Plan — one `tasks/<NNN>-<slug>.md` file per atomic task** — plus an optional ADR, with a feature branch created and the build optionally kicked off. **Nothing touches the repo until the human gate.**

`$ARGUMENTS` is the raw feature spec — free-form text, a path to a spec file, or a tracker reference. If empty, ask the human for one.

You are the **orchestrator** — a MANAGER. You drive the grilling, launch the Product Architect (PA), offer another grilling round and present the final plan, run the single human gate, set up the workspace, write the approved artifacts, and kick off the chosen build. You do NOT groom, write code, or implement anything yourself.

Read `AGENTS.md` first to confirm the active **tracker mode** (`file` → `tasks/<NNN>-<slug>.md` files; `gh` → one GitHub Issue per task).

**Input:** raw feature spec.
**Output:** decided at the human gate — by default one `tasks/<NNN>-<slug>.md` per atomic task (`status: pending`, `feature: <slug>`; or one GitHub Issue per task) + optional applied glossary additions + an optional new ADR under `docs/adr/` + branch `feat/{slug}` (in a new worktree or the current tree), then optionally the chosen build (`/squid-implement-night` or an `/squid-implement-task` loop). This is exactly what the downstream pipeline consumes.

---

## Step 0 — Resolve the feature spec

If `$ARGUMENTS` is empty, ask the human for the feature (free-form, path, or tracker ref). Otherwise resolve it: `cat` a spec file, load a tracker record, or use free-form text. Surface the resolved spec back in one paragraph.

---

## Step 1 — Grill the spec (Human ↔ /squid-grilling)

Before grooming, sharpen the raw spec with the human. **Invoke the `squid-grilling` skill** — interview the human relentlessly, one question at a time with a recommended answer, until scope, edge cases, non-goals, constraints, and any decisions that warrant an ADR are clear. Anything answerable by reading the codebase — explore instead of asking. The output is a **grilled spec**; carry it into Step 2.

---

## Step 2 — PA grooms → DRAFTS the plan (no writes yet)

Launch ONE Product Architect. It **drafts** everything and hands it back as its final message — it writes **nothing** to disk; the orchestrator writes the approved artifacts into the chosen workspace in Step 5.

```
Agent(
  subagent_type="squid:product-architect",
  prompt="""Feature-level grooming. Read AGENTS.md first. Follow your feature-grooming role.
  Feature (grilled): {grilled spec from Step 1}.
  Decompose into atomic, independently-shippable tasks, numbered (NNN) in dependency order. For EACH task, draft the
  FULL tasks/<NNN>-<slug>.md content: frontmatter `id`, `feature: {slug}`, `status: pending`, then Scope, Acceptance
  Criteria, Out of scope, and an empty `## Log` section.
  Also draft: (a) any new docs/glossary.md terms, and (b) IF the feature warrants non-obvious architectural decisions, a
  SINGLE proposed ADR for the WHOLE feature (Nygard template: Status / Context / Decision / Diagram / Consequences,
  the Diagram a coloured Mermaid system diagram of the design) — ONE ADR that captures the entire design, never one ADR
  per task; its Decision section records every related choice.
  DO NOT WRITE ANYTHING TO DISK — hand everything back as drafts; the human approves and the orchestrator writes them.
  Use the context7 plugin for authoritative library/API usage wherever the feature touches an external framework.
  Return: (1) the ordered task files with their full content, (2) the glossary additions (or 'none'), (3) the proposed
  ADR draft (or 'none')."""
)
```

**Verify before the gate:** the drafts are atomic, ordered by `NNN` in dependency order, and each has acceptance criteria. Re-launch the PA with the gap as feedback if not.

---

## Step 3 — Offer another grilling round, then output the final plan (Human ↔ /squid-grilling)

Before `/squid-plan` moves toward implementation, give the human one explicit chance to sharpen further — then lock and show the final plan.

Ask once with `AskUserQuestion`: **"Another grilling round to sharpen this, or is the plan final?"** → **More grilling** / **It's final**.

- **More grilling** → re-invoke the `squid-grilling` skill on the points the drafts left open, feed the sharpened spec back to the PA (Step 2), and return here. Repeat until the human picks **It's final**. Keep it to genuinely-open questions — *good:* "should deleting an Order cascade to its line-items?"; *bad:* re-opening a settled choice like "maybe switch datastores after all" (that's a fresh `/squid-plan`, not another round).
- **It's final** → **output the final plan in full** so the human reads exactly what will be built before anything is written: every task (`NNN — title`, scope, acceptance criteria, out-of-scope), the glossary additions, and the proposed ADR. This is the human's last look before tasks are created — render it complete, not a teaser.

Why this step: catching a wrong-shaped plan on screen costs one more grilling round; catching it after tasks, a branch, and a build already exist costs the whole downstream pipeline.

---

## Step 4 — HUMAN GATE (blocking)

This is the **only** gate, and it is **mandatory**. It decides everything that touches the repo. Recap the decision inputs, then ask:

```
Feature: {title}
Tasks ({N}):
  1. {NNN-slug} — {title}
  2. ...
Glossary additions: {M new terms, or "none"}
Proposed ADR: {ADR-NNNN "title" — 1-line summary, or "none"}
Task storage (project default): {file → local tasks/*.md | gh → GitHub Issues}   ← from AGENTS.md TRACKER_MODE
```

Then ask with `AskUserQuestion`. The decisions come in **two back-to-back asks — still ONE gate, with no repo writes between them**: Part 2 only matters once the plan is approved, and `AskUserQuestion` caps at four questions per call.

**Part 1 — the plan and its artifacts** (ask together, then act on Q1):

1. **Approve the plan?** — write these {N} tasks? → **Approve** / **Edit** / **Cancel**
2. **Store the tasks where?** — → **Local files** (`tasks/<NNN>-<slug>.md`, committed to the repo) / **GitHub Issues** (one issue per task). Pre-select the project default (`AGENTS.md` `TRACKER_MODE`) and mark it Recommended.
3. **Create the ADR?** — write the proposed ADR to `docs/adr/`? → **Create** / **Skip**  *(omit this question entirely if no ADR was proposed)*
4. **Update the glossary?** — apply the {M} drafted term(s) to `docs/glossary.md`? → **Apply** / **Skip**  *(omit this question entirely if the PA drafted no glossary additions)*

- **Cancel** → stop and discard the drafts; nothing has been written or branched. Do not ask Part 2.
- **Edit** → ask what to add / remove / reorder / re-split; re-launch the PA (Step 2); loop back to this gate.
- **Approve** → ask Part 2, then go to Step 5 carrying every answer.

**Part 2 — workspace and build** (only on Approve):

5. **Workspace?** — where should branch `feat/{slug}` live? → **New worktree** (isolated `../{repo}-{slug}` dir) / **Current working tree** (branch in place)
6. **Build now?** — what runs after setup? → **`/squid-implement-night`** (end-to-end to a validated PR) / **`/squid-implement-task` loop** (build + commit the tasks only, no review/CI) / **Stop after planning**

---

## Step 5 — Execute the decisions (only after the final plan + Approve)

Reached only after Approve at the gate. Do these in order.

**A. Set up the workspace (Q5).**

- **New worktree:**
  ```bash
  git rev-parse --abbrev-ref HEAD          # expect main; if not, ask the human how to proceed
  git pull
  WORKTREE_PATH="$(git rev-parse --show-toplevel)/../$(basename $(git rev-parse --show-toplevel))-{slug}"
  git worktree add -b feat/{slug} "$WORKTREE_PATH" main
  ```
  If it already exists (re-running after an abort): tell the human, ask reuse (`r`) / recreate (`d`) — default reuse.
- **Current working tree:**
  ```bash
  git pull
  git switch -c feat/{slug}                # if already on a feat/* branch, reuse it instead
  ```
  `WORKTREE_PATH` = the repo root.

**B. Write the approved artifacts into the workspace.** Write to **absolute paths under `$WORKTREE_PATH`** (for a new worktree the orchestrator's cwd is still the main repo — do NOT write the tasks into `main`):

- **Tasks (Q2).** **Local files** → one `$WORKTREE_PATH/tasks/<NNN>-<slug>.md` per task (`status: pending`) from the Step 2 drafts. **GitHub Issues** → `gh issue create` one issue per task from the same drafts, in `NNN` order (titles `NNN — {slug}`, body = the groomed spec). The chosen mode is this feature's tracker for the rest of the pipeline; if it differs from `AGENTS.md` `TRACKER_MODE`, it's a one-off override for this plan — don't rewrite `AGENTS.md`.
- **Glossary (Q4).** If **Apply**: apply the drafted additions to `$WORKTREE_PATH/docs/glossary.md`. If **Skip** (or none were drafted): discard them.
- **ADR (Q3).** If **Create**: write `$WORKTREE_PATH/docs/adr/NNNN-<slug>.md` (Status: Accepted) from the ADR draft. If **Skip**: discard the draft.
- **Verify:** in **Local files** mode, `ls "$WORKTREE_PATH/tasks"` lists every expected file, each with `status: pending` + acceptance criteria; in **GitHub Issues** mode, `gh issue list` shows one issue per task. If anything is missing, write it now — do not hand off an empty plan.

**C. Kick off the build (Q6).**

- **`/squid-implement-night`** → invoke `/squid-implement-night` with: feature `{slug}`, `Working directory: $WORKTREE_PATH`.
- **`/squid-implement-task` loop** → invoke `/squid-implement-task` with: the feature's pending tasks (`tasks/<NNN>-*.md`, `status: pending`), `Working directory: $WORKTREE_PATH`. (It loops SWE → Tester → commit per task; no `/squid-review` or `/squid-review-ci`.)
- **Stop after planning** → hand off and stop:
  ```
  Plan approved. {N} tasks in tasks/ (status: pending) on `feat/{slug}` ({worktree at $WORKTREE_PATH | current working tree}).
  Next: run `/squid-implement-night` (builds every pending task to a validated PR), or `/squid-implement-task` for individual tasks.
  ```

`/squid-plan` ends here.

---

## Notes

- **Task-file shape:** see the `tracker-workflow` spec (`squid-scaffold/specs/tracker-workflow.md`).
- **One ADR per plan, not per task.** A feature gets at most ONE new ADR capturing its whole design. The rare exception — a follow-up ADR authored mid-pipeline for an unforeseen architectural fork — lives in the `product-architect` agent contract.
