---
name: squid-write-navigation-docs
disable-model-invocation: true
argument-hint: "[repo-path] (default: current repo)"
description: >-
  Write an open-source repo's navigation docs — a short landing-page README for people, guides/
  runbooks for agents (full setup, every run scenario), and the GitHub About box (description,
  topics, homepage).
---

# Write navigation docs

You write two kinds of doc, each for one reader, then set the repo's GitHub About box:

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
holds credentials or sends telemetry (decides the `## Security` section in Step 3).

## Step 2 — Ask for what the repo cannot tell you

`AskUserQuestion` rounds of up to 4 questions, only for the gaps. Give every question at least two
real options — the tool rejects a one-option question. Good: "Article: local path / published
URL"; bad: a lone "none yet" option.

1. **The author's article** — the path or URL the README's prose, numbers and example come from,
   and its published URL (for Learn more and the About homepage). Take the problem, the numbers
   and the phrasing from it — good: "You can't review a 23,546-line PR from a coding agent." (the
   article's line); bad: your own paraphrase of it. **No article?** Ask for the problem and the
   solution instead; README rows that say "the article" then use those answers and the order the
   system runs in, and Step 6 sets no homepage.
2. **Audience and the one example** to feature, when the article does not settle them.
3. **The sponsor**, if any: name, tracked short link, UTM query for docs links, logo (light +
   dark), banner, CTA text (or "take it from the article's footer"). Good: `inngest.link/dai-gh`,
   given by the user for this repo; bad: `inngest.link/dai-nl`, found in the article draft.
4. **The header logo** — the repo's own, or none. A sponsor's logo never fills this slot.
5. **Video links** and the Decoding AI reader count for the CTA — confirm it every run. Good:
   "45k+", as the user states today; bad: the count from the last run.

**Assets:** in the same rounds, ask for a source link (URL or local path) for every image the
README needs that the inventory lacks. Download each into `assets/` under the name below, and copy
in any inventory image that lives elsewhere (`static/`, `docs/`); the README loads images only from
`assets/`. An asset with no link drops its block (the diagram falls back to Mermaid).

| Asset                 | Saved as                                                                                       |
| --------------------- | ---------------------------------------------------------------------------------------------- |
| Logo                  | `assets/logo-light.png`, `assets/logo-dark.png`                                                |
| Architecture          | `assets/architecture.png`; an in-depth second one as `assets/architecture-{{what}}.png`        |
| Decoding AI banner    | `assets/decodingai-banner.jpg` — copy it from this skill's `assets/`; never ask for it ¹       |
| Example result        | `assets/example-{{name}}-{{what}}.png` (or `.gif`), one per result image in the article        |
| Sponsor logo + banner | `assets/sponsors/{{sponsor}}-light.svg`, `-dark.svg`, `assets/sponsors/{{sponsor}}-banner.png` |

¹ If this skill's dir can't be found:
`gh api -H 'Accept: application/vnd.github.raw' repos/decodingai-magazine/building-a-coding-agent-from-scratch-course/contents/assets/decodingai.jpg > assets/decodingai-banner.jpg`.

Keep the source's extension (`.svg`, `.jpg`) when it is not PNG. Good: `curl -fL <url> -o
assets/architecture.png`, referenced as `assets/architecture.png`; bad: hot-linking
`https://github.com/user-attachments/...` in the README.

Every link and name comes from the repo or the user — good: "sponsor logo
`assets/sponsors/qdrant-light.svg`, given by the user"; bad: "a guessed `youtube.com/@{{repo}}`
link".

**Existing README?** Every section gets a destination. Print a move map
(`existing section → README #N | guides/<file> | cut: <reason>`) and wait for approval before
writing anything. Good: "`## Installation` → guides/01_setup.md"; bad: "move the technical stuff
to guides".

Done when every Step 4 section has content or an omission reason from the omission rule, every
asset is in `assets/` or its block is marked dropped, and the move map (if any) is approved.

## Step 3 — Write the runbooks

Four files under `guides/`, numbered in reading order (`00_` is the lookup, read on failure). Add a
file only when the user asks for a split — good: deploy steps as a `## Deploy` in `02_running.md`;
bad: a `04_deploy.md` holding one command.

| File                    | Holds                                                                                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `01_setup.md`           | Prerequisites, install, env vars, external services; a `## Cost` table when cost differs by run path                                                    |
| `02_running.md`         | Every run scenario (local, Docker, cloud, tests, evals), one `##` per scenario                                                                          |
| `03_how_it_works.md`    | Architecture, the files a run writes, API, project structure; a `## Security` section (what runs where, what leaves the machine) per Step 1's condition |
| `00_troubleshooting.md` | Each known failure as error text → cause → fix, then an `## FAQ`. Only when either has content                                                          |

Runbook rules:

| Rule                                                                                                                                                                          | Good                                                                                     | Bad                                               |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------- |
| The first line under the title states the end state.                                                                                                                          | "After this guide `make test` passes on a fresh clone."                                  | "Welcome! Let's get you set up."                  |
| Every command sits in a fenced block, runnable from the repo root.                                                                                                            | `uv sync && cp .env.example .env`                                                        | "Install the dependencies and configure env."     |
| A command that can fail is followed by its expected output, copied from a run or the repo's code; otherwise it goes in the hand-off as unverified.                            | "Prints `Uvicorn running on http://127.0.0.1:8000`."                                     | "The server should now be working."               |
| Every env var is named, with its source and whether it is required.                                                                                                           | "`OPENAI_API_KEY` — required; platform.openai.com/api-keys"                              | "Add your API keys."                              |
| `01_setup.md`: prerequisites form one table `Tool \| Min version \| Purpose \| Install`.                                                                                      | "`uv \| ≥0.5 \| Python env + deps \| [install](https://docs.astral.sh/uv/)`"             | "Make sure you have Python and Docker installed." |
| `01_setup.md`: one `###` per external service — sign-up link, env var it fills, free tier or paid.                                                                            | "`### Qdrant` — free cloud tier; fills `QDRANT_URL`, `QDRANT_API_KEY`"                   | "Create accounts on the services we use."         |
| `02_running.md`: scenarios follow the order the system runs in, each naming its prerequisite scenario.                                                                        | "`## Train` — needs `## Generate dataset` to have run"                                   | Scenarios in alphabetical order                   |
| `02_running.md`: each scenario names its code entry point — the first file to open when it breaks.                                                                            | "Entry point: `pipelines/feature_engineering.py`"                                        | "The logic is spread across the codebase."        |
| The sponsor's first prose mention in each file links the tracked short link.                                                                                                  | "[Inngest](https://inngest.link/dai-gh) checkpoints every step"                          | A plain `inngest.com` link                        |
| Where a guide explains the sponsor's product (sign-up, pricing, keys, each concept the repo uses), link its human docs page from the vendor's `llms.txt`, with the UTM query. | `https://www.inngest.com/docs/local-development?utm_medium=repo&...`                     | A `/docs-markdown/...` page, or no UTM query      |
| A GitHub alert marks only a step that breaks something if skipped: marker on its own line, one sentence.                                                                      | `> [!WARNING]` / `> Run make infra-up first — every pipeline needs MongoDB.` (two lines) | A `> [!NOTE]` on every other paragraph            |
| The last line links the next guide by number; `03_how_it_works.md` and `00_troubleshooting.md` link `../README.md#guides`.                                                    | "Next: [02_running.md](02_running.md)"                                                   | A guide that dead-ends.                           |

Done when every command and env var in the Step 1 inventory appears in exactly one runbook, and
every runbook rule holds in every file.

## Step 4 — Write the landing page

Sections in this order; headings as written, in sentence case — capitalise only the first word and
words capitalised in prose (`## Who is this for`, not `## Who Is This For`). The CTA heading (#4,
#12) is the one exception. Budgets are caps; the whole file is capped at **250 lines**.

| #   | Section                            | Holds                                                                                                                                                    | Budget                                                                                     |
| --- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1   | Header                             | Repo logo (if any), title, tagline, nav bar, sponsor line, badges                                                                                        | Tagline ≤ 15 words, 1 nav line, ≤ 4 badges                                                 |
| 2   | No heading, right after #1         | The reader's problem → what the repo does, naming its inspiration → why to trust it; a library adds a runnable example                                   | 2–3 paragraphs of 1–2 sentences + ≤ 15-line code block                                     |
| 3   | `## How it works`                  | Architecture diagram + component bullets in the order the article builds the system; an in-depth diagram after them                                      | ≤ 2 diagrams joined by 1 sentence, ≤ 5 bullets                                             |
| 4   | `## 📬 Learn {{Topic}}`            | Decoding AI CTA                                                                                                                                          | The block                                                                                  |
| 5   | `## Quickstart`                    | **Needs** line, clone → install → run on the cheapest path, the result you should see, agent-setup prompts                                               | 1 line + 1 code block ≤ 6 commands + 1 line + the prompt blocks                            |
| 6   | `## Guides`                        | Index table `Guide \| Read it when`, one row per `guides/` file; the `03_how_it_works.md` row names Security                                             | 1 row per guide                                                                            |
| 7   | `## Who is this for`               | Table `Audience \| What you get`; no audience that exists only because of the sponsor's product                                                          | ≤ 2 rows                                                                                   |
| 8   | `## See it in action`              | One example, told as the article tells it: setup → command → results, then how the shown run differs from the shipped config, then the agent-run prompts | 1 setup sentence + 1 command + 2–5 visuals of 1 sentence each + 1 line + the prompt blocks |
| 9   | `## Learn more`                    | Table `# \| Article \| Video`; each cell a linked title or `—`, text only                                                                                | 1 row per piece                                                                            |
| 10  | `## Sponsors`                      | The sponsor's CTA, from the user or the article's footer                                                                                                 | The block                                                                                  |
| 11  | `## Questions and troubleshooting` | Link to GitHub issues, `00_troubleshooting.md` when it exists, `CONTRIBUTING.md` when it exists                                                          | ≤ 2 sentences                                                                              |
| 12  | `## 📬 Learn {{Topic}}`            | The #4 CTA block again, same heading                                                                                                                     | The block                                                                                  |
| 13  | `## Star history`                  | Star-history chart                                                                                                                                       | The block                                                                                  |
| 14  | `## License`                       | License name linked to `LICENSE`                                                                                                                         | 1 line                                                                                     |

**Omission rule:** omit #8 when no example exists, #10 without a sponsor, and #9 until a published
article or video URL exists — when one turns up later, add #9 and its nav link. Everything else
(security included) lives in a runbook.

**Read [`TEMPLATE.md`](TEMPLATE.md) before writing any README section** — it holds the
landing-page rules, the diagram fallback, the exact HTML for #1, #4, #5, #8, #10, #12 and #13, and the
CTA URLs.

Done when every row above is written or omitted per the omission rule.

## Step 5 — Verify

- `wc -l README.md` ≤ 250, sections in table order.
- `ls guides/` matches the Guides table both ways: every file has a row, every row a file.
- Every image path points into `assets/`, and every relative link, image path and `#anchor` (nav
  bar included) in `README.md` and `guides/` resolves.
- Every sponsor URL in `README.md` and `guides/` is the tracked short link or carries the UTM
  query (image badge sources and `localhost` excepted), and every sponsor docs link returns
  HTTP 200 (`curl -so /dev/null -w '%{http_code}' -L <url>`).
- Every command in the docs traces to the Step 1 inventory. Run the quickstart in a fresh clone
  when it needs no secrets.
- `grep -nE '\{\{[A-Za-z][A-Za-z -]*(:|\}\})|TODO' README.md guides/*.md` returns nothing — every
  template placeholder is filled.

Fix every failure and re-run the whole list; done when all checks pass in one run.

## Step 6 — Set the GitHub About

The About box is what search results and link previews show.

- **Description:** ≤ 20 words — what it is, then what makes it different. Good: "Durable and
  secure eval-driven code search agents powered by Inngest. Bring a data scientist's mindset to
  coding agents."; bad: "🚀 The ultimate next-gen AI framework!"
- **Topics:** exactly 5. Collect candidates from the ranked repos on `https://trendshift.io/monthly`
  (server-rendered; skip the sponsor blocks) that fit this project, reading
  each one's topics with `gh api repos/<owner>/<repo> --jq .topics`; add project-specific ones
  (the sponsor, the core technique); keep the 5 most relevant. Good: `ai-agents`, `coding-agent`,
  `evals`, `inngest`, `long-running-agents`; bad: `ai`, `llm`, `typescript`, `docker`, `awesome`.
- **Homepage:** the article's published URL — good:
  `https://www.decodingai.com/p/build-durable-secure-long-running-agents`; bad: the repo's own
  GitHub URL. No article, no homepage.

It edits public state: print the command, run it only after approval, then verify.

```bash
gh repo edit {{owner}}/{{repo}} --description "{{description}}" --homepage {{article-url}} \
  --add-topic {{topic}} --remove-topic {{old-topic}}
gh repo view {{owner}}/{{repo}} --json description,repositoryTopics,homepageUrl
```

Done when `gh repo view` shows the approved description, 5 topics and homepage — or the user
declined and the hand-off reports the unapplied command.

## Step 7 — Hand-off

Report the README line count, the guides written, the sections omitted and why, the About
description, topics and homepage (and whether `gh repo edit` ran), and every command you could not
run or whose expected output is unverified. Then offer to push the docs to the default branch so
the user reviews them rendered on GitHub, and push each later round of edits as one docs-only
commit — good: `docs: move security into guides/03_how_it_works.md`; bad: one squashed commit of
ten rounds.
