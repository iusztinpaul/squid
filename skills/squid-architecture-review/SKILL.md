---
name: squid-architecture-review
description: Periodic architectural sweep of a codebase — reads existing ADRs to avoid re-litigating settled decisions, maps the current module/dependency graph and layering, surfaces 5–10 architectural smells with severity, and emits each finding as a refactor proposal that `/squid-refactor` can consume directly. Trigger when the user says "/squid-architecture-review", "audit the architecture", "what's wrong with this codebase", asks before a major version bump, or when long-horizon tech debt feels untracked.
disable-model-invocation: false
argument-hint: [scope-path or component name; default = whole repo]
---

# Architecture review — periodic structural audit

The team's day-to-day pipeline (`/squid-implement-task`, `/squid-implement-night`) operates at task grain. Long-horizon codebase health — drift, unintended coupling, dead modules, layering violations — accumulates between tasks and never gets addressed unless someone deliberately looks. This skill is that deliberate look.

The output is **not a single PR**. It's a prioritised backlog of refactor proposals, each shaped so [`/squid-refactor`](../squid-refactor/SKILL.md) can pick one up and turn it into a Tasks Plan.

You are the **auditor** — you delegate exploration to sub-agents, you read [`docs/adr/`](../../../docs/adr/) to avoid re-proposing settled questions, and you produce a written report. You do NOT write code, do NOT start refactors, and do NOT decide priority for the team — you propose, the human prioritises.

`$ARGUMENTS`:

- Empty → audit the whole repo.
- A path (`packages/backend/`) → audit only that subtree.
- A component name (`backend`, `frontend-web`) → audit only that component.

Smaller scopes produce sharper findings; whole-repo audits produce broader maps but blunter recommendations.

## When to use

- The team hasn't done a structural review in 6+ months.
- A major version bump is imminent and you want to clear debt before locking in compatibility.
- A new contributor surfaces "why is X like this?" questions that nobody can answer cleanly.
- A bug was caused by hidden coupling and you suspect more like it exist.
- After a successful `/squid-refactor` lands and you want to find the next one.

## When NOT to use

- During active feature delivery — review when the team has bandwidth to act on findings, not as theatre.
- On a codebase < 6 months old. There isn't yet enough crystallised pattern to review against.
- When the team has clear architectural anxieties already named — go straight to [`/squid-refactor`](../squid-refactor/SKILL.md) with the named target.
- As a substitute for code review on a specific PR — open or update the PR with `gh` and review it there instead.
- On infra-only repos (Terraform, CI tooling). The shape doesn't fit; this skill assumes application code with modules, layers, dependencies.

## Step 1 — Frame the scope

Resolve `$ARGUMENTS`. If empty, ask the user one question via `AskUserQuestion`:

> Whole repo, one component, or a specific subtree?

Echo the resolved scope back as a one-line confirmation. Don't block.

## Step 2 — Read prior decisions

Read [`docs/adr/`](../../../docs/adr/) end-to-end if it exists. Build a mental model of:

- What decisions are **Accepted** and still in force.
- What decisions are **Superseded** (and by what).
- What constraints (technical, business, team-shape) the ADRs cite.

This is the single highest-value step. An architecture review that proposes "split the auth module" when ADR-0005 already explained why it's deliberately combined wastes everyone's time. If ADRs don't exist, note that — recommend [`adr.md`](../squid-scaffold/specs/adr.md) as a prerequisite to capturing this review's outcome.

Also read, if present:

- [`docs/glossary.md`](../squid-scaffold/specs/ubiquitous-language.md) — to know whether the team already names concepts consistently.
- The root `CLAUDE.md` and any per-component `CLAUDE.md` — for stated rules.

## Step 3 — Map the current architecture

Spawn 2–3 Explore agents in parallel:

