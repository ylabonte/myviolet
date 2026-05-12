"""Digital-input typed views (INPUT1-12 plus 4 can-empty switches)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DigitalInput:
    """One of the 12 digital inputs. ``closed`` mirrors the open/closed state."""

    index: int
    closed: bool


@dataclass(frozen=True, slots=True)
class CanEmptyInput:
    """One of the 4 can-empty switch contacts (INPUT_CE1-4)."""

    index: int
    closed: bool


def collect_digital_inputs(raw: dict[str, Any]) -> dict[int, DigitalInput]:
    """Return digital inputs keyed by index (1-12), present-only."""
    result: dict[int, DigitalInput] = {}
    for index in range(1, 13):
        value = raw.get(f"INPUT{index}")
        if value is None:
            continue
        result[index] = DigitalInput(index=index, closed=bool(int(value)))
    return result


def collect_can_empty_inputs(raw: dict[str, Any]) -> dict[int, CanEmptyInput]:
    """Return can-empty inputs keyed by index (1-4), present-only."""
    result: dict[int, CanEmptyInput] = {}
    for index in range(1, 5):
        value = raw.get(f"INPUT_CE{index}")
        if value is None:
            continue
        result[index] = CanEmptyInput(index=index, closed=bool(int(value)))
    return result
