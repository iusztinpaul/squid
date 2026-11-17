---
name: squid-write-navigation-docs
disable-model-invocation: true
argument-hint: "[repo-path] (default: current repo)"
description: >-
  Write an open-source repo's navigation docs — a short landing-page README for people, guides/
  runbooks for agents (full setup, every run scenario), and the GitHub About description and
  trending topics.
---

# Write navigation docs

You write two kinds of doc, each for one reader:

- **`README.md` is the landing page.** A person decides in 30 seconds whether this repo solves
  their problem, then runs one quickstart. It sells the **transformation** and routes everywhere
  else.
- **`guides/*.md` are the runbooks.** An agent operates the repo from them alone: exact commands,
  env vars, expected output, every scenario.

`$ARGUMENTS` is an optional repo path. Empty means the current repo.

## Step 1 — Survey the repo

Read the existing `README.md`, every doc it links, the task runner (`Makefile`, `package.json`
scripts, `pyproject.toml` entry points), `.env.example`, `.github/workflows/`, `LICENSE`, and the
image dirs (`assets/`, `static/`). Run `git remote get-url origin` and
`git symbolic-ref --short refs/remotes/origin/HEAD` for owner, repo and default branch.

Done when you have **written the inventory**: every install and run command with the file that
defines it; every env var with the file that reads it; the CI workflow file, default branch and
published package name; every image already in the repo; and whether the repo executes code,
holds credentials or sends telemetry (#12's condition).

## Step 2 — Ask for what the repo cannot tell you

One `AskUserQuestion` call (up to 4 questions; a second call only for what remains), only for the
gaps: the problem and the solution, who it is for, which 1–2 examples to feature, article, video
and code-folder links per piece, sponsors (name and link).

**Assets:** in the same round, ask for a source link (URL or local path) for every image the README
needs that the inventory lacks: logo (light + dark), architecture diagram, Decoding AI banner, one
screenshot or GIF per example, sponsor logos. Download each into `assets/` under the name below,
and copy in any inventory image that lives elsewhere (`static/`, `docs/`); the README loads images
only from `assets/`. An asset with no link drops its block (the diagram falls back to Mermaid).

| Asset              | Saved as                                        |
| ------------------ | ----------------------------------------------- |
| Logo               | `assets/logo-light.png`, `assets/logo-dark.png` |
| Architecture       | `assets/architecture.png`                       |
| Decoding AI banner | `assets/decodingai-banner.png`                  |
| Example N          | `assets/example-N.png` (or `.gif`)              |
| Sponsor            | `assets/sponsors/{{sponsor-slug}}.png`          |

Keep the source's extension (`.svg`, `.jpg`) when it is not PNG. Good: `curl -fL <url> -o
assets/architecture.png`, referenced as `assets/architecture.png`; bad: hot-linking
`https://github.com/user-attachments/...` in the README.

Every link and name comes from the repo or the user — good: "sponsor logo `assets/sponsors/qdrant.png`,
given by the user"; bad: "a guessed `youtube.com/@{{repo}}` link".

**Existing README?** Every section gets a destination. Print a move map
(`existing section → README #N | guides/<file> | cut: <reason>`) — it also fixes the `guides/`
file list for Step 3 — and wait for approval before writing anything. Good: "`## Installation` →
guides/01_setup.md"; bad: "move the technical stuff to guides".

Done when every Step 4 section has content or an omission reason from the omission rule, every
asset is in `assets/` or its block is marked dropped, and the move map (if any) is approved.

## Step 3 — Write the runbooks

One file per job under `guides/`, numbered in reading order (`00_` is the lookup, read on failure):

| File                    | Holds                                                                                                |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| `01_setup.md`           | Prerequisites, install, env vars, external services; a `## Cost` table when cost differs by run path |
| `02_running.md`         | Every run scenario (local, Docker, cloud, tests, evals), one `##` per scenario                       |
| `03_{{topic}}.md` …     | Whatever else this repo needs: deploy, data, architecture, project structure, security               |
| `00_troubleshooting.md` | Each known failure as error text → cause → fix, then an `## FAQ`. Only when either has content       |

Runbook rules:

| Rule                                                                                                                                               | Good                                                                                     | Bad                                               |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------- |
| The first line under the title states the end state.                                                                                               | "After this guide `make test` passes on a fresh clone."                                  | "Welcome! Let's get you set up."                  |
| Every command sits in a fenced block, runnable from the repo root.                                                                                 | `uv sync && cp .env.example .env`                                                        | "Install the dependencies and configure env."     |
| A command that can fail is followed by its expected output, copied from a run or the repo's code; otherwise it goes in the hand-off as unverified. | "Prints `Uvicorn running on http://127.0.0.1:8000`."                                     | "The server should now be working."               |
| Every env var is named, with its source and whether it is required.                                                                                | "`OPENAI_API_KEY` — required; platform.openai.com/api-keys"                              | "Add your API keys."                              |
| `01_setup.md`: prerequisites form one table `Tool \| Min version \| Purpose \| Install`.                                                           | "`uv \| ≥0.5 \| Python env + deps \| [install](https://docs.astral.sh/uv/)`"             | "Make sure you have Python and Docker installed." |
| `01_setup.md`: one `###` per external service — sign-up link, env var it fills, free tier or paid.                                                 | "`### Qdrant` — free cloud tier; fills `QDRANT_URL`, `QDRANT_API_KEY`"                   | "Create accounts on the services we use."         |
| `02_running.md`: scenarios follow the order the system runs in, each naming its prerequisite scenario.                                             | "`## Train` — needs `## Generate dataset` to have run"                                   | Scenarios in alphabetical order                   |
| `02_running.md`: each scenario names its code entry point — the first file to open when it breaks.                                                 | "Entry point: `pipelines/feature_engineering.py`"                                        | "The logic is spread across the codebase."        |
| A GitHub alert marks only a step that breaks something if skipped: marker on its own line, one sentence.                                           | `> [!WARNING]` / `> Run make infra-up first — every pipeline needs MongoDB.` (two lines) | A `> [!NOTE]` on every other paragraph            |
| The last line links the next guide by number; the highest-numbered guide and `00_troubleshooting.md` link `../README.md#guides`.                   | "Next: [02_running.md](02_running.md)"                                                   | A guide that dead-ends.                           |

Done when every command and env var in the Step 1 inventory appears in exactly one runbook, and
every runbook rule holds in every file.

## Step 4 — Write the landing page

Sections in this order; headings as written, in sentence case — capitalise only the first word and
words capitalised in prose (`## Who is this for`, not `## Who Is This For`). Budgets are caps; the
whole file is capped at **250 lines**.

| #   | Section                            | Holds                                                                                                     | Budget                                                         |
| --- | ---------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| 1   | Header                             | Logo, title, tagline naming the transformation, nav bar, badges                                           | Tagline ≤ 15 words, 1 nav line, ≤ 4 badges                     |
| 2   | No heading, right after #1         | Problem → solution → **Before / After** line; a library adds its smallest runnable example                | ≤ 4 sentences + 1 line + ≤ 15-line code block                  |
| 3   | `## How it works`                  | Architecture diagram + component bullets                                                                  | 1 diagram, ≤ 5 bullets                                         |
| 4   | `## {{topic headline}}`            | CTA to the Decoding AI Substack and YouTube                                                               | 1 sentence + 2 buttons                                         |
| 5   | `## Quickstart`                    | **Needs** line, clone → install → run on the cheapest path, the result you should see, agent-setup prompt | 1 line + 1 code block ≤ 6 commands + 1 line + the prompt block |
| 6   | `## Guides`                        | Index table `Guide \| Read it when`, one row per `guides/` file                                           | 1 row per guide                                                |
| 7   | `## Who is this for`               | Table `Audience \| What you get`                                                                          | ≤ 3 rows                                                       |
| 8   | `## See it in action`              | 1–2 examples, each: problem → command → screenshot, GIF or output                                         | 1 sentence + 1 command + 1 visual each                         |
| 9   | `## Learn more`                    | Table `# \| Article \| Video \| Code`; each cell is a linked title, text only                             | 1 row per piece                                                |
| 10  | `## Sponsors`                      | Linked logos                                                                                              | 1 row of logos + 1 sentence                                    |
| 11  | `## Questions and troubleshooting` | Link to GitHub issues, `00_troubleshooting.md` when it exists, `CONTRIBUTING.md` when it exists           | ≤ 2 sentences                                                  |
| 12  | `## Security`                      | What runs where, what leaves the machine, link to the runbook that covers it                              | ≤ 3 sentences                                                  |
| 13  | `## {{topic headline}}`            | The #4 CTA block again, same headline                                                                     | The block                                                      |
| 14  | `## Star history`                  | Star-history chart                                                                                        | The block                                                      |
| 15  | `## License`                       | License name linked to `LICENSE`                                                                          | 1 line                                                         |

**Omission rule:** omit #8 when no example exists, #9 and #10 when Step 2 gave nothing for them,
and #12 unless the repo executes code, holds credentials or sends telemetry. Everything else lives
in a runbook.

**Read [`TEMPLATE.md`](TEMPLATE.md) before writing any README section** — it holds the
landing-page rules, the diagram fallback, the exact HTML for #1, #4, #5, #10, #13 and #14, and the
CTA URLs.

Done when every row above is written or omitted per the omission rule.

## Step 5 — Write the GitHub About

The repo's About box is what search results and link previews show. Write both parts:

- **Description:** ≤ 20 words, plain text — what it is, for whom, one checkable fact. Good:
  "Build a coding agent from scratch in Python — tools, memory and evals, explained in 8
  articles."; bad: "🚀 The ultimate next-gen AI framework!"
- **Topics:** fetch `https://trendshift.io/topics` (server-rendered; each `/topics/<slug>` link is
  one topic) and pick the 3–8 slugs that name what the repo does, then add the language and main
  framework from the inventory; ≤ 12 in all, lowercase-hyphenated. Good: `ai-agent`, `mcp`,
  `llm-evaluation`, `python`, `fastapi` for a Python MCP agent; bad: `ai`, `awesome`, `game-engine`
  picked only because it trends.

Print the description and topics with the `gh` command, and run it only after approval:

```bash
gh repo edit {{owner}}/{{repo}} --description "{{description}}" --add-topic {{topic}} --add-topic {{topic}}
```

Done when the description is ≤ 20 words and every topic is a trendshift slug or comes from the
inventory.

## Step 6 — Verify

- `wc -l README.md` ≤ 250, sections in table order.
- `ls guides/` matches the Guides table both ways: every file has a row, every row a file.
- Every image path points into `assets/`, and every relative link, image path and `#anchor` (nav bar included) in `README.md` and `guides/`
  resolves.
- Every command in the docs traces to the Step 1 inventory. Run the quickstart in a fresh clone
  when it needs no secrets.
- `grep -nE '\{\{[a-z][a-z -]*(:|\}\})|TODO' README.md guides/*.md` returns nothing — every
  template placeholder is filled.

Fix every failure and re-run the whole list; done when all checks pass in one run.

## Step 7 — Hand-off

Report the README line count, the guides written, the sections omitted and why, the About
description and topics (and whether `gh repo edit` ran), and every command you could not run or
whose expected output is unverified.
