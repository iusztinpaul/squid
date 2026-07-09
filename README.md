<p align="center">
  <img src="./assets/Squid.png" alt="The Opinionated Squid Logo" />
</p>

<div align="center">
<h1>Squid: An Opinionated Software Factory for Claude Code</h1>
</div>

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-2.1%2B-blue)](https://claude.com/claude-code)
[![Plugin version](https://img.shields.io/github/v/tag/iusztinpaul/squid?label=version)](https://github.com/iusztinpaul/squid/tags)

Claude Code writes code fast. It's worse at writing the code *your team* would actually ship — code that follows your conventions, has tests you trust, and survives review.

**Squid is a [Claude Code](https://claude.com/claude-code) plugin that turns a feature spec into a reviewed PR through a 5-agent pipeline — PA → SWE → Tester → PR Reviewer → On-Call — with exactly two human gates: plan approval and final merge.** No file templates, no render step: just markdown specs and agent contracts, and every file in your project gets written by an agent that reads them.

## How it works

Run `/squid-plan <feature-spec>` then `/squid-implement-night`, and Squid drives this end-to-end:

```
  feature spec
       │
       ▼   /squid-plan
  ┌──────────────────────────────────────────────────────────────┐
  │ grill → PA grooms Tasks Plan (+ADR) → HUMAN approves (1/2)     │
  │ → branch + worktree                                            │
  └──────────────────────────────────────────────────────────────┘
       │   /squid-implement-night  (runs end-to-end in the worktree)
       ▼
  ┌──────────────────────┐    ┌───────────────────┐    ┌─────────────────┐
  │ /squid-implement-task│──▶ │ /squid-review     │──▶ │ /squid-review-ci│
  │ SWE ↔ Tester         │    │ push → PA accept →│    │ On-Call drives  │
  │ commit each task     │    │ PR-Reviewer       │    │ CI to green     │
  └──────────────────────┘    └───────────────────┘    └─────────────────┘
                                                                │
                                                                ▼
                                                    HUMAN squash-merges (2/2)
```

Branch + worktree, grooming, the per-task implement/verify loop, push, diff review, and CI are all automated — you only show up for the two gates. For a quick single change, run `/squid-implement-task <task>` (the same SWE ↔ Tester loop, no planning or review pipeline). Starting from an empty repo? Run `/squid-scaffold` first — it interviews you about the stack and writes a tailored `AGENTS.md` plus a folder skeleton (no application source).

## Who this is for

- **Yes:** solo devs and small teams shipping Python backends, TypeScript frontends, or Go TUIs who want Claude Code to *consistently* hit your team's bar without re-explaining conventions every session.
- **Maybe not:** teams with an established in-house agent pipeline they don't want to displace, or stacks Squid doesn't cover yet (Rust, Java, mobile — [PRs welcome](#contributing)).

## [Learn How to Build Agentic Coding Frameworks From Scratch](https://decodingai.com)

  ▎ Join 40k+ engineers subscribed to [the Decoding AI Magazine](https://decodingai.com) — and learn to build agentic coding frameworks like Squid from scratch.

![Decoding AI Magazine](./assets/decodingai.jpg)

## Install

```
/plugin marketplace add iusztinpaul/squid
/plugin install squid@iusztinpaul
```

That's it. Open any repo in Claude Code; the agents and skills appear in `/agents` and `/help`. Run `/plugin marketplace update iusztinpaul` later to pull fresh changes.

Installing Squid also pulls in three plugins the agent team relies on, all from Anthropic's official `claude-plugins-official` marketplace — `context7` (live library docs via MCP), `code-review`, and `commit-commands`. That marketplace ships with Claude Code, so these resolve and enable on their own. (Requires Claude Code v2.1.143+ for auto-enable; v2.1.110+ for the dependency mechanism. If a dependency fails to resolve, run `/plugin marketplace update claude-plugins-official`.)

### Optional companion: caveman

Squid integrates with [**caveman**](https://github.com/JuliusBrussee/caveman) — an optional plugin that compresses agent output ~75%. It isn't pulled in automatically (it lives in a different marketplace); install it alongside Squid and the pipeline picks it up:

```
/plugin marketplace add JuliusBrussee/caveman
/plugin install caveman@caveman
```

With caveman installed, Squid uses it for:

- **Commits** — the SWE writes each commit via `/caveman-commit` (Conventional Commits, ≤50-char subject, why-over-what).
- **Reviews** — the PR-Reviewer posts one-line findings on the PR in `/caveman-review` style (`L42: bug: user null. add guard.`), on top of its usual rollup task.
- **Memory compression** — `/squid-scaffold` offers to run `/caveman-compress AGENTS.md`, so the memory file every session loads is ~46% leaner.
- **Shorter replies** — caveman's `SessionStart` hook auto-compresses every reply; tune the level with `/caveman [lite|full|ultra]`.

Squid runs fine without it — each integration falls back to its native behavior.

<details>
<summary><b>Per-project install</b> — auto-prompt for everyone who clones a specific repo</summary>

Commit this into the target repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "iusztinpaul": {
      "source": {
        "source": "github",
        "repo": "iusztinpaul/squid"
      }
    }
  },
  "enabledPlugins": {
    "squid@iusztinpaul": true
  }
}
```

When a teammate (or future-you on a fresh machine) opens that repo and trusts the folder, Claude Code prompts them to add the marketplace and install in one step. `enabledPlugins` alone isn't enough — `extraKnownMarketplaces` is what tells Claude Code where `squid@iusztinpaul` resolves to.

</details>

<details>
<summary><b>Local plugin development</b> — test uncommitted changes to Squid itself</summary>

```
claude --plugin-dir /path/to/squid
```

Launches Claude Code with the plugin loaded for the session. No marketplace, no install, no cache. Re-run after edits. This is the only path that exercises your local working tree directly on Claude Code v2.1+.

> `/plugin marketplace add /path/to/squid` reads the local `marketplace.json` but the plugin's `source` points at GitHub — so the install still fetches from `iusztinpaul/squid`, not your working tree.

</details>

<details>
<summary><b>Install just the skills (any agent)</b> — via <code>npx skills</code></summary>

Not on Claude Code, or only want Squid's skills without the full plugin? Use the cross-agent [`skills`](https://github.com/vercel-labs/skills) CLI:

```
npx skills add iusztinpaul/squid
```

It scans the repo for `SKILL.md` files and installs them into whichever agents it detects (Claude Code, Cursor, Codex, and 70+ more). Add `-g` to install into your user directory instead of the current project, or `--skill <name>` to grab specific ones:

```
npx skills add iusztinpaul/squid --skill squid-plan --skill squid-implement-task -g
```

Manage them with `npx skills list`, `npx skills update`, and `npx skills remove <name>`.

> **Skills only.** This installs the `/squid-plan`, `/squid-implement-task`, … skills but **not** Squid's five sub-agents (PA, SWE, Tester, PR-Reviewer, On-Call) or the bundled MCP plugins. The pipeline skills invoke those agents, so the full flow only works through the `/plugin install` path above — reach for `npx skills` when you want individual skills inside another agent.

</details>

<details>
<summary><b>Uninstall</b></summary>

```
/plugin uninstall squid@iusztinpaul
```

To also forget the marketplace (stops it checking for updates):

```
/plugin marketplace remove iusztinpaul
```

Installed via `npx skills` instead? Remove those with `npx skills remove <name>` (add `--global` if you used `-g`, or `--all` to clear everything).

</details>

## Skills & commands

| Surface | What it does |
|---|---|
| `/squid-scaffold` | Interactive bootstrap. Asks what you're building (backend / frontend / TUI / mix), reads the relevant specs, writes a tailored `AGENTS.md`, and lays down an empty folder skeleton. Run `/squid-plan` next to start building. |
| `/squid-plan <feature-spec>` | Plan a feature: grill the spec, PA grooms an approved Tasks Plan (+ optional ADR), create the branch + worktree. Start here. |
| `/squid-implement-night <plan>` | End-to-end single-feature pipeline (the diagram above) — builds the approved plan to a validated PR. |
| `/squid-implement-task` · `/squid-review` · `/squid-review-ci` | Granular pipeline stages, runnable standalone: build tasks · push + acceptance + diff review · CI validation. |
| `/squid-refactor` · `/squid-triage-issue` · `/squid-architecture-review` | Standalone planning/intake helpers (not wired into the main pipeline). |
| `product-architect`, `software-engineer`, `tester`, `pr-reviewer`, `oncall-engineer` | Sub-agents invoked by the pipelines; also usable directly via the `Agent` tool. See [Which model runs which agent](#which-model-runs-which-agent). |
| `squid-testing-python`, `squid-grilling`, `squid-self-improve` | Support skills the pipelines and agents lean on. |

### Which model runs which agent

Squid pins a model per agent, following Anthropic's [advisor pattern](https://x.com/ClaudeDevs/status/2074606058128224365) — reasoning-heavy roles get the strongest model, and the token-hungry executor roles run one tier down, where most of the spend lands.

| Agent | Model | Effort | Why |
|---|---|---|---|
| `product-architect` | `fable` | `high` | Grooms the Tasks Plan and does acceptance review. Pure planning + judgment, and it runs **once per feature** — highest leverage, bounded cost. |
| `pr-reviewer` | `fable` | `high` | Reads one diff and tags Blocker/Nit. Review is judgment, not generation. |
| `software-engineer` | `opus` | `high` | Writes all the code, across every task and every retry — the single biggest token sink in the pipeline. |
| `tester` | `sonnet` | `high` | Full suite + adversarial e2e. High tool-call volume, and verifying is easier than generating. |
| `oncall-engineer` | `sonnet` | `high` | Greps CI logs, root-causes, hands a fix task to the SWE. Never writes app code. |

Two things worth knowing:

- **Fable is for planning, not for coding.** It costs $10/$50 per MTok against Opus's $5/$25 — [benchmarks suggest](https://x.com/morganlinton/status/2074608204403908924) that coding with Fable at high effort buys you roughly what Opus already gives you, for more money. Squid deliberately keeps it off the code-writing path.
- **`effort: high` is a downshift.** Claude Code defaults subagents to `xhigh`. Anthropic's own guidance is to start Opus 4.8 at `high` and only raise it, and Sonnet 5 already defaults to `high`. Drop `software-engineer` to `effort: medium` if you want to trade a little headroom for cost.

**Overriding.** Each value lives in the agent's frontmatter (`agents/*.md`), so a fork can just edit it. Note that a `CLAUDE_CODE_SUBAGENT_MODEL` environment variable **silently overrides every agent's `model:`** — if all five agents seem to be running on one model, that's why.

The `/squid-scaffold` spec library (under `skills/squid-scaffold/specs/`) covers:

- **Python:** backend layout, uv, pyproject, ruff, FastAPI, FastMCP, CLI tools
- **TypeScript frontend:** package/tsconfig/vite conventions, React, Vue, Svelte, vanilla
- **Go TUI:** layout + Bubbletea / tview patterns
- **Infra:** Docker, docker-compose, GitHub Actions monorepo CI, OpenAPI contracts
- **Process:** monorepo layout, Makefile delegator, tracker workflow

Several specs are still stubs — the foundations are filled in (`python-backend`, `typescript-frontend`, `go-tui`, `uv-python`, `pyproject`, `makefile-delegator`, `monorepo-layout`); the rest are good first contributions.

## Contributing

Issues and PRs welcome — especially new specs (Rust, Java, mobile, additional Python/TS frameworks) and stub fill-ins. See [`CONTRIBUTING.md`](CONTRIBUTING.md) to get started, and [`CLAUDE.md`](CLAUDE.md) for the underlying plugin-dev conventions.

## Quick start

In an empty directory:

```
/squid-scaffold
```

The skill asks what you want to build (components, frameworks, infra, license) and writes:

- `AGENTS.md` — project brief distilled from the relevant specs; the single source of truth, with `CLAUDE.md` symlinked to it for Claude Code
- `.agents/skills/` — canonical home for project-local skills, with `.claude/skills` symlinked to it
- Skeleton `packages/<component>/` directories with placeholder Makefiles and component-level `AGENTS.md`s (each with its own `CLAUDE.md` symlink)
- Root `Makefile`, `.env.example`, `.gitignore`
- Optional: `docker-compose.yml`, `.github/workflows/`, `tasks/`

It does **not** write application source. That's the next step:

```
/squid-implement-task "Bootstrap packages/backend with a FastAPI /health endpoint and one unit test."
```

The SWE agent reads `AGENTS.md`, picks up the specs it references, writes real code + tests, hands off to the Tester, and commits the task once it passes.

## Philosophy

- **Specs over templates.** Opinions live as markdown the agent reads — no Jinja, no render step, no drift between a template and what the agent produces.
- **Progressive disclosure.** A session loads only the skills whose descriptions match the task; the spec library is gated behind `/squid-scaffold` so it doesn't pollute every session's index.
- **One skill per concern.** Adding a new stack is one markdown file, not a new scaffolding engine.
- **`AGENTS.md` is the brief.** After `/squid-scaffold`, the generated `AGENTS.md` is the single source of truth for how that project builds. Specs are referenced, not transcluded.
- **Agents are gates.** The PA catches scope drift and signs off from the user's perspective; the Tester catches false-confidence "tests pass" claims and runs an e2e adversarial pass; the PR Reviewer catches dead/duplicate/untested code, over-engineering, and hot-path regressions; On-Call catches CI breakage. No agent both writes code and decides whether it's correct.

## License

See [`LICENSE`](LICENSE).
