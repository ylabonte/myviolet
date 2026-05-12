"""Tests for myviolet.models.inputs."""

from __future__ import annotations

from myviolet.models.inputs import (
    CanEmptyInput,
    DigitalInput,
    collect_can_empty_inputs,
    collect_digital_inputs,
)


def test_collect_digital_inputs(get_readings_seed: dict) -> None:
    inputs = collect_digital_inputs(get_readings_seed)
    assert len(inputs) == 12
    assert all(isinstance(i, DigitalInput) for i in inputs.values())
    assert inputs[1].closed == bool(get_readings_seed["INPUT1"])


def test_collect_can_empty_inputs(get_readings_seed: dict) -> None:
    inputs = collect_can_empty_inputs(get_readings_seed)
    assert len(inputs) == 4
    assert all(isinstance(i, CanEmptyInput) for i in inputs.values())


def test_skips_absent_slots() -> None:
    inputs = collect_digital_inputs({"INPUT1": 1})
    assert set(inputs.keys()) == {1}
    assert inputs[1].closed is True
