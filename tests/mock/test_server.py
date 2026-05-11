"""Tests for tools.myviolet_mock.server."""

from __future__ import annotations

import base64
from typing import Any

import pytest
from aiohttp.test_utils import TestClient, TestServer

from tools.myviolet_mock.server import create_app
from tools.myviolet_mock.state import MockState

USER = "admin"
PASSWORD = "admin"


def _seed() -> dict[str, Any]:
    return {
        "PUMP": 1,
        "PUMP_LAST_ON": 1778500800,
        "PUMP_LAST_OFF": 0,
        "PUMP_RUNTIME": "00h 00m 00s",
        "HEATER": 0,
        "COVER_STATE": "OPEN",
        "pH_value": 7.3,
        "pH_value_min": 7.0,
        "pH_value_max": 7.5,
    }


def _basic_header() -> dict[str, str]:
    token = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@pytest.fixture
async def client():
    state = MockState(_seed())
    app = create_app(state, username=USER, password=PASSWORD)
    server = TestServer(app)
    async with TestClient(server) as tc:
        yield tc


class TestGetReadings:
    async def test_returns_full_snapshot_with_all(self, client: TestClient) -> None:
        async with client.get("/getReadings", params="ALL") as resp:
            assert resp.status == 200
            body = await resp.json()
        assert body["PUMP"] == 1

    async def test_no_args_returns_500(self, client: TestClient) -> None:
        async with client.get("/getReadings") as resp:
            assert resp.status == 500

    async def test_selective_query_filters(self, client: TestClient) -> None:
        async with client.get("/getReadings", params="pH_value,PUMP") as resp:
            assert resp.status == 200
            body = await resp.json()
        # Only requested keys are returned (plus their _min/_max siblings)
        assert "PUMP" in body
        assert "pH_value" in body
        assert "COVER_STATE" not in body


class TestSetFunctionManually:
    async def test_pump_on_mutates_state(self, client: TestClient) -> None:
        async with client.get(
            "/setFunctionManually",
            params="PUMP,ON,0,0",
            headers=_basic_header(),
        ) as resp:
            assert resp.status == 200

        # Now read state and confirm PUMP is MANUAL_ON (4)
        async with client.get("/getReadings", params="ALL") as resp:
            body = await resp.json()
        assert body["PUMP"] == 4

    async def test_requires_auth(self, client: TestClient) -> None:
        async with client.get("/setFunctionManually", params="PUMP,ON,0,0") as resp:
            assert resp.status == 401


class TestSetTargetValues:
    async def test_pH_target_mutates_state(self, client: TestClient) -> None:
        async with client.get(
            "/setTargetValues",
            params={"target": "pH", "value": "7.2"},
            headers=_basic_header(),
        ) as resp:
            assert resp.status == 200
        async with client.get("/getReadings", params="ALL") as resp:
            body = await resp.json()
        assert body.get("pH_target") == 7.2


class TestGetConfig:
    async def test_requires_auth(self, client: TestClient) -> None:
        async with client.get("/getConfig") as resp:
            assert resp.status == 401

    async def test_returns_config_when_authed(self, client: TestClient) -> None:
        async with client.get("/getConfig", headers=_basic_header()) as resp:
            assert resp.status == 200
            body = await resp.json()
        assert isinstance(body, dict)


class TestSetConfig:
    async def test_post_mutates_config(self, client: TestClient) -> None:
        payload = {"newKey": "value"}
        async with client.post("/setConfig", json=payload, headers=_basic_header()) as resp:
            assert resp.status == 200
        async with client.get("/getConfig", headers=_basic_header()) as resp:
            body = await resp.json()
        assert body["newKey"] == "value"
