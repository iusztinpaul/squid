---
name: adr
description: Architecture Decision Records — `docs/adr/NNNN-title.md` files capturing one decision each (Status / Context / Decision / Diagram / Consequences, with a coloured Mermaid system diagram). When to write one, when not to, the canonical Nygard template, and the lifecycle (proposed → accepted → superseded). TRIGGER when scaffolding a project that will accumulate non-obvious architectural choices, or when an existing project keeps re-litigating the same decisions. SKIP for solo prototypes or repos where every decision is self-evident from the code.
---

# Architecture Decision Records (ADRs)

An ADR is a short markdown doc capturing **one** architectural decision with enough context that a reader six months from now (including future-you) can understand *why* the codebase looks the way it does. Originated in Michael Nygard's [2011 post](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions); the canonical four-section template (Status / Context / Decision / Consequences) is what most teams converge on. We extend it with one section — a **Diagram** (coloured Mermaid) that makes the change visible at a glance.

## When to use

- An architectural choice has costs the code doesn't explain (e.g., "we don't use ORM joins because read traffic is replicated and the lag breaks invariants").
- A choice the team has now re-litigated twice — write it down so it stops coming back.
- A choice that locks in an external dependency (DB engine, message bus, framework) — future readers need the reasoning, not just the import.
- A choice that constrains future work (e.g., "all new endpoints must be async" — the constraint and its reason go in an ADR, the rule itself goes in CLAUDE.md).

## When NOT to use

- Decisions that are obvious from the code or the language idiom. ("We use Pydantic for validation" — yes, everyone using FastAPI does that.)
- Implementation choices inside a single module. ADRs are for cross-cutting decisions; `// why this loop has an off-by-one` belongs in a comment.
- Coding conventions and style — those go in CLAUDE.md or a linter config, not an ADR.
- Decisions you might unwind tomorrow. ADRs are for things you intend to live with.

## Decision tree

```
1) Will future-you (or a new contributor) read the code in 6 months and ask "why this and not the obvious alternative?"
   → write an ADR.

2) Is this a coding convention, a style rule, or a tooling preference?
   → CLAUDE.md or a linter config. Not an ADR.

3) Is this a decision local to one function or module?
   → comment in the code. Not an ADR.

4) Did the team just argue about this for an hour and reach a conclusion?
   → write an ADR while the reasoning is fresh.
```

## Canonical principles

### Location and filename

```
docs/adr/0001-record-architecture-decisions.md
docs/adr/0002-use-postgresql-for-primary-store.md
docs/adr/0003-async-by-default-for-new-endpoints.md
```

- Always `docs/adr/`. Always 4-digit zero-padded numbering.
- Filename: `NNNN-kebab-case-title.md`. The title in the filename matches the document's `# Title` heading.
- Numbering is **monotonic** — never reused. Superseded ADRs keep their number; the new ADR gets the next number and links back.
- The first ADR (`0001`) is always "Record architecture decisions" — meta, declares the team uses ADRs, documents the convention. Subsequent ADRs link back to it.

### Template (Nygard)

````markdown
# {NNNN}. {Title}

**Status:** Proposed | Accepted | Superseded by [{NNNN}](NNNN-...md) | Deprecated
**Date:** YYYY-MM-DD

## Context

