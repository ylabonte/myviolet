"""Tests for myviolet.models.sensors."""

from __future__ import annotations

import pytest

from myviolet.enums import OnewireState
from myviolet.models.sensors import (
    AnalogSensor,
    ImpulseInput,
    collect_analog_sensors,
    collect_impulse_inputs,
    collect_onewire_sensors,
)


def test_analog_sensor_collect(get_readings_seed: dict) -> None:
    sensors = collect_analog_sensors(get_readings_seed)
    # The live demo emits ADC1..ADC6; older firmware may only expose ADC1..ADC5
    assert len(sensors) >= 1
    for idx, sensor in sensors.items():
        assert 1 <= idx <= 6
        assert isinstance(sensor, AnalogSensor)
    # ADC6 is present in the bundled seed; make sure we don't drop it on the floor
    assert 6 in sensors


def test_onewire_unknown_state_skips_sensor(get_readings_seed: dict) -> None:
    """Forward-compat: a new firmware onewire state string drops just that sensor."""
    raw = dict(get_readings_seed)
    raw["onewire1_state"] = "FUTURE_STATE"
    sensors = collect_onewire_sensors(raw)
    assert 1 not in sensors
    # ... but the other configured sensors are still collected.
    assert len(sensors) >= 1


def test_impulse_input_collect(get_readings_seed: dict) -> None:
    inputs = collect_impulse_inputs(get_readings_seed)
    assert 1 in inputs
    assert isinstance(inputs[1], ImpulseInput)
    assert inputs[1].value == pytest.approx(get_readings_seed["IMP1_value"])


def test_onewire_sensor_collect(get_readings_seed: dict) -> None:
    sensors = collect_onewire_sensors(get_readings_seed)
    # Demo controller has 10 active + 2 unconfigured sensors
    assert len(sensors) == 12

    sensor1 = sensors[1]
    assert sensor1.state is OnewireState.OK
    assert sensor1.rom_code == "28121883321901A9"
    assert sensor1.value == pytest.approx(30.2)
    assert sensor1.unit == "°C"

    sensor11 = sensors[11]
    assert sensor11.state is OnewireState.NO_SENSOR_CONFIGURED
    assert sensor11.value == pytest.approx(0.0)


def test_onewire_sensor_present_only_when_configured() -> None:
    """When `_state` is missing entirely, the slot is not exposed."""
    sensors = collect_onewire_sensors({"onewire1_value": 22.0, "onewire1_state": "OK"})
    assert 1 in sensors
    assert 2 not in sensors
