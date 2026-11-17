---
name: squid-write-navigation-docs
disable-model-invocation: true
argument-hint: "[repo-path] (default: current repo)"
description: >-
  Write an open-source repo's navigation docs — a short landing-page README for people plus
  guides/ runbooks for agents (full setup, every run scenario).
---

# Write navigation docs — landing page for people, runbooks for agents

You write two kinds of doc, each for one reader:

- **`README.md` is the landing page.** A person decides in 30 seconds whether this repo solves
  their problem, then runs one quickstart. It sells the **transformation** and routes everywhere
  else.
- **`guides/*.md` are the runbooks.** An agent operates the repo from them alone: exact commands,
  env vars, expected output, every scenario.

Each fact has one home. Setup detail lives in a runbook; the landing page links to it.

`$ARGUMENTS` is an optional repo path. Empty means the current repo.

## Step 1 — Survey the repo

Read the existing `README.md`, every doc it links, the task runner (`Makefile`, `package.json`
scripts, `pyproject.toml` entry points), `.env.example`, `LICENSE`, and the image dirs (`assets/`,
`static/`). Run `git remote get-url origin` for the owner and repo name.

Done when you can list every install and run command with the file that defines it, and every
env var with the file that reads it.

## Step 2 — Ask for what the repo cannot tell you

One `AskUserQuestion` round, only for the gaps: the problem and the solution, who it is for, which
1–2 examples to feature, article + video links, sponsors (name, link, logo path). Every link and
name comes from the repo or the user; a section left without content is omitted.

**Existing README?** Relocate: every technical detail it holds moves into a runbook. Print a move
map (`existing section → destination file`, or `→ cut: <reason>`) and wait for approval before
writing anything.

## Step 3 — Write the runbooks

One file per job under `guides/`, numbered in reading order (`00_` is the lookup, read on failure):

| File                    | Holds                                                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `01_setup.md`           | Prerequisites with versions, install, every env var and where to get its value; a `Path \| Cost` table when cost differs by run path |
| `02_running.md`         | Every run scenario (local, Docker, cloud, tests, evals), one `##` per scenario                                                       |
| `03_<topic>.md` …       | Whatever else this repo needs: deploy, data, architecture, project structure                                                         |
| `00_troubleshooting.md` | Each known failure as error text → cause → fix, then an `## FAQ`. Only when either has content                                       |

Runbook rules:

| Rule                                                                                                   | Good                                                                         | Bad                                               |
| ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------------- |
| First line states the end state.                                                                       | "After this guide `make test` passes on a fresh clone."                      | "Welcome! Let's get you set up."                  |
| Every command sits in a fenced block, runnable from the repo root.                                     | `uv sync && cp .env.example .env`                                            | "Install the dependencies and configure env."     |
| Every command that can fail is followed by its expected output.                                        | "Prints `Uvicorn running on http://127.0.0.1:8000`."                         | "The server should now be working."               |
| Every env var is named, with its source and whether it is required.                                    | "`OPENAI_API_KEY` — required; platform.openai.com/api-keys"                  | "Add your API keys."                              |
| `01_setup.md`: prerequisites form one table `Tool \| Min version \| Purpose \| Install`.               | "`uv \| ≥0.5 \| Python env + deps \| [install](https://docs.astral.sh/uv/)`" | "Make sure you have Python and Docker installed." |
| `01_setup.md`: one `###` per external service — sign-up link, env var it fills, free tier or paid.     | "`### Qdrant` — free cloud tier; fills `QDRANT_URL`, `QDRANT_API_KEY`"       | "Create accounts on the services we use."         |
| `02_running.md`: scenarios follow the order the system runs in, each naming its prerequisite scenario. | "`## Train` — needs `## Generate dataset` to have run"                       | Scenarios in alphabetical order                   |
| `02_running.md`: each scenario names its code entry point — the first file to open when it breaks.     | "Entry point: `pipelines/feature_engineering.py`"                            | "The logic is spread across the codebase."        |
| A GitHub alert (`> [!WARNING]`) marks only a step that breaks something if skipped; one sentence.      | "`> [!WARNING]` Run `make infra-up` first — every pipeline needs MongoDB."   | A `> [!NOTE]` on every other paragraph            |
| The last line links the next guide; the last guide links the README's Guides table.                    | "Next: [02_running.md](02_running.md)"                                       | A guide that dead-ends.                           |

## Step 4 — Write the landing page

Sections in this order; headings as written. Budgets are caps, and the default for the whole file
is **250 lines**.