{What's the situation? What forces are at play (tech, business, team)? Be concrete — name specific systems, constraints, deadlines. The reader needs enough context to evaluate whether the decision still applies if any of these forces change.}

## Decision

{What did we decide to do? One paragraph max. State the decision in active voice ("We will use PostgreSQL...") not passive voice ("PostgreSQL has been chosen...").}

## Diagram

{Make the change visually graspable. At minimum a **system/architecture diagram** showing the components and how they interact *after* this decision; add more (sequence, data-flow, state) — as many as it takes to see the change at a glance. **Use Mermaid** fenced blocks (```mermaid) so the diagram renders on GitHub, lives in version control, and diffs as text. **Colour the diagram** — use `classDef` / `style` to group or highlight nodes (new components vs existing, or by layer) so the change reads at a glance; never ship a monochrome diagram. If a before→after contrast clarifies the change, show both. For a purely procedural decision with no system structure to draw, write "No diagram — this decision changes no system structure."}

```mermaid
graph TD
  Client -->|HTTP| API[API service]
  API -->|enqueue| Queue[[Task queue]]
  API --> DB[(PostgreSQL)]
  Worker --> Queue
  Worker --> DB

  classDef existing fill:#dbeafe,stroke:#1e40af,color:#1e3a8a;
  classDef added fill:#dcfce7,stroke:#166534,color:#14532d;
  class Client,API,DB existing
  class Queue,Worker added
```

## Consequences

{What becomes easier? What becomes harder? What did we deliberately give up? Name the trade-offs explicitly so a future reader knows we considered them.}
````

That's it — Status, Context, Decision, Diagram, Consequences. Don't add sections beyond these; the discipline of "one decision, drawn and reasoned" is the whole point.

### Status lifecycle

- **Proposed** — drafted, not yet team-agreed. Status while a PR adding the ADR is in review.
- **Accepted** — merged. The decision is live.
- **Superseded by [NNNN]** — replaced by a newer ADR. The original is **not deleted**; the new ADR explains what changed and why. Both stay in version control.
- **Deprecated** — the decision is no longer in force, but no replacement exists. Rare; usually means the constraint that motivated the decision is gone.

Never edit an Accepted ADR's substance. Either supersede it (new ADR) or correct typos / tighten prose. The ADR's value is its frozen-in-time view.

### Cross-references

- ADR-0001 → no parent.
- Every other ADR → cite the prior decisions it depends on or contradicts.
- CLAUDE.md → may link to ADRs to explain *why* a rule exists ("All new endpoints must be async — see [ADR-0003](docs/adr/0003-...)").

### How long should an ADR be?

One page — Context 80–200 words, Decision 30–80, Consequences 60–150, Diagram prose a one-line caption. Doesn't fit on a page → the decision is too big, split it. Fits in three sentences → a code comment will do.

## Anti-patterns

- **An ADR for every ticket.** ADRs are for architecture, not feature delivery — most tickets don't need one. When a feature *does* warrant one, its whole design goes in a **single** ADR (one plan → at most one new ADR).
- **Aspirational ADRs.** Don't write ADRs for decisions you might make. Wait until the team has actually committed.
- **ADRs as design docs.** Design docs explore options; ADRs record decisions. If you're still listing alternatives, you're writing a design doc — finish it, then write the ADR with the resulting decision.
- **Skipping numbers.** Monotonic, contiguous. If an ADR is abandoned mid-draft, repurpose its number for the next decision rather than leaving a gap.
- **Burying the decision.** Sentence one of the Decision section is the decision. Don't bury it in narrative.

## Bootstrap

Drop ADR-0001 into a new project as the first ADR. Recommended body:

```markdown
# 0001. Record architecture decisions

**Status:** Accepted
**Date:** {YYYY-MM-DD}

## Context

We expect to make architectural decisions over the lifetime of this project — choices that the code itself doesn't fully explain (which datastore, which queue, which async model, which auth boundary). Six months from now, we will not remember why we chose what we chose. Without a record, we will re-litigate the same decisions and probably reach different conclusions.

## Decision

We will use Architecture Decision Records, as described by Michael Nygard, stored in `docs/adr/` as `NNNN-kebab-title.md`. Each ADR has five sections: Status, Context, Decision, Diagram (a coloured Mermaid system diagram of the change), Consequences.

## Diagram

No diagram — this decision changes no system structure.

## Consequences

- Every non-obvious architectural choice gets a one-page record.
- New contributors can read `docs/adr/` to understand why the codebase is shaped the way it is.
- Prior ADRs are read during planning to avoid re-proposing settled questions.
- Cost: ~30 minutes per ADR. We accept this cost because the alternative — re-deriving past reasoning — is more expensive.
```
