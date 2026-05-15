---
'myviolet': patch
---

- **Loosened `yarl` pin from `>=1.23.0,<2` to `>=1.17,<2`** for older Home Assistant Core compatibility (PR #8). Pairs with the same-cycle aiohttp loosen shipped in 0.1.1.
- **Synced README `## Requirements` section** with the actual `pyproject.toml` pins. v0.1.1's README still claimed `aiohttp>=3.13.5` and `yarl>=1.23.0`; updated to `aiohttp>=3.10,<4` / `yarl>=1.17,<2` and reworded the rationale (PR #7).
- **Adopt the changesets release flow** ([github-actions-updater](https://github.com/ylabonte/github-actions-updater)-style). Future releases are driven by a `Version Packages` PR auto-opened by `changesets/action`; merge that PR to ship. See `.changeset/README.md` for the contributor side. `python-publish.yml` is unchanged and still publishes to PyPI on GitHub release.
- **Added scheduled GitHub Actions auto-update workflow** (`update-github-actions.yml`) using `ylabonte/github-actions-updater@v1`. Runs Mondays 08:00 UTC and on workflow_dispatch; opens a PR with the proposed `uses:` ref bumps.
