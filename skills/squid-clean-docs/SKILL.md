---
name: squid-clean-docs
disable-model-invocation: true
argument-hint: "[scope-path] (default: whole repo)"
description: >-
  Strip redundancy from prose — docs, READMEs, code comments, docstrings — keeping behaviour
  identical.
---

# Clean docs — remove words, keep behaviour

You are the **cleaner**. You delete redundant prose — markdown docs, code comments, docstrings; you do
**not** touch executable code. Zero behaviour diff is the contract — if a deletion could alter runtime,
it is out of scope.

Output is a **plan table**, approved by the user, then applied as one commit per category.

`$ARGUMENTS` is an optional scope path (`docs/`, `src/ingest/`). Empty means the whole repo.

## When to use

- Cluttered docs, READMEs, comments, or docstrings.
- Before a release, to shrink the surface a reader must hold in their head.

## When NOT to use — never touch these without explicit opt-in

| Excluded                                                                               | Why                                                                             |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `docs/adr/`, `docs/notes/`                                                             | ADRs are immutable historical records; notes are the user's.                    |
| `CHANGELOG*`, `LICENSE*`                                                               | Append-only / legally load-bearing.                                             |
| `.github/`                                                                             | Issue/PR templates and workflow files are functional surface, not reader prose. |
| Generated + vendored trees (`node_modules/`, `.venv/`, `dist/`, `vendor/`, `*_pb2.py`) | Not authored; regenerated on build.                                             |
| Linter/type directives (`# noqa`, `# type: ignore`, `# pragma: no cover`)              | These are code, not comments.                                                   |
| Doctest examples (`>>>` blocks in docstrings)                                          | Executable tests, not prose.                                                    |

## Step 1 — Confirm scope

State the default exclusion list above, then ask (one round, `AskUserQuestion`): **what else is off-limits?**
Do not scan until answered.

## Step 2 — Scan

Read every candidate file in scope. Classify each deletion against Step 3's test. Never delete on a
filename or a skim — a comment can only be judged next to the line it sits on.

## Step 3 — Apply the keep/delete test

**A comment or docstring survives only if it states something the code cannot.** A constraint, a
non-obvious _why_, a limit, a workaround and its issue link. If it narrates _what_ the next line does,
it is noise — delete it.

| Delete                                                                           | Keep                                                                            |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `# increment the counter` above `i += 1`                                         | `# Chunk at 200 tokens — the embedding model truncates above 256.`              |
| A docstring restating the signature: `"""Takes a user_id and returns a User."""` | `"""Returns None for soft-deleted users; callers must handle it (see #412)."""` |
| `# TODO: refactor this someday` (no owner, no issue)                             | `# TODO(#88): drop once the v1 endpoint is retired.`                            |
| `# Fixed the bug where...` — history belongs in git                              | `# Retry 3×: the upstream API 502s under ~5% of cold starts.`                   |

**Docs:** a section dies when it duplicates a section that lives elsewhere. Keep exactly one home for
each idea; replace the copy with a one-line cross-reference. A README that repeats `CONTRIBUTING.md`'s
install steps loses them and links instead.

**Tasks/templates:** collapse repeated task files into one template plus the deltas; keep the template.

## Step 4 — Plan of attack (the output artifact)

Print one table in chat. Do not write it to disk unless the user asks.

| File                  | What goes                                     | Rule (Step 3)     | ~Lines |
| --------------------- | --------------------------------------------- | ----------------- | ------ |
| `src/ingest/chunk.py` | 4 narrating comments, 1 signature docstring   | restates code     | −12    |
| `README.md`           | install section duplicating `CONTRIBUTING.md` | one home per idea | −18    |

Stop and wait for explicit approval. Do not edit before it.

## Step 5 — Execute

Apply the approved plan. Commit one category at a time (`comments`, `docs`) so any revert is surgical.

## Step 6 — Verify

Behaviour must be provably unchanged before hand-off:

- Test + lint suite green (`make pre-commit && make unit-tests`, or the project's equivalent) —
  docstring deletions can break doctests and doc builds.
- `git diff --stat` touches only prose and docstrings — **no logic lines**.
- No broken internal links: every path, heading, or anchor you deleted or moved has no remaining
  referrers.

Anything red: revert that commit, do not "fix forward".

## Step 7 — Hand-off

Report lines removed per category and the verify result. If the README was reorganised, say what moved
where.

## Notes on shape

- **Removing beats rewriting.** Prefer deleting a paragraph to shortening it.
- **One home per idea.** Duplication is the target; cross-reference, never transclude.
- **Complements `/caveman-compress`** (if the caveman plugin is installed), which compresses a single
  memory file's _wording_. This skill decides what should exist at all. Run this first, compress after.
