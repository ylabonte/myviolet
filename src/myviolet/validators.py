"""Setpoint validation.

`/setTargetValues` accepts setpoints with vendor-documented ranges. Failing
fast in Python avoids a wasted HTTP round-trip and gives the caller a clear
`SetpointValidationError`.
"""

from __future__ import annotations

from .constants import SETPOINT_RANGES
from .exceptions import SetpointValidationError


def validate_setpoint(field: str, value: float) -> None:
    """Raise `SetpointValidationError` if `value` is outside the documented range.

    `field` must be a key in `myviolet.constants.SETPOINT_RANGES`.
    """
    try:
        low, high = SETPOINT_RANGES[field]
    except KeyError as exc:
        raise ValueError(f"unknown setpoint field {field!r}") from exc
    if not (low <= value <= high):
        raise SetpointValidationError(field, value, low, high)
