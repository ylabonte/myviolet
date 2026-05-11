"""Tests for myviolet.client.VioletClient and its namespaces."""

from __future__ import annotations

import json

import aiohttp
import pytest
from aioresponses import aioresponses

from myviolet import VioletClient
from myviolet.exceptions import (
    SetpointValidationError,
    UnsafeOperationException,
    VioletApiException,
)


async def _client_ctx(
    payload_get_readings: dict | None = None,
) -> tuple[VioletClient, aiohttp.ClientSession, aioresponses]:
    session = aiohttp.ClientSession()
    client = VioletClient(
        session,
        host="violet.local",
        username="admin",
        password="secret",
        timeout=5.0,
    )
    mock = aioresponses()
    mock.start()
    if payload_get_readings is not None:
        mock.get(
            "http://violet.local/getReadings?ALL,DOSAGE,RUNTIMES",
            payload=payload_get_readings,
            status=200,
        )
    return client, session, mock


class TestReadingsNamespace:
    async def test_get_default_query(self) -> None:
        client, session, mock = await _client_ctx({"pH_value": 7.3})
        try:
            async with client:
                snapshot = await client.readings.get()
            assert snapshot.raw == {"pH_value": 7.3}
        finally:
            mock.stop()
            await session.close()

    async def test_get_selective_query(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/getReadings?pH_value,PUMP",
                    payload={"pH_value": 7.3, "PUMP": 1},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    snapshot = await client.readings.get(["pH_value", "PUMP"])
                assert snapshot.raw == {"pH_value": 7.3, "PUMP": 1}
        finally:
            await session.close()


class TestControlNamespace:
    async def test_pump_on_uses_set_function_manually(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/setFunctionManually?PUMP,ON,0,0",
                    payload={"ok": True},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.control.set_function("PUMP", "ON")
                assert result == {"ok": True}
        finally:
            await session.close()

    async def test_cover_open_without_ack_raises(self) -> None:
        session = aiohttp.ClientSession()
        try:
            async with VioletClient(
                session, host="violet.local", username="admin", password="secret"
            ) as client:
                with pytest.raises(UnsafeOperationException):
                    await client.control.cover_open()
        finally:
            await session.close()

    async def test_cover_open_with_ack_proceeds(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/setFunctionManually?COVER_OPEN,PUSH,0,0",
                    payload={"ok": True},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.control.cover_open(acknowledge_unsafe=True)
                assert result == {"ok": True}
        finally:
            await session.close()

    async def test_cover_stop_does_not_require_ack(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/setFunctionManually?COVER_STOP,PUSH,0,0",
                    payload={"ok": True},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.control.cover_stop()
                assert result == {"ok": True}
        finally:
            await session.close()


class TestTargetsNamespace:
    async def test_set_ph_in_range(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/setTargetValues?target=pH&value=7.2",
                    payload={"ok": True},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.targets.set_ph(7.2)
                assert result == {"ok": True}
        finally:
            await session.close()

    async def test_set_ph_out_of_range_raises(self) -> None:
        session = aiohttp.ClientSession()
        try:
            async with VioletClient(
                session, host="violet.local", username="admin", password="secret"
            ) as client:
                with pytest.raises(SetpointValidationError):
                    await client.targets.set_ph(8.5)
        finally:
            await session.close()


class TestConfigNamespace:
    async def test_get_config(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get("http://violet.local/getConfig", payload={"setting": 42})
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    cfg = await client.config.get()
                assert cfg == {"setting": 42}
        finally:
            await session.close()

    async def test_update_config_posts(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.post("http://violet.local/setConfig", payload={"ok": True})
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.config.update({"setting": 99})
                assert result == {"ok": True}
        finally:
            await session.close()


class TestHistoryNamespace:
    async def test_get_hours_only(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get("http://violet.local/getHistory?hours=24", payload={"rows": []})
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.history.get(24)
                assert result == {"rows": []}
        finally:
            await session.close()

    async def test_get_with_sensor(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/getHistory?hours=24&sensor=pH",
                    payload={"rows": [{"t": 0, "v": 7.3}]},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.history.get(24, sensor="pH")
                assert result == {"rows": [{"t": 0, "v": 7.3}]}
        finally:
            await session.close()

    async def test_sensor_param_is_url_encoded(self) -> None:
        """A `sensor` value with `&`/`=` must be encoded, not smuggled in."""
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                # If encoding works, the literal request goes to the safe URL below.
                # If it didn't, the request would hit ?hours=24&sensor=x&hours=999
                # and this mock wouldn't match.
                mock.get(
                    "http://violet.local/getHistory?hours=24&sensor=x%26hours%3D999",
                    payload={"ok": True},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.history.get(24, sensor="x&hours=999")
                assert result == {"ok": True}
        finally:
            await session.close()


class TestCalibrationNamespace:
    async def test_raw_values(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/getCalibrationRawValues",
                    payload={"ADC1_raw": 0.48},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.calibration.raw_values()
                assert result == {"ADC1_raw": 0.48}
        finally:
            await session.close()

    async def test_history_uses_sensor_param(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/getCalibrationHistory?sensor=pH",
                    payload={"rows": []},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.calibration.history("pH")
                assert result == {"rows": []}
        finally:
            await session.close()

    async def test_history_sensor_is_url_encoded(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/getCalibrationHistory?sensor=x%26evil%3D1",
                    payload={"ok": True},
                )
                async with VioletClient(
                    session, host="violet.local", username="admin", password="secret"
                ) as client:
                    result = await client.calibration.history("x&evil=1")
                assert result == {"ok": True}
        finally:
            await session.close()


class TestClientLifecycle:
    async def test_context_manager_returns_self(self) -> None:
        session = aiohttp.ClientSession()
        try:
            async with VioletClient(
                session, host="violet.local", username="admin", password="secret"
            ) as client:
                assert isinstance(client, VioletClient)
        finally:
            await session.close()

    async def test_anonymous_client(self) -> None:
        """No credentials = anonymous access (public read endpoints)."""
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/getReadings?ALL,DOSAGE,RUNTIMES",
                    payload={"x": 1},
                )
                async with VioletClient(session, host="violet.local") as client:
                    snapshot = await client.readings.get()
                assert snapshot.raw == {"x": 1}
        finally:
            await session.close()

    async def test_https_scheme(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "https://violet.local/getReadings?ALL,DOSAGE,RUNTIMES",
                    payload={"x": 1},
                )
                async with VioletClient(session, host="violet.local", scheme="https") as client:
                    snapshot = await client.readings.get()
                assert snapshot.raw == {"x": 1}
        finally:
            await session.close()


# Silence unused-import warnings for VioletApiException; it's documented as
# the umbrella exception type for blanket catches even if not raised here.
_ = (VioletApiException, json)
