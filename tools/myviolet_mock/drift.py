"""Deterministic sensor drift for the myviolet mock controller.

The real controller's sensor readings oscillate slightly over time. The mock
reproduces this without random sources so tests stay reproducible: drift is
a sine wave keyed off the elapsed seconds since mock start.
"""

from __future__ import annotations

import math
from typing import Any

# Sensor key → (oscillation amplitude, period in seconds)
_DRIFT_PROFILE: dict[str, tuple[float, float]] = {
    "pH_value": (0.05, 300.0),
    "orp_value": (1.5, 240.0),
    "pot_value": (0.02, 180.0),
    "CPU_TEMP": (0.5, 600.0),
}


def apply_drift(snapshot: dict[str, Any], *, elapsed_seconds: float) -> dict[str, Any]:
    """Return `snapshot` with sensor drift applied to known oscillating fields.

    The input dict is mutated and returned. Non-sensor keys are untouched.
    """
    for key, (amplitude, period) in _DRIFT_PROFILE.items():
        if key not in snapshot:
            continue
        baseline = float(snapshot[key])
        delta = amplitude * math.sin((2 * math.pi * elapsed_seconds) / period)
        snapshot[key] = round(baseline + delta, 3)
    return snapshot
