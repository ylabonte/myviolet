#!/usr/bin/env bash
#
# Invoked by changesets/action as its `publish:` command. Runs only when there
# are no `.changeset/*.md` files left on `main` — i.e. the "Version Packages"
# PR was just merged.
#
# Job: tag the release and create a GitHub Release. The `python-publish.yml`
# workflow takes it from there and uploads the wheel to PyPI via Trusted
# Publishing.
#
# Idempotency: re-running on the same commit is a no-op once the tag exists.
#
# Output: the "🦋  myviolet@<version>" marker on stdout tells changesets/action
# to set `published=true` in its outputs. Skipping the marker (because the tag
# already exists) leaves `published=false`, which is fine — nothing else in the
# workflow consumes it for now.

set -euo pipefail

version="$(node -p "require('./package.json').version")"
tag="v${version}"

if git rev-parse --verify "refs/tags/${tag}" >/dev/null 2>&1; then
  echo "Tag ${tag} already exists; nothing to release."
  exit 0
fi

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'

# hatch-vcs reads this tag to stamp the version into the wheel METADATA.
git tag "${tag}"
git push origin "${tag}"

# Pull this release's CHANGELOG.md section so it lands in the GitHub Release
# notes. Section runs from "## ${version}" up to (but not including) the
# next "## " heading.
notes="$(awk -v marker="## ${version}" '
  $0 == marker { in_section = 1; next }
  in_section && /^## / { exit }
  in_section { print }
' CHANGELOG.md)"

if [[ -z "${notes//[$' \t\n\r']/}" ]]; then
  notes="See CHANGELOG.md for details."
fi

# `release.published` event from this fires python-publish.yml, which does the
# actual PyPI upload via OIDC.
gh release create "${tag}" \
  --title "${tag}" \
  --notes "${notes}"

# Tell changesets/action this counts as a publish.
echo "🦋  myviolet@${version}"