| #   | Section                               | Holds                                                                                                                                          | Budget                                                         |
| --- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| 1   | Header                                | Logo, title, tagline naming the transformation, nav bar, badges                                                                                | Tagline ≤ 15 words, 1 nav line, ≤ 4 badges                     |
| 2   | `## What Is This`                     | The problem, then how this repo solves it, then a **Before / After** line; a library adds its smallest runnable example                        | ≤ 4 sentences + 1 line + ≤ 15-line code block                  |
| 3   | `### How It Works`                    | Architecture diagram + one bullet per main component naming its tool, directly under #2                                                        | 1 diagram, ≤ 5 bullets                                         |
| 4   | `## <headline for this repo's topic>` | CTA to the Decoding AI Substack and YouTube                                                                                                    | 1 sentence + 2 buttons                                         |
| 5   | `## Quickstart`                       | A **Needs** line, clone → install → run on the cheapest path, the result you should see, then the agent-setup prompt                           | 1 line + 1 code block ≤ 6 commands + 1 line + the prompt block |
| 6   | `## Guides`                           | Index table `Guide \| Read it when`, one row per `guides/` file                                                                                | 1 row per guide                                                |
| 7   | `## Who Is This For`                  | Table `Audience \| What you get`                                                                                                               | ≤ 3 rows                                                       |
| 8   | `## See It Work`                      | 1–2 examples, each: problem → command → screenshot, GIF or output                                                                              | 1 sentence + 1 visual each                                     |
| 9   | `## Go Deeper`                        | Table `# \| Article \| Video \| Code`; each cell is a linked title, text only                                                                  | 1 row per piece                                                |
| 10  | `## Sponsors`                         | Linked logos                                                                                                                                   | 1 row of logos + 1 sentence                                    |
| 11  | `## Questions and Troubleshooting`    | Link to GitHub issues + `00_troubleshooting.md` when it exists                                                                                 | ≤ 2 sentences                                                  |
| 12  | `## Security`                         | What runs where, what leaves the machine, link to the sandboxing guide. Only when the repo executes code, holds credentials or sends telemetry | ≤ 3 sentences                                                  |
| 13  | `## <headline for this repo's topic>` | The #4 CTA block again, same headline                                                                                                          | The block                                                      |
| 14  | `## Star History`                     | Star-history chart                                                                                                                             | The block                                                      |
| 15  | `## License`                          | License name linked to `LICENSE`                                                                                                               | 1 line                                                         |

Omit #9 and #10 when Step 2 gave nothing for them, and #12 when its condition fails. Everything else a README usually carries —
full prerequisites, project structure, FAQ (in `00_troubleshooting.md`), contributing — lives in a runbook or
`CONTRIBUTING.md` and earns at most a Guides row.

**Read [`TEMPLATE.md`](TEMPLATE.md) before writing #1, #4, #5, #10, #13 and #14** — it holds their exact
HTML and the CTA URLs.

**Diagram (#3):** use an architecture image already in the repo; otherwise write a Mermaid
`flowchart LR` of ≤ 8 nodes, each node a component a reader can find in the tree.

Landing-page rules:

| Rule                                                                                      | Good                                                                                          | Bad                                                     |
| ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Open on the reader's problem, then the solution.                                          | "Notes pile up unread. This turns 500 Notion pages into an assistant that answers from them." | "This repository contains the code for our RAG course." |
| Before / After names the reader's concrete state on each side.                            | "**Before:** grep 500 notes by hand. **After:** ask, get a cited answer in 3 s."              | "**Before:** inefficient. **After:** streamlined."      |
| Needs lists runtime, keys, cost and hardware — everything a reader checks before cloning. | "**Needs:** Python 3.12 · one free Gemini key · $0 · no GPU"                                  | "**Needs:** see the setup guide"                        |
| Every sentence carries a checkable fact: a number, a name, a command.                     | "Runs on a laptop for $0 with a free Gemini key."                                             | "A powerful, production-ready pipeline."                |
| Show first: a diagram, code block or table replaces a paragraph.                          | A 6-node diagram of ingest → index → agent                                                    | Three paragraphs describing the data flow               |
| A How It Works bullet names the component, its tool and its job.                          | "**Vector search** — MongoDB Atlas; retrieves the top-5 chunks per query"                     | "Uses a modern, scalable database."                     |
| The Needs line shows the cheapest path's cost; the full table lives in `01_setup.md`.     | "**Needs:** … · from $0 ([cost by path](guides/01_setup.md#cost))"                            | A 4-row cost table in the README                        |
| An example is a result someone wanted.                                                    | "`/demo-snake` builds a playable Snake game in one prompt" + screenshot                       | "Supports many use cases."                              |
| A Guides row says when to open it.                                                        | "`02_running.md` — you want to run the evals or the Docker stack"                             | "`02_running.md` — Running guide"                       |
| The nav bar links this page's anchors, in section order.                                  | "[Quickstart](#quickstart) · [Guides](#guides) · [Go Deeper](#go-deeper)"                     | A nav bar to the org's homepage and Twitter             |
| A library's example runs as pasted and shows the output it prints.                        | 8-line FastMCP server with `@mcp.tool def add(a, b)`, then "`mcp.run()` serves it on stdio"   | A signature-only snippet with `...` in the body         |
| The agent-setup prompt sends the agent to `guides/` and names the end state.              | "Read guides/ in order and set this repo up until `make test` passes."                        | "Use AI to install this."                               |
| Link the runbook for anything past the quickstart.                                        | "Full setup: [guides/01_setup.md](guides/01_setup.md)"                                        | Docker and cloud install steps inline                   |

## Step 5 — Verify

- `wc -l README.md` ≤ 250, sections in table order, License last.
- `ls guides/` matches the Guides table both ways: every file has a row, every row a file.
- Every relative link, image path and `#anchor` (nav bar included) in `README.md` and `guides/` resolves.
- Every command in the docs traces to the file found in Step 1. Run the quickstart in a fresh
  clone when it needs no secrets.
- `grep -nE '\{\{|TODO' README.md guides/*.md` returns nothing — every template placeholder is filled.

## Step 6 — Hand-off

Report the README line count, the guides written, the sections omitted and why, and any command
you could not run.
