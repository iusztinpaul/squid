#!/usr/bin/env bash
# Release the squid plugin: bump .claude-plugin/plugin.json, commit, tag, push.
# Usage and the manual fallback: CONTRIBUTING.md -> "Releasing (maintainers)".

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: scripts/release.sh <patch|minor|major|X.Y.Z> [--dry-run] [--yes]" >&2
  exit 2
fi

BUMP="$1"
shift

DRY_RUN=0
ASSUME_YES=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --yes|-y)  ASSUME_YES=1 ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$REPO_ROOT" ]]; then
  echo "error: not inside a git repository" >&2
  exit 1
fi
cd "$REPO_ROOT"

MANIFEST=".claude-plugin/plugin.json"
if [[ ! -f "$MANIFEST" ]]; then
  echo "error: $MANIFEST not found (run from the squid repo)" >&2
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT_BRANCH" != "main" ]]; then
  echo "error: must be on 'main' branch (currently on '$CURRENT_BRANCH')" >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "error: working tree has uncommitted changes; commit or stash first" >&2
  exit 1
fi

echo "fetching origin/main..."
git fetch --quiet origin main

LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git rev-parse origin/main)"
if [[ "$LOCAL_SHA" != "$REMOTE_SHA" ]]; then
  echo "error: local main is not in sync with origin/main" >&2
  echo "  local:  $LOCAL_SHA" >&2
  echo "  origin: $REMOTE_SHA" >&2
  exit 1
fi

CURRENT_VERSION="$(python3 -c "import json; print(json.load(open('$MANIFEST'))['version'])")"

if [[ ! "$CURRENT_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "error: current version in $MANIFEST is not valid semver: '$CURRENT_VERSION'" >&2
  exit 1
fi

IFS='.' read -r MAJ MIN PAT <<< "$CURRENT_VERSION"
case "$BUMP" in
  patch) NEW_VERSION="${MAJ}.${MIN}.$((PAT + 1))" ;;
  minor) NEW_VERSION="${MAJ}.$((MIN + 1)).0" ;;
  major) NEW_VERSION="$((MAJ + 1)).0.0" ;;
  *)
    if [[ "$BUMP" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      NEW_VERSION="$BUMP"
    else
      echo "error: bump must be 'patch', 'minor', 'major', or X.Y.Z (got '$BUMP')" >&2
      exit 2
    fi
    ;;
esac

NEW_TAG="v${NEW_VERSION}"

if git rev-parse --verify --quiet "refs/tags/${NEW_TAG}" >/dev/null; then
  echo "error: tag ${NEW_TAG} already exists locally" >&2
  exit 1
fi

if git ls-remote --tags origin "refs/tags/${NEW_TAG}" | grep -q "${NEW_TAG}"; then
  echo "error: tag ${NEW_TAG} already exists on origin" >&2
  exit 1
fi

echo
echo "  current version: $CURRENT_VERSION"
echo "  new version:     $NEW_VERSION"
echo "  new tag:         $NEW_TAG"
echo

if [[ $DRY_RUN -eq 1 ]]; then
  echo "(dry run — no changes made)"
  exit 0
fi

# json round-trip, not sed: preserves key order without a jq dependency.

python3 - "$MANIFEST" "$NEW_VERSION" <<'PYEOF'
import json, sys
path, new_version = sys.argv[1], sys.argv[2]
with open(path) as f:
    data = json.load(f)
data["version"] = new_version
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PYEOF

git add "$MANIFEST"
git commit -m "chore: release ${NEW_TAG}"
git tag -a "$NEW_TAG" -m "$NEW_TAG"

echo
echo "ready to push:"
echo "  git push origin main"
echo "  git push origin ${NEW_TAG}"
echo

if [[ $ASSUME_YES -ne 1 ]]; then
  read -r -p "push now? [y/N] " ANSWER
  case "$ANSWER" in
    y|Y|yes|YES) ;;
    *)
      echo
      echo "push skipped. local state has commit + tag for ${NEW_TAG}."
      echo "to push later:  git push origin main && git push origin ${NEW_TAG}"
      echo "to undo:        git tag -d ${NEW_TAG} && git reset --hard HEAD~1"
      exit 0
      ;;
  esac
fi

git push origin main
git push origin "$NEW_TAG"

echo
echo "released ${NEW_TAG}"
echo "verify: https://github.com/iusztinpaul/squid/releases/tag/${NEW_TAG}"
