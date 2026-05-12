"""Cover typed view (read-only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..enums import CoverState


@dataclass(frozen=True, slots=True)
class Cover:
    """Pool cover state (read-only; control is via `client.control.cover_*`)."""

    state: CoverState

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> Cover | None:
        """Build from `COVER_STATE`. Unknown firmware values return ``None``."""
        state_raw = raw.get("COVER_STATE")
        if state_raw is None:
            return None
        try:
            return cls(state=CoverState(str(state_raw)))
        except ValueError:
            return None
