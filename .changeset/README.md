# Changesets

This folder is managed by [changesets](https://github.com/changesets/changesets). It tracks the
"what changed since last release" log for `myviolet` and drives the release flow.

## Adding a changeset for your PR

Before merging anything user-visible (dep changes, API changes, bugfixes, docs that affect
consumers), drop a changeset file in this folder:

```bash
npx --yes @changesets/cli@^2 add
```

(Or write the file by hand — it's a tiny markdown file. See existing ones for the format.)

Pick the bump type — **major / minor / patch** — and write a short narrative description. Commit
the resulting `.changeset/<random-slug>.md` alongside your code change.

## What happens on merge

When your PR merges into `main`, the `Release` workflow notices the new changeset and opens a
`chore(release): version packages` PR that:

- Bumps `package.json` `version` according to the highest pending bump type.
- Prepends a `## <version>` section to `CHANGELOG.md` containing all the changeset narratives.
- Deletes the consumed `.changeset/*.md` files.

When **that** PR is merged, the workflow runs again, tags the release, and creates a GitHub
Release. The existing `python-publish.yml` workflow triggers off the release event and uploads
the wheel to PyPI via Trusted Publishing.

## Why a thin `package.json` exists in a Python repo

Changesets is a Node tool that reads `package.json` `version`. We use it purely as a release-flow
driver, not as a JS package manifest. `pyproject.toml` declares the Python package's runtime
metadata, and `hatch-vcs` reads the git tag (which the release workflow creates from
`package.json`'s version) to stamp the wheel. The two stay in sync because the release flow
controls both.
