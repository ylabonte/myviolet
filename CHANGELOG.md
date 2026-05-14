# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Development dependencies moved from `[project.optional-dependencies]` to `[dependency-groups]`** (PEP 735). The `dev`, `test`, and `docs` groups were never user-facing extras; they're for working *on* the package, not *with* it. They no longer appear as `Provides-Extra:` on PyPI. Local install: `pip install -e . --group dev --group test --group docs` (requires pip ≥ 25.1). CI workflows (`test.yml`, `lint.yml`, `docs.yml`) and `CONTRIBUTING.md` updated accordingly.
- **License changed from Apache-2.0 to MIT.** The `LICENSE` file now contains the canonical MIT License text; `pyproject.toml`'s SPDX expression (`license = "MIT"`) and Trove classifier (`"License :: OSI Approved :: MIT License"`) updated to match. MIT remains compatible with Home Assistant Core's Apache-2.0 licensing — MIT-licensed code can be incorporated into Apache-2.0 projects. v0.1.0 on PyPI stays as Apache-2.0 (published releases are immutable); the next release will ship as MIT. Downstream consumers should review the new license terms before upgrading.

## [0.1.0] - 2026-05-12

### Added

- Initial scaffold based on the `proconip-pypi` stack: hatchling+hatch-vcs
  build, ruff/mypy strict tooling, mkdocs-material docs site, devcontainer,
  CI workflows (lint, test, codeql, docs, automerge, release-drafter,
  PyPI Trusted Publishing).
- Apache-2.0 license (chosen for Home Assistant Core compatibility).
- Async `VioletClient` targeting the Pooldigital Violet pool controller API.
- Typed view layer (~200 documented fields) over the raw `/getReadings`
  JSON response, with shared enums (`OutputState`, `CoverState`,
  `OnewireState`, `DmxSceneState`, `RuleState`, `SimpleOnOff`, `YesNo`,
  `DosingType`, `PvSurplusState`).
- Setpoint validators with vendor-documented ranges.
- Cover control guarded by mandatory `acknowledge_unsafe=True` opt-in.
- Stateful aiohttp mock service in `tools/myviolet_mock/`.
- Test + coverage summary rendered to the GitHub Actions step summary
  via `.github/scripts/summarize_tests.py`.

[Unreleased]: https://github.com/ylabonte/myviolet/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ylabonte/myviolet/releases/tag/v0.1.0
