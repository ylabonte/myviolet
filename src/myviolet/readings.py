"""`VioletReadings` — the typed facade over a raw `/getReadings` JSON dict.

All typed views are computed lazily and memoized via `cached_property` so
that repeatedly accessing the same view on a snapshot is free and returns
the same object identity.
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import cached_property
from types import MappingProxyType
from typing import Any

from .hardware import HardwareProfile
from .models.chemistry import WaterChemistry
from .models.cover import Cover
from .models.dmx import DmxScene, collect_dmx_scenes
from .models.dosing import DosingChannel, collect_dosing_channels
from .models.extension import ExtensionRelay, collect_extension_relays
from .models.inputs import (
    CanEmptyInput,
    DigitalInput,
    collect_can_empty_inputs,
    collect_digital_inputs,
)
from .models.outputs import (
    Backwash,
    BackwashRinse,
    Eco,
    Heater,
    Light,
    Pump,
    Refill,
    Solar,
)
from .models.rules import SwitchingRule, collect_switching_rules
from .models.sensors import (
    AnalogSensor,
    ImpulseInput,
    OneWireSensor,
    collect_analog_sensors,
    collect_impulse_inputs,
    collect_onewire_sensors,
)
from .models.system import SystemInfo
from .models.system_states import (
    BackwashStatus,
    BathingAi,
    OverflowState,
    PvSurplus,
)


class VioletReadings:
    """Typed read-only view of one `/getReadings` snapshot.

    Wraps the parsed JSON dict from the controller. Every typed accessor is
    lazy and memoized; the underlying dict remains accessible as `.raw` so
    callers can still reach undocumented or firmware-specific keys.
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        # Defensive copy: the caller may still hold a reference to `raw` and
        # later mutate it; without a copy, that would silently corrupt the
        # memoized typed views on this snapshot. Shallow is enough — the
        # /getReadings payload is a flat dict of JSON scalars.
        self._raw = dict(raw)

    @property
    def raw(self) -> Mapping[str, Any]:
        """Read-only view of the original `/getReadings` JSON dict.

        Returned as a `MappingProxyType` so callers can read any key
        (including undocumented or firmware-future ones) but cannot mutate
        the underlying dict in a way that would corrupt cached typed views.
        """
        return MappingProxyType(self._raw)

    # ---- system & metadata ------------------------------------------------

    @cached_property
    def system_info(self) -> SystemInfo:
        return SystemInfo.from_raw(self._raw)

    @cached_property
    def hardware_profile(self) -> HardwareProfile:
        return HardwareProfile.from_raw(self._raw)

    # ---- sensors ----------------------------------------------------------

    @cached_property
    def analog_sensors(self) -> dict[int, AnalogSensor]:
        return collect_analog_sensors(self._raw)

    @cached_property
    def impulse_inputs(self) -> dict[int, ImpulseInput]:
        return collect_impulse_inputs(self._raw)

    @cached_property
    def onewire_sensors(self) -> dict[int, OneWireSensor]:
        return collect_onewire_sensors(self._raw)

    @cached_property
    def water_chemistry(self) -> WaterChemistry:
        return WaterChemistry.from_raw(self._raw)

    # ---- outputs ----------------------------------------------------------

    @cached_property
    def pump(self) -> Pump | None:
        return Pump.from_raw(self._raw)

    @cached_property
    def heater(self) -> Heater | None:
        return Heater.from_raw(self._raw)

    @cached_property
    def solar(self) -> Solar | None:
        return Solar.from_raw(self._raw)

    @cached_property
    def light(self) -> Light | None:
        return Light.from_raw(self._raw)

    @cached_property
    def refill(self) -> Refill | None:
        return Refill.from_raw(self._raw)

    @cached_property
    def eco(self) -> Eco | None:
        return Eco.from_raw(self._raw)

    @cached_property
    def backwash(self) -> Backwash | None:
        return Backwash.from_raw(self._raw)

    @cached_property
    def backwash_rinse(self) -> BackwashRinse | None:
        return BackwashRinse.from_raw(self._raw)

    # ---- cover, dmx, extension, dosing -----------------------------------

    @cached_property
    def cover(self) -> Cover | None:
        return Cover.from_raw(self._raw)

    @cached_property
    def dmx_scenes(self) -> dict[int, DmxScene]:
        return collect_dmx_scenes(self._raw)

    @cached_property
    def extension_relays(self) -> dict[int, dict[int, ExtensionRelay]]:
        return collect_extension_relays(self._raw)

    @cached_property
    def dosing_channels(self) -> dict[str, DosingChannel]:
        return collect_dosing_channels(self._raw)

    # ---- inputs & rules ---------------------------------------------------

    @cached_property
    def digital_inputs(self) -> dict[int, DigitalInput]:
        return collect_digital_inputs(self._raw)

    @cached_property
    def can_empty_inputs(self) -> dict[int, CanEmptyInput]:
        return collect_can_empty_inputs(self._raw)

    @cached_property
    def switching_rules(self) -> dict[int, SwitchingRule]:
        return collect_switching_rules(self._raw)

    # ---- mixed system states ---------------------------------------------

    @cached_property
    def overflow(self) -> OverflowState | None:
        return OverflowState.from_raw(self._raw)

    @cached_property
    def backwash_status(self) -> BackwashStatus | None:
        return BackwashStatus.from_raw(self._raw)

    @cached_property
    def bathing_ai(self) -> BathingAi | None:
        return BathingAi.from_raw(self._raw)

    @cached_property
    def pv_surplus(self) -> PvSurplus | None:
        return PvSurplus.from_raw(self._raw)
