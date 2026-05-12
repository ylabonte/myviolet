"""End-to-end integration tests against the real mock subprocess.

Opt-in via ``pytest -m integration``. These tests spawn the mock service in
a child Python process, then drive a `VioletClient` against it to verify
write→read round-trip semantics.
"""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
from collections.abc import AsyncIterator
from pathlib import Path

import aiohttp
import pytest

from myviolet import VioletClient
from myviolet.enums import CoverState, OutputState

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def _wait_for_port(host: str, port: int, *, timeout: float = 10.0) -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return
        except (OSError, ConnectionRefusedError):
            await asyncio.sleep(0.1)
    raise TimeoutError(f"mock server did not start on {host}:{port}")


@pytest.fixture
async def mock_server() -> AsyncIterator[tuple[str, int, str, str]]:
    port = _free_port()
    user = "test_admin"
    password = "test_secret"
    env = {
        **os.environ,
        "MYVIOLET_MOCK_HOST": "127.0.0.1",
        "MYVIOLET_MOCK_PORT": str(port),
        "MYVIOLET_MOCK_USER": user,
        "MYVIOLET_MOCK_PASS": password,
    }
    # Inherit stdout/stderr so a noisy mock crash (e.g. import-time traceback)
    # is visible in pytest's captured output instead of deadlocking on a full
    # PIPE buffer that nothing drains.
    proc = subprocess.Popen(
        [PYTHON, "-m", "tools.myviolet_mock"],
        cwd=REPO_ROOT,
        env=env,
    )
    try:
        await _wait_for_port("127.0.0.1", port)
        yield "127.0.0.1", port, user, password
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            # Reap the kill so we don't leave a zombie behind.
            proc.wait(timeout=5)


@pytest.mark.integration
async def test_round_trip_readings(mock_server: tuple[str, int, str, str]) -> None:
    host, port, user, password = mock_server
    async with (
        aiohttp.ClientSession() as session,
        VioletClient(session, host=f"{host}:{port}", username=user, password=password) as client,
    ):
        snapshot = await client.readings.get()

    # The seed has the demo controller's values
    assert snapshot.water_chemistry.ph is not None
    assert snapshot.cover is not None
    assert snapshot.cover.state is CoverState.OPEN


@pytest.mark.integration
async def test_round_trip_pump_control(mock_server: tuple[str, int, str, str]) -> None:
    host, port, user, password = mock_server
    async with (
        aiohttp.ClientSession() as session,
        VioletClient(session, host=f"{host}:{port}", username=user, password=password) as client,
    ):
        initial = await client.readings.get()
        assert initial.pump is not None
        initial_state = initial.pump.state

        await client.control.pump("OFF")

        after = await client.readings.get()
        assert after.pump is not None
        assert after.pump.state is OutputState.MANUAL_OFF
        assert after.pump.state is not initial_state


@pytest.mark.integration
async def test_cover_open_requires_ack(mock_server: tuple[str, int, str, str]) -> None:
    host, port, user, password = mock_server
    async with (
        aiohttp.ClientSession() as session,
        VioletClient(session, host=f"{host}:{port}", username=user, password=password) as client,
    ):
        from myviolet.exceptions import UnsafeOperationException

        with pytest.raises(UnsafeOperationException):
            await client.control.cover_open()

        await client.control.cover_open(acknowledge_unsafe=True)
        after = await client.readings.get()
        assert after.cover is not None
        assert after.cover.state is CoverState.OPENING
