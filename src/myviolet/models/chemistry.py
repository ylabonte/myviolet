"""Water chemistry typed view: pH, ORP, chlorine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._common import MeasuredValue


@dataclass(frozen=True, slots=True)
class WaterChemistry:
    """Pool water chemistry readings (pH, ORP, free chlorine)."""

    ph: MeasuredValue | None
    orp: MeasuredValue | None
    chlorine: MeasuredValue | None

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> WaterChemistry:
        return cls(
            ph=MeasuredValue.from_raw(raw, "pH", unit="pH"),
            orp=MeasuredValue.from_raw(raw, "orp", unit="mV"),
            chlorine=MeasuredValue.from_raw(raw, "pot", unit="mg/L"),
        )
