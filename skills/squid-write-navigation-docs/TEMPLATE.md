# Landing-page rules and blocks

Section numbers refer to the Step 4 table in [`SKILL.md`](SKILL.md).

## Rules

| Rule                                                                                                                                                                                                               | Good                                                                                                        | Bad                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| The tagline is `<category>: <transformation>`, sentence case after the colon, grammar checked (hyphenate compound modifiers). Report a grammar issue in a user-given tagline and offer the fix before applying it. | "Eval-driven code search: bring a data-scientist mindset to coding agents"                                  | "Let a coding agent climb your eval scores overnight, with caps it can't override" |
| #2 opens on the reader's problem, in the article's words and numbers.                                                                                                                                              | "You can't review a 23,546-line PR from a coding agent."                                                    | "This repository contains the code for our RAG course."                            |
| #2's last paragraph says why it can be trusted.                                                                                                                                                                    | "Guardrails live in code, not in the prompt."                                                               | "**Before:** inefficient. **After:** streamlined."                                 |
| Every sentence carries a checkable fact: a number, a name, a command.                                                                                                                                              | "Runs on a laptop for $0 with a free Gemini key."                                                           | "A powerful, production-ready pipeline."                                           |
| Show first: a diagram, code block or table replaces a paragraph.                                                                                                                                                   | A 6-node diagram of ingest → index → agent                                                                  | Three paragraphs describing the data flow                                          |
| A library's example runs as pasted and shows the output it prints.                                                                                                                                                 | 8-line FastMCP server with `@mcp.tool def add(a, b)`, then "`mcp.run()` serves it on stdio"                 | A signature-only snippet with `...` in the body                                    |
| A How it works bullet names the component, its tool and its job.                                                                                                                                                   | "**Metering proxy** — holds the real credentials, allows only the config's models"                          | "Uses a modern, scalable database."                                                |
| Needs lists runtime, keys, the cheapest path's cost (linked to `01_setup.md#cost`) and hardware.                                                                                                                   | "**Needs:** Python 3.12 · one free Gemini key · from $0 ([cost by path](guides/01_setup.md#cost)) · no GPU" | "**Needs:** see the setup guide"                                                   |
| Link the runbook for anything past the quickstart.                                                                                                                                                                 | "Full setup: [guides/01_setup.md](guides/01_setup.md)"                                                      | Docker and cloud install steps inline                                              |
| A Guides row says when to open it.                                                                                                                                                                                 | "`02_running.md` \| you want to run the evals or the Docker stack"                                          | "`02_running.md` \| Running guide"                                                 |
| Each #8 visual gets one sentence carrying the article's numbers.                                                                                                                                                   | "Node extraction F1 climbed to 0.764 on dev and scored 0.738 on test:"                                      | "Here are the results:"                                                            |
| Every sponsor link, text or image, is the tracked short link; the first prose mention of the sponsor on each line links it.                                                                                        | "[Inngest](https://inngest.link/dai-gh) checkpoints every step"                                             | An untracked `inngest.com` link, or an unlinked mention                            |
| The nav bar links this page's anchors, in section order.                                                                                                                                                           | "[Quickstart](#quickstart) · [Guides](#guides) · [Learn more](#learn-more)"                                 | A nav bar to the org's homepage and Twitter                                        |

## Diagrams (#3)

Use `assets/architecture.png` (from the repo or Step 2). Otherwise write a Mermaid `flowchart LR` of ≤ 8
nodes, each node a component a reader can find in the tree — good: 6 nodes, ingest → index →
agent; bad: a 15-node diagram of every module. When the article shows a progression (simple, then
in depth), add the in-depth image after the bullets, introduced by one sentence.

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
  <p><a href="#quickstart">Quickstart</a> · <a href="#guides">Guides</a> · <a href="#see-it-in-action">See it in action</a> · <a href="#learn-more">Learn more</a> · <a href="#questions-and-troubleshooting">Questions</a></p>
  <h3>Sponsored by&nbsp;
    <a href="{{sponsor-tracked-url}}"><picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/sponsors/{{sponsor}}-dark.svg">
      <img src="assets/sponsors/{{sponsor}}-light.svg" alt="{{Sponsor}}" height="16">
    </picture></a>
  </h3>
</div>

