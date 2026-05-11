"""Forward-compatibility, immutability, and public-surface tests."""

from __future__ import annotations

import aiohttp
import pytest

import myviolet
from myviolet import VioletClient


class TestForwardCompatibleEnums:
    """M5/M6: unknown firmware values must not crash the snapshot."""

    def test_unknown_output_state_returns_none(self) -> None:
        from myviolet.models.outputs import Pump

        raw = {"PUMP": 99, "PUMP_RUNTIME": "00h 00m 00s"}
        assert Pump.from_raw(raw) is None

    def test_unknown_cover_state_returns_none(self) -> None:
        from myviolet.models.cover import Cover

        assert Cover.from_raw({"COVER_STATE": "AJAR_NEW_FIRMWARE_STATE"}) is None

    def test_known_state_still_works(self) -> None:
        from myviolet.models.cover import Cover

        cover = Cover.from_raw({"COVER_STATE": "OPEN"})
        assert cover is not None


class TestRawImmutability:
    """M7: VioletReadings.raw must not allow callers to corrupt memoized views."""

    def test_raw_is_immutable_mapping(self) -> None:
        from myviolet.readings import VioletReadings

        snapshot = VioletReadings({"PUMP": 1, "PUMP_RUNTIME": "00h 00m 00s"})
        raw = snapshot.raw
        with pytest.raises(TypeError):
            raw["PUMP"] = 99  # type: ignore[index]


class TestNamespaceDisambiguation:
    """M3: the dosing-parameters namespace should not collide with the dosing control method."""

    async def test_dosing_parameters_namespace_exists(self) -> None:
        session = aiohttp.ClientSession()
        try:
            async with VioletClient(session, host="violet.local") as client:
                # The namespace for /setDosingParameters
                assert hasattr(client, "dosing_parameters")
                assert hasattr(client.dosing_parameters, "set")
                # The control method is unambiguously namespaced under .control
                assert hasattr(client.control, "dosing")
        finally:
            await session.close()


class TestPublicSurface:
    """M4: typed view classes must be part of the documented public API."""

    @pytest.mark.parametrize(
        "name",
        [
            "VioletClient",
            "VioletReadings",
            "HardwareProfile",
            "WaterChemistry",
            "MeasuredValue",
            "Pump",
            "Heater",
            "Cover",
            "DosingChannel",
            "ExtensionRelay",
            "DmxScene",
            "OneWireSensor",
            "SystemInfo",
            "OutputState",
            "CoverState",
        ],
    )
    def test_top_level_export(self, name: str) -> None:
        assert hasattr(myviolet, name), f"myviolet.{name} should be exported"
        assert name in myviolet.__all__, f"{name!r} missing from myviolet.__all__"


class TestStrictAckUnsafe:
    """M8: cover_open/cover_close should accept only the literal True."""

    async def test_truthy_string_rejected(self) -> None:
        from myviolet.exceptions import UnsafeOperationException

        session = aiohttp.ClientSession()
        try:
            async with VioletClient(session, host="violet.local") as client:
                with pytest.raises(UnsafeOperationException):
                    await client.control.cover_open(
                        acknowledge_unsafe="yes"  # type: ignore[arg-type]
                    )
        finally:
            await session.close()

    async def test_one_int_rejected(self) -> None:
        from myviolet.exceptions import UnsafeOperationException

        session = aiohttp.ClientSession()
        try:
            async with VioletClient(session, host="violet.local") as client:
                with pytest.raises(UnsafeOperationException):
                    await client.control.cover_open(
                        acknowledge_unsafe=1  # type: ignore[arg-type]
                    )
        finally:
            await session.close()