```
Agent(
  subagent_type="Explore",
  prompt="""Architecture mapping pass on {scope}.

  Produce four artefacts:
  (1) Module / package list with one-line responsibility per module (file:line for the canonical entry point).
  (2) Dependency graph — who imports whom. Flag any cycles. Flag any "junk drawer" modules imported by everyone.
  (3) Layering — name the de-facto layers (e.g., handlers → services → repositories → models) and list any layer-skipping imports.
  (4) Public surface — what's exported / consumed by other components or external callers. Mark anything intended-internal that's leaked.

  Be exhaustive on the dependency graph; missing an edge produces a wrong recommendation. Report as four sections."""
)

Agent(
  subagent_type="Explore",
  prompt="""Hot-spot scan on {scope}.

  Find:
  (1) Files with > 500 lines.
  (2) Files / modules touched by > 30% of commits in the last 6 months — `git log --since='6 months ago' --name-only | sort | uniq -c | sort -rn | head -20`.
  (3) Tests with > 100 setup lines or > 5 fixtures — usually a smell that the system-under-test is too coupled.
  (4) `# TODO` / `# FIXME` / `# HACK` markers — count and cluster.
  (5) Any `# type: ignore` / `eslint-disable` / `nolint` clusters — places where the team is fighting their own static analysis.

  Report as five sections with file:line."""
)
```

When agents return, **read the top-3 most-implicated files yourself**. Don't rely on summaries on the load-bearing modules — you need firsthand familiarity to call findings credibly.

## Step 4 — Identify smells

Walk these dimensions. For each, form 0 or more findings. Don't manufacture findings to pad the report — empty dimensions are fine and signal health.

| Dimension | What to look for |
|---|---|
| **Cycles** | Import cycles between modules / packages. Always a smell. |
| **Layer violations** | Lower layers (e.g., models) importing higher layers (e.g., HTTP handlers). |
| **God modules** | One module that everything imports; usually means responsibilities accreted. |
| **Junk drawers** | `utils/`, `common/`, `helpers/` modules with > 10 unrelated functions. |
| **Hidden coupling** | Two modules that should be independent but share a hidden contract (a shape, a magic string, an env var). |
| **Test smells** | High setup-to-assert ratio; brittle tests on private internals; flaky tests. Usually rooted in a structural problem in the SUT. |
| **API leakage** | Internal types reaching public surface; public surface that should be private (e.g., a route that no caller uses). |
| **Dead code** | Unused exports, unreachable branches, modules with zero importers. |
| **Over-engineering** | Abstraction the code doesn't earn: a single-implementation interface / factory / wrapper that only forwards, a layer with one caller, config nobody sets, hand-rolled logic the stdlib ships, or a dependency duplicating a platform/framework feature. Tag each with the same `delete`/`stdlib`/`native`/`yagni`/`shrink` vocabulary the PR-Reviewer uses (Dimension F). |
| **Drift from CLAUDE.md** | Stated rules the codebase no longer follows. The rule is right; the code drifted. |
| **ADR drift** | Decisions ADRs describe that the code no longer reflects (silently superseded). Either update the ADR or fix the code. |
| **Performance shape** | Sync I/O in async handlers; N+1 patterns; in-memory aggregation that should be a query. |
| **Observability gaps** | Critical paths without logs / metrics / traces; logs that don't include correlation IDs. |

## Step 5 — Score and prioritise

For each finding, assign:

- **Severity:** S1 (active risk — security, data loss, ongoing pain) / S2 (significant friction) / S3 (technical debt without acute symptom) / S4 (cosmetic, defer).
- **Effort:** S (small, ≤ half a day) / M (medium, 1–3 days) / L (large, > 3 days; probably needs to split).
- **Confidence:** High (you've read the code yourself) / Medium (one sub-agent finding, you spot-checked) / Low (sub-agent finding, you haven't verified).

Prioritise by `severity / effort` ratio, with confidence as a tiebreaker. **Do not propose more than 10 findings.** A 30-finding report gets ignored; a 7-finding report gets acted on. Cluster related findings into one if they share a root cause.

## Step 6 — Write the report

Path:

- File mode: `tracker/squid-architecture-review-{YYYY-MM-DD}.md`.
- gh mode: a single issue, label `squid-architecture-review`.

Template:

```markdown
# Architecture review — {scope}, {YYYY-MM-DD}

**Scope:** {whole repo / component / path}
**ADRs read:** {N} ({list, e.g. "0001–0007"})
**Findings:** {N total — by severity: S1×N, S2×N, S3×N, S4×N}

## Summary

{2–3 sentences. The headline shape: "Three module cycles between auth/ and core/, all introduced in the last 4 months, blocking the planned auth-extraction work. Tests on the affected modules have grown 2× in setup size. No ADR governs the boundary. Recommend ADR + extraction refactor."}

## Findings

### F1 — {one-line title} (S{1–4}, effort: {S/M/L}, confidence: {H/M/L})

**Where:** `path/to/a.py:42`, `path/to/b.py:117`

**Symptom:** {what is concretely wrong, observable}

**Root cause hypothesis:** {your best read on why}

**Proposed refactor:** {one paragraph; the shape of the fix, not the fix itself}

**ADR exposure:** {does an ADR govern this? if yes, cite. If no, an ADR should accompany the refactor.}

**Out of scope (explicit):** {what this finding is NOT recommending}

### F2 — ...

(Repeat for each finding, top to bottom by priority.)

## Not recommended

{Smells you found but are deliberately NOT proposing. State why — e.g., "F-skip-1: The `utils/strings.py` module has 12 unrelated functions and looks like a junk drawer. Skipping because every function is < 10 lines and the cost of splitting exceeds the reading cost."}

## Pre-existing decisions (from ADRs) you should NOT undo

{One-bullet-each summary of ADRs that explain *why* something looks weird but is intentional. This protects the next reader from re-litigating.}

## Suggested order of operations

1. F{best-first} — {why it goes first}
2. F{next} — {why}
...

Each finding above can be picked up by `/squid-refactor F{N}` (paste the finding's body into the refactor goal). Don't tackle all of them at once — pick the top 1–3 and run them through the pipeline first.
```

## Step 7 — Hand off

Single block:

```markdown
## Architecture review complete — {scope}

**Report:** {path or issue URL}
**Findings:** {N} ({severity breakdown})
**Top recommendation:** F1 — {title}

### Recommended next step

`/squid-refactor F1` (or paste the F1 body into a fresh `/squid-refactor` invocation). The first finding is the highest leverage by severity-over-effort.

### Open question (if applicable)

{Anything you found but couldn't conclude on without team input — e.g., "F4 hinges on whether the auth/billing boundary should be a hard-coded contract or a feature-flag-toggled split. Surfacing for team decision before refactoring."}

### ADR action

{One of:}
- "Recommend ADR-{NNNN} to record the resolution of F{X} when its refactor lands."
- "No ADRs in `docs/adr/` — recommend bootstrapping with [`adr.md`](../squid-scaffold/specs/adr.md) before proceeding so this review's findings stay durable."
```

## Notes on shape

- **The ADR read is non-negotiable.** Half the findings in a poorly-scoped review are decisions the team already made and rejected. Reading ADRs first is the cheapest way to be useful.
- **Cap findings at 10.** Past 10, the report becomes a wishlist; the team picks zero. Force prioritisation by enforcing the cap.
- **Confidence affects priority.** A High-confidence S2 beats a Low-confidence S1 — don't recommend a refactor on a finding you haven't personally read.
- **Propose, don't prescribe.** This skill outputs *findings with proposed refactors*. The team prioritises. `/squid-refactor` then plans. `/squid-implement-night` then executes. Skipping ahead to "we should do X" pre-commits the team.
- **Don't re-litigate.** The "Pre-existing decisions" section is a discipline — it prevents the next architecture review (or the next contributor) from undoing things that are intentional.
- **Empty findings = signal.** If a dimension produced no finding, say so explicitly ("Layer violations: none observed"). It's information.
- **Pair output with ADR proposals.** Every accepted refactor that lands deserves an ADR if its decision wasn't already governed. Otherwise the next review re-finds it.
