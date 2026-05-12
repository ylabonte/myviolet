"""Tests for myviolet.models.outputs."""

from __future__ import annotations

from datetime import timedelta

import pytest

from myviolet.enums import OutputState
from myviolet.models.outputs import Backwash as BackwashOutput
from myviolet.models.outputs import (
    BackwashRinse,
    Eco,
    Heater,
    Light,
    Pump,
    PumpSpeed,
    Refill,
    Solar,
)


def test_pump_with_speeds(get_readings_seed: dict) -> None:
    pump = Pump.from_raw(get_readings_seed)
    assert pump is not None
    assert pump.state is OutputState.AUTO_ON
    assert pump.runtime == timedelta(hours=8, minutes=24, seconds=43)
    assert len(pump.speeds) == 4
    speed_2 = pump.speeds[2]
    assert isinstance(speed_2, PumpSpeed)
    assert speed_2.state is OutputState.AUTO_ON
    assert speed_2.runtime == timedelta(hours=4, minutes=37, seconds=1)
    # PUMP_RPM_*_LAST_ON/OFF are always "00:00:00" per spec — exposed as None
    assert speed_2.last_on is None
    assert speed_2.last_off is None


def test_pump_speeds_is_immutable(get_readings_seed: dict) -> None:
    pump = Pump.from_raw(get_readings_seed)
    assert pump is not None
    with pytest.raises(TypeError):
        pump.speeds[99] = pump.speeds[0]  # type: ignore[index]


def test_pump_unknown_speed_state_skipped() -> None:
    """Forward-compat: unknown PUMP_RPM_N enum value drops that speed, not the pump."""
    raw = {
        "PUMP": 1,
        "PUMP_RUNTIME": "00h 00m 00s",
        "PUMP_RPM_0": 0,
        "PUMP_RPM_0_RUNTIME": "00h 00m 00s",
        "PUMP_RPM_1": 99,  # unknown firmware value
        "PUMP_RPM_1_RUNTIME": "00h 00m 00s",
        "PUMP_RPM_2": 1,
        "PUMP_RPM_2_RUNTIME": "00h 00m 00s",
    }
    pump = Pump.from_raw(raw)
    assert pump is not None
    assert 1 not in pump.speeds
    assert 0 in pump.speeds and 2 in pump.speeds


def test_heater_postrun_none(get_readings_seed: dict) -> None:
    heater = Heater.from_raw(get_readings_seed)
    assert heater is not None
    assert heater.state is OutputState.AUTO_ON
    assert heater.postrun_remaining is None  # 'NONE' sentinel


def test_heater_postrun_active() -> None:
    raw = {"HEATER": 1, "HEATER_RUNTIME": "00h 00m 00s", "HEATER_POSTRUN_TIME": 120}
    heater = Heater.from_raw(raw)
    assert heater is not None
    assert heater.postrun_remaining == timedelta(seconds=120)


@pytest.mark.parametrize(
    ("model_cls", "key"),
    [
        (Solar, "SOLAR"),
        (Light, "LIGHT"),
        (Refill, "REFILL"),
        (Eco, "ECO"),
        (BackwashOutput, "BACKWASH"),
        (BackwashRinse, "BACKWASHRINSE"),
    ],
)
def test_simple_outputs_present(model_cls, key: str, get_readings_seed: dict) -> None:
    output = model_cls.from_raw(get_readings_seed)
    assert output is not None
    # State value matches the raw integer (interpreted as OutputState)
    assert int(output.state) == int(get_readings_seed[key])


def test_missing_output_returns_none() -> None:
    """When the canonical state key isn't present, no output is built."""
    assert Solar.from_raw({}) is None
