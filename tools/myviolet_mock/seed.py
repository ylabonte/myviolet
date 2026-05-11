"""Load the captured `/getReadings` snapshot used to seed the mock state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_SEED_PATH = (
    Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "getReadings_seed.json"
)


def load_seed(path: Path | None = None) -> dict[str, Any]:
    """Load a seed snapshot from disk (defaults to the captured demo response)."""
    target = path or DEFAULT_SEED_PATH
    with target.open() as fh:
        return json.load(fh)  # type: ignore[no-any-return]
