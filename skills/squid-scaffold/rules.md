# Scaffold rules — single source of truth

Both modes of [`/squid-scaffold`](SKILL.md) consume this file. `mode=create` follows every rule while generating; `mode=evaluate` audits a live repo against the `I#` invariants. No rule is stated anywhere else — `SKILL.md` and [`AGENTS_TEMPLATE.md`](AGENTS_TEMPLATE.md) reference these IDs, they do not restate them.

Two classes of rule:

- **`P#` — Process rules (create-time only).** Govern the *act* of scaffolding. Not checkable from a finished checkout (you can't tell from a repo whether the scaffolder asked before overwriting). `mode=create` only; `mode=evaluate` skips them.
- **`I#` — Artifact invariants (checkable).** Properties the generated output must keep satisfying as the repo evolves. Each carries a `Check:` line — a concrete procedure the evaluate audit walks. Some are marked *monorepo-only* and are N/A for a standalone single-package scaffold.

## Process rules (create-time)

### P1 — Never author application source
Create-time form of [`I1`](#i1--no-application-source-in-the-skeleton): emit only structural / configuration files, with `AGENT: fill in` placeholders where real content is owed.
*Why:* source is the SWE agent's job under `/squid-implement-task`; scaffolding it pre-commits design decisions the team hasn't made.

### P2 — Stop and ask on conflicting choices
If the user's answers conflict (e.g. `cli-tool-python` *and* `fastapi-service` for one backend), ask which one before composing.
*Why:* a guessed resolution bakes a wrong opinion into `AGENTS.md` that everything downstream inherits.

### P3 — Don't overwrite without confirmation
If the target already has an `AGENTS.md` / `CLAUDE.md`, or a `packages/<c>/` for a chosen component, ask before clobbering.
*Why:* `/squid-scaffold` is destructive at the root; an evolved repo must never be silently overwritten.

### P4 — Don't mutate the spec library
`specs/` (and this `rules.md`) are read-only at scaffold time. Edits happen in the plugin repo, never in a consumer project.
*Why:* specs are shared canon; a consumer project must not fork them silently.

### P5 — Ask which tools get `llms.txt` reference links
During create, ask the user which tools / frameworks / external services this project uses that publish an `llms.txt`, and collect each one's index URL. Render them into the `AGENTS.md` "Access Documentation" section per [`AGENTS_TEMPLATE.md`](AGENTS_TEMPLATE.md); everything the user doesn't name is covered by the `context7` fallback already in that section.
*Why:* an `llms.txt` index is the cheapest authoritative doc source, but only the user knows which of their tools publish one and at what URL — guessing ships dead links, and skipping the question loses the cheap path. (Format, e.g.: `**Modal:** https://modal.com/llms.txt`, not a vague "the Modal docs".)

## Artifact invariants (checkable)

### I1 — No application source in the skeleton
The skeleton holds only config/structure files plus `AGENT: fill in` stubs.
*Why:* the skeleton orients; the SWE writes the first real code.
*Check:* `packages/<c>/src/` (or `cmd/`) contains only empty dirs / placeholder files — no non-trivial `.py` / `.tsx` / `.go` logic that the scaffold (not the SWE) authored.

### I2 — `AGENTS.md` ≤ 250 lines
*Why:* past 250 lines you're transcluding specs instead of distilling, and the file stops orienting.
*Check:* `wc -l AGENTS.md` ≤ 250.

### I3 — Distil, don't copy
`AGENTS.md` cites specs; it does not reproduce them. Each Key-Components design note is 1–2 phrases that link out for depth.
*Why:* depth lives in the specs and agent contracts; `AGENTS.md` is the index, not the manual.
*Check:* no verbatim multi-line spec blocks; component notes are short and link to a spec. (Judgment call — read the file, don't grep alone.)

### I4 — `CLAUDE.md` is a symlink to `AGENTS.md`
The root `CLAUDE.md` and every `packages/<c>/CLAUDE.md` is a **relative symlink** to its sibling `AGENTS.md`, created with `ln -s AGENTS.md CLAUDE.md`. `AGENTS.md` is the single source of truth; `CLAUDE.md` exists only so Claude Code — and any harness that reads a file named `CLAUDE.md` — loads the exact same bytes.
*Why:* a symlink gives zero duplication and zero drift (editing `AGENTS.md` updates every harness at once) and is harness-agnostic, whereas an `@AGENTS.md` import only Claude Code understands. *Good:* `CLAUDE.md -> AGENTS.md`. *Bad:* a `CLAUDE.md` whose body is `@AGENTS.md`, or a second copy of the memory file.
*Check:* for the root and each `packages/<c>/`, `test -L CLAUDE.md && [ "$(readlink CLAUDE.md)" = AGENTS.md ]`.

### I5 — `AGENTS.md` follows the template structure
Flat, scope-based `#` (H1) section order running most-fundamental → operational, with `##` subsections, as defined in [`AGENTS_TEMPLATE.md`](AGENTS_TEMPLATE.md). No empty sections.
*Why:* a stable section order keeps every project's memory file navigable by humans and agents.
*Check:* H1 headings appear in template order; sections for absent components are omitted, not left blank.

### I6 — Gate sections on presence
A section or bullet appears iff its component/feature exists. No empty `## Component dependencies` for a single-component repo; no orphan stack bullets; no language runner bullet for an absent language.
*Why:* dead sections train agents to skim past the memory file.
*Check:* for each H1 / bullet, the referenced `packages/<c>/` (or chosen feature) exists.

### I7 — Group Key Components per app *(monorepo-only)*
A multi-app project groups `# Key Components` under a `## <app-name>` subheading per app; a single-product monorepo lists components flat.
*Why:* the memory file should mirror the product boundary the team reasons in.
*Check:* if the repo has >1 app, `## <app>` subheadings are present under `# Key Components`. N/A for standalone / single-app.

### I8 — Fill placeholders inline; leave `AGENT: fill in` literal
The `{...}` braces are instructions to the composer — replace them with concrete content. The `AGENT: fill in` markers are for the SWE agent and stay literal in the output.
*Why:* a leaked `{...}` brace is a generation bug; `AGENT: fill in` is a deliberate, owned TODO.
*Check:* no unresolved `{...}` template placeholders remain in `AGENTS.md` prose (`{` inside code fences, e.g. JSON examples, is fine); `AGENT: fill in` may remain.

### I9 — Stack stubs wrapped in `<!-- stack:<slug> -->` comments
Each external-service bullet is wrapped `<!-- stack:<slug> --> … <!-- /stack:<slug> -->`.
*Why:* `grep '<!-- stack:'` lets a user find-and-delete a service cleanly later.
*Check:* every stack bullet has a matched open/close comment pair with the same slug.

### I10 — Makefile delegates, never reimplements *(monorepo-only)*
Every root `Makefile` recipe is `$(MAKE) -C packages/<c> <verb>` — never a literal `make`, never a `cd` chain. `.PHONY` is built from the emitted verbs and targets are component-gated. Pattern defined in [`specs/makefile-delegator.md`](specs/makefile-delegator.md).
*Why:* `$(MAKE)` propagation plus component-gating keep `make <verb>` predictable as components are added or removed.
*Check:* root `Makefile` recipes match `$(MAKE) -C packages/`; no literal `make ` / `cd ` in recipes. N/A for standalone.

### I11 — Stack stubs are optional and deletable
The `datastore-* / orchestrator-* / observability-* / llm-* / embeddings-* / model-serving-* / scraping-*` references are deletable without breaking anything else.
*Why:* they're pending real-project use; nothing structural depends on them.
*Check:* deleting a `<!-- stack:<slug> -->` block leaves no dangling reference elsewhere in `AGENTS.md` or the skeleton.

### I12 — `.agents/skills/` is canonical; `.claude/skills` symlinks to it
Project-local skills live in `.agents/skills/` — the harness-agnostic single source of truth. `.claude/skills` is a **relative symlink** to it, created with `ln -s ../.agents/skills .claude/skills`, so Claude Code discovers the same skills. Every scaffold creates `.agents/skills/` (seeded with a `.gitkeep` while empty) plus the symlink.
*Why:* the same source-of-truth principle as [`I4`](#i4--claudemd-is-a-symlink-to-agentsmd), one directory up — a project skill is authored once under `.agents/` and every harness sees it; `.agents/` is the emerging cross-tool convention and `.claude/` is the Claude Code adapter. *Good:* `.claude/skills -> ../.agents/skills`. *Bad:* skill files duplicated under both `.claude/skills/` and `.agents/skills/`, or a real `.claude/skills/` directory that shadows `.agents/`.
*Check:* `.agents/skills/` is a real directory; `test -L .claude/skills && [ "$(readlink .claude/skills)" = ../.agents/skills ]`.
