# myviolet

## 0.1.1

### Patch Changes

- **Loosened `aiohttp` pin from `>=3.13.5,<4` to `>=3.10,<4`.** Lets the library install into Home Assistant Core environments that still ship an older aiohttp than the most recent release. `yarl>=1.23.0,<2` unchanged in this release.
- **Development dependencies moved from `[project.optional-dependencies]` to `[dependency-groups]`** (PEP 735). The `dev`, `test`, and `docs` groups were never user-facing extras; they're for working *on* the package, not *with* it. They no longer appear as `Provides-Extra:` on PyPI. Local install: `pip install -e . --group dev --group test --group docs` (requires pip ≥ 25.1). CI workflows (`test.yml`, `lint.yml`, `docs.yml`) and `CONTRIBUTING.md` updated accordingly.
- **License changed from Apache-2.0 to MIT.** The `LICENSE` file now contains the canonical MIT License text; `pyproject.toml`'s SPDX expression (`license = "MIT"`) and Trove classifier (`"License :: OSI Approved :: MIT License"`) updated to match. v0.1.0 on PyPI stays as Apache-2.0 (published releases are immutable); from 0.1.1 onwards the package ships as MIT. Downstream consumers should review the new license terms before upgrading.

## 0.1.0

### Minor Changes

- Initial public release. Async `VioletClient` for the Pooldigital Violet pool controller, primarily intended as the foundation for a Home Assistant integration.
- Typed view layer over the ~400-key `/getReadings` JSON, covering all ~200 documented fields plus observed extras (`EXT2_*`, `ADC6_value`, `DOS_3_ELO_REV`). Shared enums for `OutputState`, `CoverState`, `OnewireState`, `DmxSceneState`, `RuleState`, `SimpleOnOff`, `YesNo`, `DosingType`, `PvSurplusState`.
- Forward-compatible parsing: unknown firmware enum values degrade gracefully (skip-and-continue for collections, return `None` for atomic snapshots) instead of crashing `/getReadings` parsing.
- Immutable snapshots: `MappingProxyType` / `frozenset` / `tuple` for container fields; defensive copy of the input dict in `VioletReadings.__init__`.
- Security pass: SSRF-resistant host validation, `SafeBasicAuth` redacted `repr`, constant-time credential compare in the mock, allowlist + regex on control keys and readings selectors, `NaN`/`Inf` rejection in setpoint validation, cover control gated behind `acknowledge_unsafe=True`.
- Setpoint validators with vendor-documented ranges. Stateful aiohttp mock controller in `tools/myviolet_mock/` with deterministic sensor drift — used by the bundled integration tests.
- Project stack: hatchling + hatch-vcs build, Apache-2.0 (relicensed to MIT in 0.1.1), ruff/mypy strict tooling, mkdocs-material docs, devcontainer, full CI (lint, test, codeql, docs, PyPI Trusted Publishing).
- Test + coverage summary rendered into the GitHub Actions step summary via `.github/scripts/summarize_tests.py`.