<p align="center">
  <a href="https://github.com/{{owner}}/{{repo}}/actions"><img src="https://img.shields.io/github/actions/workflow/status/{{owner}}/{{repo}}/{{workflow-file}}?branch={{default-branch}}&label=ci" alt="CI"></a>
  <a href="https://pypi.org/project/{{package}}"><img src="https://img.shields.io/pypi/v/{{package}}" alt="PyPI version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/{{owner}}/{{repo}}" alt="License"></a>
  <img src="https://img.shields.io/badge/{{label}}-{{value}}-{{color}}" alt="{{label}}: {{value}}">
</p>
```

- Drop the `<picture>` when the repo has no logo of its own; with one logo, use it for both
  sources. A sponsor's logo never goes there.
- Drop the `Sponsored by` `<h3>` without a sponsor. Its logo stays ~16 px tall, matching the text
  and smaller than the title.
- Drop a nav link whose section is omitted.
- Prefer live badges (CI, version, license) — they update themselves. On a JS package swap the
  PyPI badge for `npmjs.com/package/{{package}}` + `npm/v/{{package}}`; drop it for a repo that
  publishes nothing.
- A static badge states a fact a reader checks before cloning — good: `node-≥20-blue`,
  `durability-Inngest-black` linked to the sponsor's tracked URL; bad: `mock_night-$0-green`,
  `made_with-love-red`. Write a literal `-` in text as `--`.

### CTA (#4, repeated at #12)

The heading is `## 📬 Learn {{Topic}}`, in title case — good: `## 📬 Learn to Build Long-Running
Agents`; bad: `## Stay updated`. Copy `assets/decodingai-banner.jpg` from this skill's `assets/`.

```markdown
> Join {{reader count: e.g. 45k+, confirmed in Step 2}} engineers reading [the Decoding AI Magazine](https://www.decodingai.com/) and watching [the Decoding AI YouTube channel](https://www.youtube.com/@itsdecodingai) to learn to {{topic lesson: e.g. build durable, secure long-running agents}}.

<a href="https://www.decodingai.com/" target="_blank">
  <img src="assets/decodingai-banner.jpg" alt="Decoding AI Magazine" width="100%"/>
</a>
```

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

### Agent-run prompt (#8)

Last block of See it in action: the featured example as one copyable prompt.

````markdown
**Run it with your coding agent:**

```txt
In https://github.com/{{owner}}/{{repo}} (set up per guides/01_setup.md if it isn't yet), follow
guides/02_running.md#{{scenario-anchor}} to run {{example: e.g. the GraphRAG night}} with
{{command}}, until {{end state: e.g. done.json is written}}. Use 00_troubleshooting.md on any
error and ask me for any API key or budget it needs.
```
````

### Sponsors (#10)

Take the lines from the sponsor's CTA text or the article's footer, with "the series" changed to
"this project".

```html
<p align="center"><i>Thanks again to <a href="{{sponsor-tracked-url}}"><b>{{Sponsor}}</b></a> for sponsoring this project and keeping it free!</i></p>

<p align="center">
  <a href="{{sponsor-tracked-url}}"><img src="assets/sponsors/{{sponsor}}-banner.png" alt="{{Sponsor}} x Decoding AI" width="80%"></a>
</p>

<p align="center"><a href="{{sponsor-tracked-url}}">Try {{Sponsor}} for free here</a> ({{free-plan line: e.g. free plan with 50k executions/month}})</p>

<h3 align="center">{{pitch line: e.g. Build AI agents and workflows that survive crashes, retries, and long waits:}}</h3>

<p align="center">
  <a href="{{sponsor-tracked-url}}"><img src="https://img.shields.io/badge/Start_building_for_free-c0392b?style=for-the-badge" alt="Start building for free" height="40"></a>
</p>
```

### Star history (#13)

```html
<a href="https://www.star-history.com/?type=date&repos={{owner}}%2F{{repo}}">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos={{owner}}/{{repo}}&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos={{owner}}/{{repo}}&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos={{owner}}/{{repo}}&type=date&legend=top-left" />
 </picture>
</a>
```

<!-- Blocks adapted from decodingai-magazine/building-a-coding-agent-from-scratch-course,
second-brain-ai-assistant-course and codeclimb. -->
