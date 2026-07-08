#!/usr/bin/env python3
"""Validate the YAML frontmatter of every agent and skill in this plugin.

Why this exists: `claude plugin validate .` from the repo root only reads
`.claude-plugin/marketplace.json`. It never opens `agents/` or `skills/`, so a
skill whose frontmatter fails to parse sails straight through — and Claude Code
then loads that skill with *every frontmatter field silently dropped* (no name,
no description, no disable-model-invocation). That is exactly how four skills
shipped broken. Even when pointed at a marketplace-free copy, `claude plugin
validate` checks field *types* but never *values*: `model: not-a-real-model`
and `effort: banana` both pass.

Usage:  python3 scripts/check-frontmatter.py
Exit:   0 = clean, 1 = at least one error
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    sys.exit("error: PyYAML is required.  pip install pyyaml")

# Accepted `model:` aliases per Claude Code's sub-agent docs. Anything else must
# look like a full model ID (e.g. claude-opus-4-8), which we shape-check only —
# we deliberately do not pin a list of live model IDs here, because it would rot.
MODEL_ALIASES = {"sonnet", "opus", "haiku", "fable", "inherit"}
MODEL_ID_RE = re.compile(r"^claude-[a-z0-9.\-]+$")
EFFORT_LEVELS = {"low", "medium", "high", "xhigh", "max"}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

errors: list[str] = []
warnings: list[str] = []


def err(path: Path, msg: str) -> None:
    errors.append(f"{path}: {msg}")


def warn(path: Path, msg: str) -> None:
    warnings.append(f"{path}: {msg}")


def load(path: Path, rel: Path) -> dict | None:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        err(rel, "no YAML frontmatter (file must start with a '---' block)")
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        hint = ""
        raw = m.group(1)
        if re.search(r"^\w[\w-]*: [^'\"|>].*?: ", raw, re.M):
            hint = (
                "\n    hint: an unquoted YAML scalar cannot contain ': ' — it reads as a "
                "nested key.\n"
                "          Use a folded block scalar:  description: >-\\n  <text>"
            )
        elif re.search(r"^\w[\w-]*: \[.*\]\s*\S", raw, re.M):
            hint = (
                "\n    hint: `key: [a] [b]` opens a YAML flow sequence; the trailing text "
                "after ']' is a parse error.\n"
                "          Quote the whole value:  argument-hint: \"[a] [b]\""
            )
        err(
            rel,
            f"frontmatter failed to parse ({type(e).__name__}). Claude Code will load "
            f"this file with ALL frontmatter fields silently dropped.{hint}",
        )
        return None
    if not isinstance(data, dict):
        err(rel, f"frontmatter is {type(data).__name__}, expected a mapping")
        return None
    return data


def check_common(path: Path, fm: dict, expected_name: str) -> None:
    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        err(path, "missing or empty `name:`")
    elif name != expected_name:
        err(path, f"`name: {name}` does not match its location (expected {expected_name!r})")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        err(path, "missing or empty `description:` — Claude cannot decide when to invoke this")

    hint = fm.get("argument-hint")
    if hint is not None and not isinstance(hint, str):
        err(
            path,
            f"`argument-hint:` parsed as {type(hint).__name__}, not a string — "
            f'it starts with "[". Quote it.',
        )

    model = fm.get("model")
    if model is not None:
        if not isinstance(model, str):
            err(path, f"`model:` must be a string, got {type(model).__name__}")
        elif model not in MODEL_ALIASES and not MODEL_ID_RE.match(model):
            err(
                path,
                f"`model: {model}` is neither an alias ({', '.join(sorted(MODEL_ALIASES))}) "
                f"nor a claude-* model ID",
            )

    effort = fm.get("effort")
    if effort is not None and effort not in EFFORT_LEVELS:
        err(path, f"`effort: {effort}` is not one of {', '.join(sorted(EFFORT_LEVELS))}")


def main() -> int:
    root = Path(__file__).resolve().parent.parent

    agents = sorted(root.glob("agents/*.md"))
    skills = sorted(root.glob("skills/*/SKILL.md"))
    if not agents or not skills:
        sys.exit(f"error: found {len(agents)} agents and {len(skills)} skills under {root} — "
                 "run this from the plugin repo")

    loaded: dict[str, dict] = {}

    for path in agents:
        rel = path.relative_to(root)
        fm = load(path, rel)
        if fm is None:
            continue
        loaded[path.stem] = fm
        check_common(rel, fm, path.stem)
        if not fm.get("tools"):
            warn(rel, "no `tools:` — this agent inherits the full tool set")

    for path in skills:
        rel = path.relative_to(root)
        fm = load(path, rel)
        if fm is None:
            continue
        check_common(rel, fm, path.parent.name)

    # Squid's own model policy (AGENTS.md): Fable plans and reviews; it never writes code.
    swe = loaded.get("software-engineer")
    if swe and swe.get("model") == "fable":
        warn(
            Path("agents/software-engineer.md"),
            "model: fable on the code-writing agent — Fable costs 2x Opus and buys "
            "little for generation. See README 'Which model runs which agent'.",
        )

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}", file=sys.stderr)

    checked = len(agents) + len(skills)
    if errors:
        print(
            f"\n{len(errors)} error(s) across {checked} files "
            f"({len(agents)} agents, {len(skills)} skills)",
            file=sys.stderr,
        )
        return 1
    print(f"ok: {checked} files ({len(agents)} agents, {len(skills)} skills) — frontmatter clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
