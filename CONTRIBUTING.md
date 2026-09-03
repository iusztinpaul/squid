# Contributing to Squid

Thanks for considering a contribution. Squid stays small and opinionated on purpose — the contract layer is markdown only — so most contributions land as a single `.md` edit and ship the next time someone runs `/plugin update`.

## What we're looking for

- **New `/squid-scaffold` specs** — Rust, Java, mobile (Swift/Kotlin), additional Python/TS frameworks. Highest leverage.
- **Stub fill-ins** — many specs under `skills/squid-scaffold/specs/` are still placeholders. Fleshing one out is a great first PR.
- **Agent prompt improvements** — sharpening PA, SWE, Tester, PR Reviewer, or On-Call so they fail less often.
- **Bug reports** with a concrete repro (which skill, what input, what went wrong).
- **Doc clarifications** in `README.md`, `CLAUDE.md`, or this file.

## What we're NOT looking for

- File templates, Jinja, render steps. Squid intentionally has none — specs replaced templates two pivots ago and we're not going back.
- Language-specific build tooling *for the plugin itself* (no `pyproject.toml`, no `Makefile`, no test suite at the repo root). The contract layer stays pure markdown.
- Large architectural changes without prior discussion — open an issue first.

## Quick start

1. Fork and clone the repo.
2. Load your working tree into Claude Code:
   ```
   claude --plugin-dir /path/to/your/fork
   ```
   This is the only path that exercises uncommitted changes.
3. Validate the frontmatter:
   ```
   python3 scripts/check-frontmatter.py
   ```
4. Run the affected skill against a scratch directory (see [Testing your change](#testing-your-change)).
5. Open a PR.

## What to edit

| Change | File(s) |
|---|---|
| Agent behavior | `agents/<name>.md` |
| Skill (top-level) | `skills/<name>/SKILL.md` |
| New `/squid-scaffold` spec | `skills/squid-scaffold/specs/<name>.md` + add rows to the index in `skills/squid-scaffold/specs/README.md` and the **spec-selection** table (Step 2 of the flow) in `skills/squid-scaffold/SKILL.md` |
| Agent-team lifecycle | `skills/squid-scaffold/AGENTS_TEMPLATE.md` (pipeline map + cross-cutting rules) + the agent contracts |

See [`CLAUDE.md`](CLAUDE.md) for full editing conventions, spec-writing style, and publishing flow.

## Testing your change

There is no automated test suite. Testing means running the affected skill against a real scratch target — see [`CLAUDE.md`](CLAUDE.md) → "Testing the plugin" for the per-skill checks and validation commands (`scripts/check-frontmatter.py` is the guard; `claude plugin validate` alone misses broken frontmatter).

## Submitting

- **Small fixes** (typos, doc clarifications, one-spec edits): open a PR directly.
- **Larger changes** (new agent, lifecycle changes, new pipeline, multi-spec refactor): open an issue first to align on scope.
- **One concern per PR.** Don't bundle a new spec with an agent rewrite — splitting them makes review tractable and reverts surgical.
- Don't bump the `version` in `.claude-plugin/plugin.json` in your PR — maintainers handle versioning at release time.

## Reporting bugs

Open an issue with:

- Which command or skill you ran (e.g. `/squid-implement-night`, `/squid-scaffold`, `software-engineer` agent).
- The exact input you gave.
- What happened vs. what you expected.
- Claude Code version (`claude --version`).
- Squid plugin version (visible in `/plugin list`).

## Releasing (maintainers)

The single source of truth for the plugin version is `.claude-plugin/plugin.json`. Git tags `vX.Y.Z` must agree with it; CI (`.github/workflows/release-check.yml`) blocks any tag push where they disagree.

Use the release script:

```
scripts/release.sh patch          # 0.2.5 -> 0.2.6
scripts/release.sh minor          # 0.2.5 -> 0.3.0
scripts/release.sh major          # 0.2.5 -> 1.0.0
scripts/release.sh 0.3.0          # explicit version
scripts/release.sh patch --dry-run
scripts/release.sh patch --yes    # skip the push confirmation
```

After release, smoke-test from a fresh Claude Code session:

```
/plugin marketplace update iusztinpaul
/plugin update squid@iusztinpaul
```

**Manual fallback.** If the script can't run, the equivalent steps are: bump `version` in `.claude-plugin/plugin.json` by hand → `git commit -m "chore: release v0.X.Y"` → `git tag -a v0.X.Y -m "v0.X.Y"` → `git push origin main` → `git push origin v0.X.Y`. CI still verifies the tag matches `plugin.json`.

**How git tags work.** Tags are local until you push them — plain `git push` does not send tags; you need `git push origin vX.Y.Z` (or `--tags`). The shields.io version badge on `README.md` queries GitHub's API for the highest-versioned *pushed* tag on the public repo, so it can lag your local state by exactly one push.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0 — see [`LICENSE`](LICENSE).
