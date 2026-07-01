---
name: ubiquitous-language
description: Glossary discipline borrowed from Domain-Driven Design — one canonical name per domain concept, used identically in code, tests, docs, specs, and conversation. Lives at `docs/glossary.md`. Updated by the team, referenced by PA grooming and `/squid-grilling`. TRIGGER when scaffolding a project with non-trivial domain vocabulary (e.g., backend services with named business entities). SKIP for libraries, infra-only projects, or anything where the public surface IS the vocabulary.
---

# Ubiquitous language

A glossary file at `docs/glossary.md` listing every domain concept the team has agreed on, with one canonical name and a one-sentence definition. The full DDD methodology is much larger; this spec borrows only the **glossary discipline**, which is the cheap, load-bearing part: every domain concept has *one* name, and code / tests / docs / specs / Slack all use it.

## When to use

- Backend services with named business entities ("Order", "Settlement", "Subscriber") that already drift between code names, customer-facing names, and database column names.
- Projects with a non-technical stakeholder (product owner, customer) who uses different vocabulary than the engineers — the glossary is the bridge.
- Multi-package monorepos where the same concept appears in several components and you want consistency across them.

## When NOT to use

- Libraries / SDKs where the public API *is* the vocabulary — the API docs serve the same purpose.
- Infrastructure-only projects (a Terraform monorepo, a CI tooling repo) — domain language is "infrastructure", not really domain-shaped.
- Projects with < 5 domain concepts. The glossary's overhead exceeds its value.

## Canonical principles

### One canonical name per concept

When the engineers say "Order", the database column says "order_id", the OpenAPI says "Order", the React component says `OrderCard`, and the customer-facing UI says "Order" — you have a ubiquitous language. When any of those drift ("Purchase" in the UI, "Tx" in the database, "Order" in code), you don't.

The glossary names the canonical term. Code that diverges from it gets renamed in the next refactor.

### Where it lives

```
docs/glossary.md
```

One file, alphabetised by term, per project. For monorepos with strongly-bounded sub-domains, you may have `packages/<c>/docs/glossary.md` for component-local terms — but the root one is canonical for cross-cutting concepts.

### Format

```markdown
# Glossary

The canonical vocabulary for {project}. When code, docs, specs, or conversation use a domain concept, use the term as it appears here.

| Term | Definition | Notes |
|---|---|---|
| **Order** | A customer's request to purchase one or more items, identified by `order_id`. | Use "Order" not "Purchase" or "Transaction". A single Order can have multiple `OrderLine`s. |
| **OrderLine** | One line item within an Order. | Use "OrderLine" not "Item" — "Item" is the catalogue entry, not the line. |
| **Settlement** | The financial reconciliation of an Order after fulfilment. | Distinct from "Payment" (which is the act of charging). |
| **Subscriber** | A customer who has an active recurring billing relationship. | Distinct from "Customer" (any account). |
```

Three columns:

- **Term** — bolded, the canonical name. Code identifiers should match this in casing-appropriate form (`Order` class, `order_id` column, `OrderCard.tsx` component).
- **Definition** — one sentence. If you need two, the concept is probably two concepts.
- **Notes** — distinctions from adjacent terms, common confusions, deliberate exclusions.

### When to update

- A new domain concept enters the codebase → add it to the glossary in the same PR. PR review checks both.
- A team conversation reveals two people are using one word for different things → add the term and the distinction to the Notes column.
- A term is renamed during a refactor → update the glossary in the renaming commit, not after.

The glossary going stale is the failure mode. Treat it as a code artefact: it lives in the repo, it ships in PRs, it gets reviewed.

### How PA grooming and `/squid-grilling` use it

- **PA grooming** (in `/squid-plan`) — the PA reads the glossary before decomposing a feature, and uses canonical terms in every task spec. A task whose AC says "the Item enters the cart" when the glossary says "OrderLine" is wrong-shaped on its face.
- [`/squid-grilling`](../../squid-grilling/SKILL.md) — when a spec uses a non-canonical term, grilling flags it as a question: "Spec says 'Purchase'; glossary says 'Order' — same thing? If yes, we'll use 'Order' in the resolved spec."

The glossary is the tie-breaker when specs and code disagree.

### Boundaries and contexts

If the project has truly distinct sub-domains (e.g., a billing context and a fulfilment context that share concepts but mean different things by them), DDD calls these **bounded contexts**. The cheap version of this discipline:

- Use a section heading per context: `## Billing context`, `## Fulfilment context`.
- A term appearing in both contexts gets one row per context, with the same name only if the meaning is genuinely the same. Otherwise rename one.
- Cross-context translation (when data crosses the boundary) gets its own row in a `## Mapping` section.

Most projects don't need this. Don't reach for it until the team has actually been confused by a shared term.

## Anti-patterns

- **Synonyms in the glossary.** "Order, also called Purchase or Transaction" is the bug, not the cure. Pick one; rename the others in code.
- **Glossary written once and never updated.** A stale glossary is worse than no glossary — it confidently asserts the wrong vocabulary.
- **Glossary as documentation.** It's not docs; it's a vocabulary. Definitions are one sentence, not paragraphs. If you want extended explanation, link from the glossary entry to a doc page.
- **Database column names that don't match the glossary.** When the glossary says "Order" but the table is `tx_records`, the next engineer to join the team will lose half a day. Rename the column (refactor task) or document the deviation explicitly in the glossary's Notes column with a reason.
- **Per-team glossaries that disagree.** One canonical glossary per project, one canonical term per concept. Multiple glossaries → multiple languages → the discipline is dead.

## Bootstrap

Seed `docs/glossary.md` with the 3–5 highest-frequency domain concepts from the project's first feature spec. Don't try to enumerate everything up front — the glossary grows organically as the codebase does. Empty Notes columns are fine; they fill in as confusions surface.

If the project also uses [ADRs](adr.md), an ADR-0002 ("Maintain a project glossary") is a good way to record the team's commitment.
