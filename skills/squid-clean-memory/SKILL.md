---
name: squid-clean-memory
disable-model-invocation: true
argument-hint: "[scope-path] (default: every memory file in the repo)"
description: >-
  Shrink the memory files sessions load — the root AGENTS.md plus every nested AGENTS.md /
  CLAUDE.md — to the minimum words that state the same rules: compress wording, delete duplicates
  and harness-enforced claims, merge fragments.
---

# Clean memory — same rules, minimum words

You are the **cleaner**. You shrink the memory files sessions load; you do **not** change what they
instruct. Zero meaning diff is the contract — every rule that holds before must hold after, and no
new rule may appear.

Output is a **plan table**, approved by the user, then applied as one commit per pass.

`$ARGUMENTS` is an optional file or directory scope. Empty means every memory file in the repo: the
root `AGENTS.md` plus each nested `AGENTS.md` / `CLAUDE.md`. Where `CLAUDE.md` symlinks `AGENTS.md`,
that is one file — edit the target, never replace the symlink with a copy.

## When to use

- `AGENTS.md` has organically grown into entropy — `/squid-self-improve` rounds, hand-pasted rules, merged PRs.
- Sessions keep loading guidance that repeats itself, restates harness defaults, or fragments across tiny sections.

## When NOT to use

- Docs, READMEs, comments, docstrings → `/squid-clean-docs`.
- A rule you think is _wrong_ — that is a deliberate edit to make with the user, not a cleanup.

## Step 1 — Resolve the target set

Discover the set with `git ls-files '*AGENTS.md' '*CLAUDE.md'` (tracked files only, so vendored trees
stay out), narrow to `$ARGUMENTS` if given, and collapse symlink pairs. The files must be clean in
git — each pass below commits separately so any revert is surgical.

## Step 2 — Compress wording (caveman pass)

If the caveman plugin is installed, ask, then run `/caveman-compress <file>` on each file in the set
and commit the pass as one commit (code, paths, and URLs are byte-preserved). Not installed → skip;
the cuts below still shrink the files, just without the wording-level pass.

## Step 3 — Apply the keep/delete test

**A memory line survives only if deleting it would change how a future session behaves.** Three cuts:

**Duplicates** — the same instruction stated twice, even reworded — in one file or across the set: a
nested `AGENTS.md` repeating the root dies where it's nested, since the root already loads everywhere.
Keep one home, delete the copies; leave a cross-reference only when the section survives without it.
Moving a rule between files (root ↔ nested) changes where it applies — that is a scope edit, not a
cleanup: flag it in the plan, never fold it into a dedupe.

**Baked-in claims** — the test: would a fresh session with an _empty_ memory file already behave this
way? If yes, the line is dead weight. Caution: `AGENTS.md` is read by non-Claude harnesses too — if
the behaviour is a Claude Code default rather than universal, keep the line and flag it in the plan.

| Delete                                                          | Keep                                                             |
| --------------------------------------------------------------- | ---------------------------------------------------------------- |
| "Always read a file before modifying it." — harness enforces    | "Use `uv run pytest`, never bare `pytest`." — project decision   |
| "Be concise." / "Don't over-engineer." — system-prompt defaults | "Chunk at 200 tokens — the embedding model truncates above 256." |
| Install steps under both _Setup_ and _Contributing_ — one home  | "Never edit `docs/adr/` — ADRs are immutable."                   |

**Merges** — two sections merge when a reader never needs one without the other, or a section is a few
lines sharing a topic with its neighbour. A 3-line _Code style_ plus a 2-line _Naming_ become one
_Conventions_; a heading costs more attention than it organises.

## Step 4 — Plan of attack (the output artifact)

Print one table in chat. Do not write it to disk unless the user asks.

| File            | Lines / section           | Cut (Step 3) | Why                    | ~Words |
| --------------- | ------------------------- | ------------ | ---------------------- | ------ |
| `AGENTS.md`     | "read before you edit"    | baked-in     | harness enforces it    | −9     |
| `api/AGENTS.md` | "use `uv run`, never pip" | duplicate    | root already states it | −11    |
| `AGENTS.md`     | _Code style_ + _Naming_   | merge        | always read together   | −12    |

Stop and wait for explicit approval. Do not edit before it.

## Step 5 — Execute

Apply the approved plan as one commit, separate from the Step 2 commit.

## Step 6 — Verify

Meaning must be provably unchanged before hand-off:

- Re-read each final file against its pre-clean version: every old rule is still stated in a file
  that loads wherever the rule applied, merged, or a planned deletion — name its new home.
- Every path, command, and URL in the files still resolves.
- `git diff` touches only memory files.

Anything off: revert that commit, do not "fix forward".

## Step 7 — Hand-off

Report `wc -w` before → after per file.

## Notes on shape

- **Fewer words, never fewer rules.** If a cut loses a nuance, it is an edit — out of scope.
- **One home per idea.** Duplication is the target; cross-reference, never transclude.
- **Compress before cutting.** The caveman pass normalises wording, so reworded duplicates become
  literal ones — easier to spot in Step 3.
