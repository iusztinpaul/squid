# README blocks

Copy each block verbatim, then replace every `{{placeholder}}`. `{{owner}}/{{repo}}` comes from
`git remote get-url origin`.

## Header (#1)

```html
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="{{logo-dark-path}}">
    <img src="{{logo-light-path}}" alt="{{repo}} logo" width="140">
  </picture>
  <h1>{{title}}</h1>
  <h3>{{tagline: the transformation in ≤ 15 words}}</h3>
  <p><a href="#quickstart">Quickstart</a> · <a href="#guides">Guides</a> · <a href="#go-deeper">Go Deeper</a> · <a href="#questions-and-troubleshooting">Questions</a></p>
</div>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/{{owner}}/{{repo}}/{{ci-workflow}}.yml?branch=main&label=ci" alt="CI">
  <img src="https://img.shields.io/pypi/v/{{package}}" alt="PyPI version">
  <img src="https://img.shields.io/github/license/{{owner}}/{{repo}}" alt="License">
  <img src="https://img.shields.io/badge/{{label}}-{{value}}-{{color}}" alt="{{label}}: {{value}}">
</p>
```

Drop the `<picture>` when the repo has no logo; with one logo, use it for both sources. Drop a nav
link whose section is omitted. Prefer live badges (CI, version, license) — they update themselves;
swap `pypi/v/` for `npm/v/` on a JS package and drop it for a repo that publishes nothing. A static
badge states a fact a reader checks before cloning: `cost_to_run-$0`, `articles-8`.

## Agent-setup prompt (#5)

Last block of the Quickstart.

````markdown
**Set up with your coding agent:**

```txt
Clone https://github.com/{{owner}}/{{repo}}, read guides/ in order, and set it up
until {{end state, e.g. `make test` passes}}. Ask me for any API key it needs.
```
````

## Sponsors (#10)

```html
<p align="center">
  <a href="{{sponsor-url}}" target="_blank"><img src="{{sponsor-logo-path}}" alt="{{sponsor}}" height="45"></a>
  &nbsp;&nbsp;
  <a href="{{sponsor-url}}" target="_blank"><img src="{{sponsor-logo-path}}" alt="{{sponsor}}" height="45"></a>
</p>

<p align="center">Special thanks to <a href="{{sponsor-url}}"><b>{{sponsor}}</b></a> for sponsoring this project.</p>
```

## CTA (#4, repeated at #13)

The heading names what the reader learns next, in this repo's topic: `## Learn Harness
Engineering`, not `## Stay Updated`.

```markdown
> {{one sentence: what Decoding AI teaches about this repo's topic}}

<p align="center">
  <a href="https://www.decodingai.com/" target="_blank">
    <img src="https://img.shields.io/static/v1?label&logo=substack&message=Read%20on%20Substack&style=for-the-badge&color=black" alt="Decoding AI on Substack" height="40">
  </a>
  &nbsp;
  <a href="https://www.youtube.com/@itsdecodingai" target="_blank">
    <img src="https://img.shields.io/static/v1?label&logo=youtube&message=Watch%20on%20YouTube&style=for-the-badge&color=black" alt="Decoding AI on YouTube" height="40">
  </a>
</p>
```

## Star History (#14)

```html
<a href="https://www.star-history.com/?type=date&repos={{owner}}%2F{{repo}}">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos={{owner}}/{{repo}}&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos={{owner}}/{{repo}}&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos={{owner}}/{{repo}}&type=date&legend=top-left" />
 </picture>
</a>
```

---

Blocks adapted from
[building-a-coding-agent-from-scratch-course](https://github.com/decodingai-magazine/building-a-coding-agent-from-scratch-course)
and [second-brain-ai-assistant-course](https://github.com/decodingai-magazine/second-brain-ai-assistant-course);
prose density modelled on [pi](https://github.com/earendil-works/pi).
