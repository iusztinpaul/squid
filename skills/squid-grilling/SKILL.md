---
name: squid-grilling
description: Interview the user relentlessly about a plan or design. Use when the user wants to stress-test a plan before building, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds of at most 5 questions**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Each round, ask up to 5 frontier questions, most load-bearing first (the ones that unblock the most downstream decisions); the rest wait for the next round. Number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the codebase or environment, dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

---

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling), © 2026 Matt Pocock, [MIT License](https://github.com/mattpocock/skills/blob/main/LICENSE); renamed `squid-grilling`, rounds capped at 5 questions.
