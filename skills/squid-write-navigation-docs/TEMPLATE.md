# Landing-page rules and blocks

Section numbers refer to the Step 4 table in [`SKILL.md`](SKILL.md).

## Rules

| Rule                                                                                             | Good                                                                                                        | Bad                                                     |
| ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Open on the reader's problem, then the solution.                                                 | "Notes pile up unread. This turns 500 Notion pages into an assistant that answers from them."               | "This repository contains the code for our RAG course." |
| Before / After names the reader's concrete state on each side.                                   | "**Before:** grep 500 notes by hand. **After:** ask, get a cited answer in 3 s."                            | "**Before:** inefficient. **After:** streamlined."      |
| Every sentence carries a checkable fact: a number, a name, a command.                            | "Runs on a laptop for $0 with a free Gemini key."                                                           | "A powerful, production-ready pipeline."                |
| Show first: a diagram, code block or table replaces a paragraph.                                 | A 6-node diagram of ingest → index → agent                                                                  | Three paragraphs describing the data flow               |
| A library's example runs as pasted and shows the output it prints.                               | 8-line FastMCP server with `@mcp.tool def add(a, b)`, then "`mcp.run()` serves it on stdio"                 | A signature-only snippet with `...` in the body         |
| A How it works bullet names the component, its tool and its job.                                 | "**Vector search** — MongoDB Atlas; retrieves the top-5 chunks per query"                                   | "Uses a modern, scalable database."                     |
| Needs lists runtime, keys, the cheapest path's cost (linked to `01_setup.md#cost`) and hardware. | "**Needs:** Python 3.12 · one free Gemini key · from $0 ([cost by path](guides/01_setup.md#cost)) · no GPU" | "**Needs:** see the setup guide"                        |
| Link the runbook for anything past the quickstart.                                               | "Full setup: [guides/01_setup.md](guides/01_setup.md)"                                                      | Docker and cloud install steps inline                   |
| A Guides row says when to open it.                                                               | "`02_running.md` \| you want to run the evals or the Docker stack"                                          | "`02_running.md` \| Running guide"                      |
| An example is a result someone wanted.                                                           | "`/demo-snake` builds a playable Snake game in one prompt" + screenshot                                     | "Supports many use cases."                              |
| The nav bar links this page's anchors, in section order.                                         | "[Quickstart](#quickstart) · [Guides](#guides) · [Learn more](#learn-more)"                                 | A nav bar to the org's homepage and Twitter             |

## Diagram (#3)

Use `assets/architecture.png` (from the repo or Step 2). Otherwise write a Mermaid `flowchart LR` of ≤ 8
nodes, each node a component a reader can find in the tree — good: 6 nodes, ingest → index →
agent; bad: a 15-node diagram of every module.

````markdown
```mermaid
flowchart LR
  A[{{component}}] --> B[{{component}}] --> C[{{component}}]
```
````

## Blocks

Copy each block, then replace every `{{placeholder}}` with values from the Step 1 inventory or
Step 2 answers.

### Header (#1)

```html
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
    <img src="assets/logo-light.png" alt="{{repo}} logo" width="140">
  </picture>
  <h1>{{title}}</h1>
  <h3>{{tagline}}</h3>
  <p><a href="#quickstart">Quickstart</a> · <a href="#guides">Guides</a> · <a href="#learn-more">Learn more</a> · <a href="#questions-and-troubleshooting">Questions</a></p>
</div>

<p align="center">
  <a href="https://github.com/{{owner}}/{{repo}}/actions"><img src="https://img.shields.io/github/actions/workflow/status/{{owner}}/{{repo}}/{{workflow-file}}?branch={{default-branch}}&label=ci" alt="CI"></a>
  <a href="https://pypi.org/project/{{package}}"><img src="https://img.shields.io/pypi/v/{{package}}" alt="PyPI version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/{{owner}}/{{repo}}" alt="License"></a>
  <img src="https://img.shields.io/badge/{{label}}-{{value}}-{{color}}" alt="{{label}}: {{value}}">
</p>
```

- Drop the `<picture>` when the repo has no logo; with one logo, use it for both sources.
- Drop a nav link whose section is omitted.
- Prefer live badges (CI, version, license) — they update themselves. On a JS package swap the
  PyPI badge for `npmjs.com/package/{{package}}` + `npm/v/{{package}}`; drop it for a repo that
  publishes nothing.
- A static badge states a fact a reader checks before cloning — good: `cost_to_run-$0-green`,
  `articles-8-blue`; bad: `made_with-love-red`. Write a literal `-` in text as `--`.

### CTA (#4, repeated at #13)

The heading names what the reader learns next, in this repo's topic — good: `## Learn harness
engineering`; bad: `## Stay updated`.

```markdown
> {{one sentence: what Decoding AI teaches about this repo's topic}}

<a href="https://www.decodingai.com/">
  <img src="assets/decodingai-banner.png" alt="Decoding AI Magazine" width="100%">
</a>

<p align="center">
  <a href="https://www.decodingai.com/">
    <img src="https://img.shields.io/static/v1?label&logo=substack&message=Read%20on%20Substack&style=for-the-badge&color=black" alt="Decoding AI on Substack" height="40">
  </a>
  &nbsp;
  <a href="https://www.youtube.com/@itsdecodingai">
    <img src="https://img.shields.io/static/v1?label&logo=youtube&message=Watch%20on%20YouTube&style=for-the-badge&color=black" alt="Decoding AI on YouTube" height="40">
  </a>
</p>
```

Drop the banner `<a>` when Step 2 gave no banner link.

### Agent-setup prompt (#5)

Last block of the Quickstart.

````markdown
**Set up with your coding agent:**

```txt
Clone https://github.com/{{owner}}/{{repo}}, follow guides/ from 01_setup.md onward
(00_troubleshooting.md on any error), and set it up until {{end state: e.g. make test passes}}.
Ask me for any API key it needs.
```
````

### Sponsors (#10)

One `<a>` per sponsor, joined by `&nbsp;&nbsp;`.

```html
<p align="center">
  <a href="{{sponsor-url}}"><img src="assets/sponsors/{{sponsor-slug}}.png" alt="{{sponsor}}" height="45"></a>
</p>

<p align="center">Special thanks to {{sponsor links: comma-separated}} for sponsoring this project.</p>
```

### Star history (#14)

```html
<a href="https://www.star-history.com/?type=date&repos={{owner}}%2F{{repo}}">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos={{owner}}/{{repo}}&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos={{owner}}/{{repo}}&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos={{owner}}/{{repo}}&type=date&legend=top-left" />
 </picture>
</a>
```

<!-- Blocks adapted from decodingai-magazine/building-a-coding-agent-from-scratch-course and
second-brain-ai-assistant-course. -->
