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
