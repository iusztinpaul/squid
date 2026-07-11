---
name: squid-clean-harness
disable-model-invocation: true
argument-hint: "[.agents-path] (default: ./.agents)"
description: >-
  Shrink an agent harness (.agents/ skills + resources) to the minimum tokens that keep the exact
  same logic. Never touches resources/datasets/.
---

# Clean harness — same logic, minimum tokens

You are the **cleaner**. You shrink the skills and resources a harness loads; you do **not** change
what they make the agent do. Zero logic diff is the contract — every capability, step, and rule that
holds before must hold after; only tokens die.

Output is a **plan table**, approved by the user, then applied as one commit per category.

`$ARGUMENTS` is an optional `.agents/` path (e.g. `~/Vaults/Second-Brain/.agents`). Empty means the
repo's `./.agents`.

## When to use

- The harness has **sedimented** — stale layers of guidance, verbose prompts, dead helpers.
- Sessions burn tokens on skill descriptions and bodies that say little per word.

## When NOT to use — out of scope, no exceptions

| Excluded                                | Why                                                        |
| --------------------------------------- | ---------------------------------------------------------- |
| `resources/datasets/`                   | Data the skills operate **on**, not logic. Never in scope. |
| Memory files (`AGENTS.md`, `CLAUDE.md`) | → `/squid-clean-memory`.                                   |
| Docs, READMEs, comments, docstrings     | → `/squid-clean-docs`.                                     |
| Skill names and argument shapes         | The name is the API — a rename is an edit, not a cleanup.  |

## Step 1 — Resolve the target set

Inventory `skills/*/SKILL.md` and `resources/**` minus `resources/datasets/` under the target
`.agents/`. Everything must be revertible: clean in git, or snapshot first
(`cp -R .agents .agents.bak`) when the tree isn't tracked.

## Step 2 — Audit the contract (frontmatter)

Two questions per skill:

- **Invocation type** — auto-fired by the model, or only typed by the user? User-only →
  `disable-model-invocation: true`, keeping its description out of the always-loaded skill list.
  Flipping also cuts reach from **other skills** — grep the set for the skill's name first (Step 4's
  proof); one referrer means it stays model-invoked.
- **Description** — must match what the body does. Model-invoked → triggers only, one per branch:
  synonyms naming the same branch are duplication ("build with TDD" / "asks for test-first
  development" is one branch written twice). User-only → one sentence of what it does; trigger prose
  serves no router — delete it. A user-only skill with fifteen lines of "use for X, Y, Z" pays those
  tokens for nobody.

Done only when every skill in the set has both answers recorded — no sampling.

## Step 3 — Apply the keep/delete test

**An instruction survives only if deleting it would change what the agent does.** The cuts apply to
every file in the set — skill bodies and `resources/` docs alike, `datasets/` never. Five cuts:

**Duplicates** — the same rule twice in one skill, repeated across skills, or restating a
`resources/` doc the skill already points at (a skill body repeating `glossary.md` definitions) —
the resource is the home, the skill keeps the pointer. Two resources repeating each other collapse
to one home the same way, as does a block ≥2 skills share — **Disclosure** below says where it goes.

**Baked-in claims** — would the agent already behave this way with the line deleted (harness default,
system-prompt rule)? Dead weight. "Read the file before editing it" dies; "write posts in the voice
defined in `resources/branding/`" stays. The test is harness-relative — `.agents/` serves non-Claude
agents too: delete only defaults universal to whatever loads the skill; flag the Claude Code-specific
ones. Test sentence by sentence; a failing sentence dies whole — never trim words from it.

**Verbose logic** — the exact same logic in the minimum words: collapse restatements, prefer a table
row to a paragraph, caveman-terse wording. Collapse a restated quality into one pretrained **leading
word** ("fast, deterministic, low-overhead" → a _tight_ loop) — fewer tokens and a sharper hook. If
the caveman plugin is installed, `/caveman-compress` per file is a good first draft — re-check
afterwards that the frontmatter is still parseable YAML.

**Merges** — steps or sections nobody reads apart become one; reorder so each idea appears once, at
the point the agent needs it.

**Disclosure** — a skill body is paid for on **every** invocation, including the branches that never
read it. Inline what every branch needs; push what only some branches reach — a lookup table, a
per-platform appendix, a rare edge-case procedure — into a `resources/` doc loaded on demand. Same
home for a block ≥2 skills share. Size decides: **~20+ lines earns its own file**, below that
indirection costs a Read for less than it saves. Per-invocation tokens fall even when total words
don't. The pointer's wording, not its target, decides whether the agent reaches the material — say
when to load it, not just where it lives ("for the Slack variants, read `platforms.md`", not "see
`platforms.md`"). Theory: `/squid-write-skill`.

Done only when every file in the set is read whole and judged against all five cuts.

## Step 4 — Dangling artifacts

A reference, script, agent, or `resources/` doc is dead only with **zero references** outside its
own definition:

```sh
grep -rn "helper.py" <harness-root> <project-root>   # prove it, don't assume
```

- A **rule** dangles by staleness, not references — nobody cites a rule, they read it. It dies when
  what it governs no longer exists: a step for a removed tool, a caveat for a branch that's gone.
- Referenced but missing → a broken contract, not a deletion: flag it and ask.
- Present but unreferenced → delete only on clean proof; a helper called from outside `.agents/`
  (cron, vault automation) is invisible to grep — when unsure, flag, never auto-delete.

Done only when every artifact is proven dead, alive, or flagged.

## Step 5 — Plan of attack (the output artifact)

Print one table in chat. Do not write it to disk unless the user asks.

| File                              | Cut (Step 2–4) | Why                                        | ~Words |
| --------------------------------- | -------------- | ------------------------------------------ | ------ |
| `skills/search/SKILL.md`          | frontmatter    | user-only; trigger prose serves no router  | −130   |
| `skills/post/` ∩ `skills/thread/` | duplicate      | shared hook rules → one home in resources/ | −200   |
| `skills/article/SKILL.md`         | verbose        | Step 2 restated three ways                 | −90    |
| `skills/publish/SKILL.md`         | disclosure     | per-platform appendix; 1 of 4 branches     | −240   |
| `resources/glossary.md`           | verbose        | each term defined twice, prose + table     | −150   |

Stop and wait for explicit approval. Do not edit before it.

## Step 6 — Execute

Apply the approved plan, one commit per category (`frontmatter`, `cuts`, `dangling`) so any revert is
surgical.

## Step 7 — Verify

Logic must be provably unchanged before hand-off:

- Every `SKILL.md` frontmatter still parses as YAML with `name` + `description` — unparseable YAML
  loads the skill with **every field silently dropped**.
- Every remaining reference (file, skill, script, agent) resolves, and every disclosed file has a
  pointer that states when to load it.
- Per-file logic diff: every step and rule in the old version is still stated or merged — name its
  new home.
- No skill or argument was renamed.

Anything off: revert that commit (or restore the snapshot), do not "fix forward".

## Step 8 — Hand-off

Report `wc -w` before → after per file, what moved into `resources/`, and every flagged dangling
item. Point the user at `/squid-write-skill` for flagged items that need rewriting rather than
cutting — an edit is theirs to make, and only they can invoke it.

## Notes on shape

- **Fewer tokens, never fewer capabilities.** If a cut loses logic, it is an edit — out of scope.
- **One home per idea.** Shared blocks live in `resources/`; skills reference, never transclude.
- **Datasets are cargo.** `resources/datasets/` is what skills operate on, not how they work — never
  in scope.
