---
name: squid-plan
description: Turn a raw feature spec into an approved Tasks Plan — one markdown file per atomic task under `tasks/` (or one GitHub Issue per task) — plus an optional ADR, glossary additions, branch, and worktree. Grills the human to sharpen the spec, has the Product Architect groom it into draft tasks (reading docs/glossary, proposing an ADR, using context7), offers another grilling round and shows the final plan before any task is created, then runs ONE human gate that decides everything touching the repo — approve the tasks and where to store them (local files vs GitHub Issues), create the ADR, apply the glossary additions, new worktree vs current tree, and which build to run (/squid-implement-night, an /squid-implement-task loop, or stop). Trigger when the user wants to plan a feature before building, or says "/squid-plan".
disable-model-invocation: true
argument-hint: <feature-spec | path/to/spec.md | tracker-ref>
---

# Plan — feature spec → per-task files (+ optional ADR, + worktree)

Anchor a feature in shared understanding and prior decisions, then produce the artifact `/squid-implement-night` consumes: an **approved Tasks Plan — one `tasks/<NNN>-<slug>.md` file per atomic task** — plus an optional ADR, with a feature branch created and the build optionally kicked off. **Nothing touches the repo until the human gate.**

`$ARGUMENTS` is the raw feature spec — free-form text, a path to a spec file, or a tracker reference. If empty, ask the human for one.

You are the **orchestrator** — a MANAGER. You drive the grilling, launch the Product Architect (PA), offer another grilling round and present the final plan, run the single human gate, set up the workspace, write the approved artifacts, and kick off the chosen build. You do NOT groom, write code, or implement anything yourself — and you NEVER start building, or create any task, before the human has seen the final plan and passed the gate.

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

Launch ONE Product Architect. It **drafts** everything and hands it back — it writes **nothing** to disk. The PA returns the drafts as its final message; they live only in the orchestrator's context window until Step 5 writes them. The human approves at the gate; the orchestrator writes the approved artifacts into the chosen workspace in Step 5.

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

**Verify before the gate:** the drafts are atomic, ordered by `NNN` in dependency order, and each has acceptance criteria. Re-launch the PA with the gap as feedback if not. Nothing is on disk yet — that is intentional.

---

## Step 3 — Offer another grilling round, then output the final plan (Human ↔ /squid-grilling)

The PA has drafted the plan, but **nothing is on disk and no task exists yet**. Before `/squid-plan` moves toward implementation, give the human one explicit chance to sharpen further — then lock and show the final plan.

Ask once with `AskUserQuestion`: **"Another grilling round to sharpen this, or is the plan final?"** → **More grilling** / **It's final**.

- **More grilling** → re-invoke the `squid-grilling` skill on the points the drafts left open, feed the sharpened spec back to the PA (Step 2), and return here. Repeat until the human picks **It's final**. Keep it to genuinely-open questions — *good:* "should deleting an Order cascade to its line-items?"; *bad:* re-opening a settled choice like "maybe switch datastores after all" (that's a fresh `/squid-plan`, not another round).
- **It's final** → **output the final plan in full** so the human reads exactly what will be built before anything is written: every task (`NNN — title`, scope, acceptance criteria, out-of-scope), the glossary additions, and the proposed ADR. This is the human's last look before tasks are created — render it complete, not a teaser.

Why this step: catching a wrong-shaped plan on screen costs one more grilling round; catching it after tasks, a branch, and a build already exist costs the whole downstream pipeline. So tasks are created in Step 5, **never** before the human has seen this final plan.

---

## Step 4 — HUMAN GATE (blocking)

This is the **only** gate, and it is **mandatory** — do not skip it, and do not start writing files, creating branches, or implementing before the human answers. It decides everything that touches the repo. The human has just seen the final plan (Step 3); recap the decision inputs, then ask:

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

- **Cancel** → stop. Nothing has been written or branched — that is the whole point of drafting first. Discard the rest; do not ask Part 2.
- **Edit** → ask what to add / remove / reorder / re-split; re-launch the PA (Step 2); loop back to this gate.
- **Approve** → ask Part 2, then go to Step 5 carrying every answer.

**Part 2 — workspace and build** (only on Approve):

5. **Workspace?** — where should branch `feat/{slug}` live? → **New worktree** (isolated `../{repo}-{slug}` dir) / **Current working tree** (branch in place)
6. **Build now?** — what runs after setup? → **`/squid-implement-night`** (end-to-end to a validated PR) / **`/squid-implement-task` loop** (build + commit the tasks only, no review/CI) / **Stop after planning**

---

## Step 5 — Execute the decisions (only after the final plan + Approve)

Reached only after the human saw the final plan (Step 3) and approved at the gate (Step 4). This is where the first task is created — never earlier. Do these in order.

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

- **Grill, groom, re-grill until final, gate last.** The grilling sharpens intent; the PA's grooming turns it into atomic, commit-grain task drafts; Step 3 offers another grilling round and then shows the final plan; the single gate decides everything that touches the repo. Don't skip the grilling — a wrong-shaped plan costs the whole pipeline downstream.
- **The human sees the final plan before any task exists.** Step 3 renders the full final plan, and tasks are created only in Step 5. *Good:* the human reads every task's scope + acceptance criteria, says "it's final," approves, then files are written. *Bad:* writing `tasks/*.md` (or opening Issues) off the PA's draft before the human has seen the final plan — that creates work the human never signed off on.
- **Nothing touches the repo before the gate.** The PA only drafts; the orchestrator writes task files, the ADR, the glossary edit, and creates the branch/worktree **after** the final plan is shown and Approve is given. Cancel leaves the repo untouched.
- **The tasks ARE the plan.** One `tasks/<NNN>-<slug>.md` per atomic task (`status: pending`) — there is no separate plan document. See the [`tracker-workflow`](../squid-scaffold/specs/tracker-workflow.md) spec for the file shape.
- **One gate, then act — never before.** `/squid-plan` must not start implementing (no `/squid-implement-night`, no `/squid-implement-task`) until the human has answered the gate and chosen a build. Storage, ADR, glossary, workspace, and build are all part of the gate, not assumptions.
- **One ADR per plan, not per task.** A feature gets at most ONE new ADR capturing its whole design; the tasks it decomposes into stay atomic and each links back to that single ADR. (A follow-up ADR authored mid-pipeline for an unforeseen architectural fork is the rare exception — see [`product-architect`](../../agents/product-architect.md).)
- **ADRs and glossary additions are human-gated.** The PA *proposes* both; the human decides at the gate (ADR at Q3, glossary at Q4); only the approved docs land under `docs/adr/` and `docs/glossary.md`. The PA authors both files.
- **Storage is chosen at the gate.** Q2 picks where the tasks live — local `tasks/*.md` or GitHub Issues — defaulting to `AGENTS.md` `TRACKER_MODE`. The choice is this plan's tracker downstream; a deviation from the project default is a one-off for this feature, not an edit to `AGENTS.md`.
