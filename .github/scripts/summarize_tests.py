"""Render a polished Markdown test + coverage report into the GitHub Actions step summary.

Reads ``junit.xml`` (pytest's ``--junitxml`` output) and ``coverage.xml`` (Cobertura
format from coverage.py) and appends a structured Markdown block to the file
referenced by ``$GITHUB_STEP_SUMMARY``. When that env var is unset (e.g. running
locally for inspection), the report is written to stdout so it can be eyeballed.

Designed to be dependency-free — uses only the stdlib so it works on any CI
runner that has Python.
"""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TestStats:
    tests: int
    failures: int
    errors: int
    skipped: int
    time_seconds: float

    @property
    def passed(self) -> int:
        return self.tests - self.failures - self.errors - self.skipped

    @property
    def ok(self) -> bool:
        return self.failures == 0 and self.errors == 0


@dataclass(frozen=True)
class FileCoverage:
    filename: str
    line_rate: float
    branch_rate: float
    lines_valid: int
    lines_covered: int


@dataclass(frozen=True)
class CoverageStats:
    line_rate: float
    branch_rate: float
    lines_valid: int
    lines_covered: int
    files: list[FileCoverage]


def _parse_junit(path: Path) -> TestStats:
    root = ET.parse(path).getroot()
    # pytest emits either <testsuites> wrapping a <testsuite> or just <testsuite>.
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise ValueError(f"no <testsuite> element found in {path}")
    return TestStats(
        tests=int(suite.attrib.get("tests", 0)),
        failures=int(suite.attrib.get("failures", 0)),
        errors=int(suite.attrib.get("errors", 0)),
        skipped=int(suite.attrib.get("skipped", 0)),
        time_seconds=float(suite.attrib.get("time", 0.0)),
    )


def _parse_coverage(path: Path) -> CoverageStats:
    root = ET.parse(path).getroot()
    files: list[FileCoverage] = []
    for cls in root.iter("class"):
        files.append(
            FileCoverage(
                filename=cls.attrib.get("filename", "?"),
                line_rate=float(cls.attrib.get("line-rate", 0.0)),
                branch_rate=float(cls.attrib.get("branch-rate", 0.0)),
                lines_valid=_count_lines(cls, "line"),
                lines_covered=_count_lines(cls, "line", covered_only=True),
            )
        )
    files.sort(key=lambda f: (f.line_rate, f.filename))
    return CoverageStats(
        line_rate=float(root.attrib.get("line-rate", 0.0)),
        branch_rate=float(root.attrib.get("branch-rate", 0.0)),
        lines_valid=int(root.attrib.get("lines-valid", 0)),
        lines_covered=int(root.attrib.get("lines-covered", 0)),
        files=files,
    )


def _count_lines(cls: ET.Element, tag: str, *, covered_only: bool = False) -> int:
    count = 0
    for line in cls.iter(tag):
        if covered_only and int(line.attrib.get("hits", 0)) == 0:
            continue
        count += 1
    return count


def _pct(rate: float) -> str:
    return f"{rate * 100:.2f}%"


def _coverage_badge(rate: float, threshold: float) -> str:
    pct = rate * 100
    if pct >= 95:
        return "🟢"
    if pct >= threshold:
        return "🟡"
    return "🔴"


def render(
    tests: TestStats | None,
    coverage: CoverageStats | None,
    *,
    coverage_threshold: float = 80.0,
    top_files: int = 10,
) -> str:
    lines: list[str] = []

    # --- Tests --------------------------------------------------------------
    if tests is not None:
        icon = "✅" if tests.ok else "❌"
        lines.append(
            f"## {icon} Tests · {tests.passed} passed"
            + (f", {tests.failures} failed" if tests.failures else "")
            + (f", {tests.errors} errored" if tests.errors else "")
            + (f", {tests.skipped} skipped" if tests.skipped else "")
            + f" ({tests.time_seconds:.2f}s)"
        )
        lines.append("")
        lines.append("| Tests | Passed | Failed | Errors | Skipped | Duration |")
        lines.append("|---:|---:|---:|---:|---:|---:|")
        lines.append(
            f"| {tests.tests} | {tests.passed} | {tests.failures} | "
            f"{tests.errors} | {tests.skipped} | {tests.time_seconds:.2f}s |"
        )
        lines.append("")
    else:
        lines.append("## ⚠️ Tests · junit.xml not found")
        lines.append("")

    # --- Coverage -----------------------------------------------------------
    if coverage is not None:
        pct = coverage.line_rate * 100
        badge = _coverage_badge(coverage.line_rate, coverage_threshold)
        status = "above" if pct >= coverage_threshold else "below"
        lines.append(
            f"## {badge} Coverage · {_pct(coverage.line_rate)} "
            f"({status} threshold {coverage_threshold:.0f}%)"
        )
        lines.append("")
        lines.append(f"- **Lines**: {coverage.lines_covered} / {coverage.lines_valid} covered")
        lines.append(f"- **Branch coverage**: {_pct(coverage.branch_rate)}")
        lines.append("")

        below_threshold = [f for f in coverage.files if f.line_rate * 100 < coverage_threshold]
        if below_threshold:
            lines.append(f"### Files below {coverage_threshold:.0f}%")
            lines.append("")
            lines.append("| File | Lines | Covered | Coverage | Branch |")
            lines.append("|---|---:|---:|---:|---:|")
            for f in below_threshold[:top_files]:
                lines.append(
                    f"| `{f.filename}` | {f.lines_valid} | {f.lines_covered} | "
                    f"{_pct(f.line_rate)} | {_pct(f.branch_rate)} |"
                )
            if len(below_threshold) > top_files:
                lines.append(
                    f"\n_…and {len(below_threshold) - top_files} more files "
                    f"below {coverage_threshold:.0f}%._"
                )
            lines.append("")
        else:
            lines.append(f"_All tracked files meet the {coverage_threshold:.0f}% threshold._")
            lines.append("")

        # Lowest-coverage files (regardless of threshold) — useful pointer for where to add tests.
        lowest = [f for f in coverage.files if f.lines_valid > 0][:top_files]
        if lowest and not below_threshold:
            lines.append(f"### Lowest-coverage files (top {len(lowest)})")
            lines.append("")
            lines.append("| File | Lines | Covered | Coverage | Branch |")
            lines.append("|---|---:|---:|---:|---:|")
            for f in lowest:
                lines.append(
                    f"| `{f.filename}` | {f.lines_valid} | {f.lines_covered} | "
                    f"{_pct(f.line_rate)} | {_pct(f.branch_rate)} |"
                )
            lines.append("")
    else:
        lines.append("## ⚠️ Coverage · coverage.xml not found")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    junit = repo_root / "junit.xml"
    cov = repo_root / "coverage.xml"

    tests = _parse_junit(junit) if junit.exists() else None
    coverage = _parse_coverage(cov) if cov.exists() else None

    report = render(tests, coverage)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as fh:
            fh.write(report)
            fh.write("\n")
    else:
        sys.stdout.write(report + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
