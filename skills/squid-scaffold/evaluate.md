# Scaffold — evaluate mode

`mode=evaluate` audits an *existing* scaffolded repo against the artifact invariants in [`rules.md`](rules.md) and reports drift. **You are the auditor — you do NOT apply fixes, you report.** The flow is read-only on the target repo; the report is printed to chat (no file is written).

## E1 — Resolve target

`$ARGUMENTS` after `mode=evaluate` is the target repo root (default: the current working directory). Echo it back in one line. If there is no `AGENTS.md` there, stop with a clear message: *"Nothing scaffolded to evaluate at `{path}` — run `mode=create` first."*

## E2 — Spawn the audit sub-agent

Launch a single `Explore` sub-agent. It reads the rules from the **plugin's** scaffold skill dir and audits the artifacts in the **target** repo — keep those two locations distinct in the prompt:

```
Agent(
  subagent_type="Explore",
  prompt="""Scaffold-conformance audit of the repo at {target path}.

  AUTHORITATIVE RULES (read from the squid plugin's scaffold skill dir, NOT the target repo):
  read `skills/squid-scaffold/rules.md` end to end, and `skills/squid-scaffold/AGENTS_TEMPLATE.md` for
  structure questions. Audit ONLY the `I#` artifact invariants — skip every `P#` (those are
  create-time and not checkable from a checkout).

  ARTIFACTS UNDER AUDIT (in the target repo at {target path}): read `AGENTS.md` and the root
  `Makefile`; verify with `ls -l` / `readlink` (not by reading bodies — a symlink read follows
  transparently to `AGENTS.md`) that the root `CLAUDE.md` and every `packages/*/CLAUDE.md` are
  symlinks to their sibling `AGENTS.md` (`I4`) and that `.claude/skills` is a symlink to
  `../.agents/skills` with `.agents/skills/` a real directory (`I12`); and scan the skeleton
  tree (`ls -R`, not file bodies).

  For EACH `I#` rule, run its `Check:` procedure and return one row:
    `rule id | PASS | VIOLATED | N/A | evidence (file:line or command output) | one-line remediation`.
  Mark a rule N/A (not VIOLATED) when it doesn't apply — e.g. monorepo-only rules (I7, I10) on a
  standalone single-package repo. Quote rules by ID only — do NOT paste rule text into your output.
  Do NOT propose code changes beyond the one-line remediation. Return the table plus a 2–3 sentence
  health summary."""
)
```

## E3 — Compose the report (to chat)

Read the target's `AGENTS.md` yourself first — the judgment-call invariants (`I2` size, `I3` distil, `I5` structure) need a firsthand read, not just the sub-agent's grep. Then print:

- A 2–3 sentence headline summary (the main drift, or "no drift").
- **Violations** — one block per VIOLATED rule: reference the rule by ID (e.g. `see rules.md#I2` — do **not** restate the rule text), the evidence (`file:line`), and a one-paragraph remediation describing the *shape* of the fix (not a patch).
- **Passing** — a terse one-line list of the PASS rule IDs.
- **N/A** — an explicit list of N/A rules with the one-line reason (e.g. "I7, I10 — standalone repo, no monorepo Makefile/per-app grouping").

## E4 — Hand off

Single block: result counts, the violated IDs, and the recommended next step — either *"Edit AGENTS.md to resolve {IDs} — see remediations above, then re-run `/squid-scaffold mode=evaluate` to confirm"* or *"No drift — AGENTS.md still conforms."*
