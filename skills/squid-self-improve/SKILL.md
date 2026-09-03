---
name: squid-self-improve
description: >-
  Analyze developer corrections from the current coding session and persist lessons learned as
  rules in AGENTS.md files or memory. Use at the end of a session after the developer corrected
  your work, or when they ask to capture what was learned.
---

# Self-Improvement from Developer Feedback

After a coding session where the developer reviewed and corrected your work, this skill extracts reusable rules from those corrections and persists them so future sessions benefit — even if context is lost.

Run this **before** wrapping up the session so improvements are saved while the full conversation is still in context.

## Step 1: Scan the Conversation for Corrections

Review the entire conversation history and identify every instance where the developer:

- **Rejected** your approach ("no, don't do it that way", "that's wrong")
- **Modified** your code or suggestion (edited files after you wrote them, rewrote your implementation)
- **Redirected** your strategy ("use X instead of Y", "we don't do it like that here")
- **Corrected** a misunderstanding ("that's not what I meant", "the requirement is actually...")
- **Expressed frustration** with a pattern ("stop doing X", "I told you already")
- **Confirmed a non-obvious choice** ("yes, exactly like that", "perfect, keep doing that") — these are just as important as corrections because they validate approaches that should be repeated

Collect each correction as a raw observation with:
- What you originally did or proposed
- What the developer changed it to or asked for instead
- Any reasoning the developer gave (the "why")

## Step 2: Extract Rules

For each correction (or group of related corrections), distill a concrete, actionable rule. Good rules are:

**Specific and actionable** — they tell future-you exactly what to do:
- "When writing fixtures for async ODM models, always use the real async client, never `mongomock`"
- "Run `make format-fix` before committing, not after"
- "For this project, prefer `httpx` over `requests` for all HTTP calls"

**Not vague platitudes** — these are useless:
- "Follow best practices"
- "Write clean code"
- "Be more careful"

**Grouped when related** — if the developer corrected the same underlying issue multiple times (e.g., kept adding type hints you forgot), that's one rule, not five.

**Skipping one-offs** — if a correction was purely about a specific bug or a unique situation that won't recur, don't create a rule for it. The fix is already in the code.

For confirmed/validated approaches, frame the rule positively: "Continue using X pattern when Y" with a note that this was validated by the developer.

## Step 3: Present Rules for Approval

Show the developer all extracted rules in a numbered list. For each rule, include:

1. **The rule** — the concrete instruction
2. **Why** — the developer's reasoning (or your best understanding of it)
3. **Evidence** — brief reference to when this came up in the session
4. **Where to persist** — your recommendation for where this rule should live:
   - `AGENTS.md` (project root) — project-wide conventions, architecture decisions, coding standards
   - `AGENTS.md` (local, in a subdirectory) — module-specific conventions
   - `feedback memory` — personal preferences about collaboration style
   - `project memory` — project context, goals, constraints, deadlines
5. **Conflicts** — any existing rules this might contradict (see Step 4)

Ask the developer to:
- Approve, edit, or reject each rule
- Confirm or change the persistence location
- Resolve any conflicts you flagged

Do NOT persist anything without explicit approval.

## Step 4: Check for Contradictions

Before presenting rules, scan for conflicts:

1. **Read all AGENTS.md files** in the project (root and any subdirectories)
2. **Read the memory index** at `~/.claude/projects/*/memory/MEMORY.md` and any referenced memory files that seem related
3. **Compare** each new rule against existing rules

If a new rule contradicts an existing one:
- Flag it clearly: "New rule X conflicts with existing rule Y in `AGENTS.md:line N`"
- Present both versions to the developer
- Ask which to keep, or whether to merge them

If a new rule duplicates an existing one:
- Skip it and note: "Already captured in `AGENTS.md:line N`"

## Step 5: Persist Approved Rules

For each approved rule, persist it to the agreed location:

### AGENTS.md updates
- Read the target AGENTS.md file first
- Find the most appropriate section for the rule (or suggest creating a new section if none fits)
- Add the rule concisely — AGENTS.md should stay scannable, not become a novel
- Use the existing formatting style of the file

### Memory updates
- Use the memory system's frontmatter format
- For feedback memories: lead with the rule, then `**Why:**` and `**How to apply:**`
- For project memories: lead with the fact/decision, then `**Why:**` and `**How to apply:**`
- Update MEMORY.md index if creating new memory files
- Update existing memory files if the new rule extends or refines an existing memory

### After persisting
- Show the developer exactly what was written and where
- If a AGENTS.md was modified, show the diff

## Step 6: Summary

End with a brief summary:
- How many rules were extracted
- How many were persisted (and where)
- How many were skipped or already existed
- Any conflicts that were resolved

## Important Principles

- **Persistence is the whole point.** The value of this skill is that lessons survive beyond the current session. If you extract rules but don't write them down, you've wasted the developer's time.
