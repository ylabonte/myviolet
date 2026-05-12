"""Tests for myviolet.transport — HTTP, auth, error mapping."""

from __future__ import annotations

import aiohttp
import pytest
from aioresponses import aioresponses
from yarl import URL

from myviolet.exceptions import (
    BadCredentialsException,
    BadStatusCodeException,
    InvalidPayloadException,
    TimeoutException,
)
from myviolet.transport import VioletTransport

BASE = URL("http://violet.local")
AUTH = aiohttp.BasicAuth("admin", "secret")


async def _make_transport(
    default_timeout: float = 10.0,
) -> tuple[VioletTransport, aiohttp.ClientSession]:
    session = aiohttp.ClientSession()
    transport = VioletTransport(session, BASE, auth=AUTH, default_timeout=default_timeout)
    return transport, session


class TestGet:
    async def test_returns_parsed_json(self) -> None:
        with aioresponses() as mock:
            mock.get(
                "http://violet.local/getReadings?ALL",
                payload={"pH_value": 7.3},
                status=200,
            )
            transport, session = await _make_transport()
            try:
                result = await transport.get("/getReadings", query="ALL")
            finally:
                await session.close()
        assert result == {"pH_value": 7.3}

    async def test_get_without_query(self) -> None:
        with aioresponses() as mock:
            mock.get("http://violet.local/getConfig", payload={"a": 1})
            transport, session = await _make_transport()
            try:
                result = await transport.get("/getConfig")
            finally:
                await session.close()
        assert result == {"a": 1}

    async def test_401_raises_bad_credentials(self) -> None:
        with aioresponses() as mock:
            mock.get("http://violet.local/getConfig", status=401)
            transport, session = await _make_transport()
            try:
                with pytest.raises(BadCredentialsException) as excinfo:
                    await transport.get("/getConfig")
            finally:
                await session.close()
        assert excinfo.value.status_code == 401

    async def test_403_raises_bad_credentials(self) -> None:
        with aioresponses() as mock:
            mock.get("http://violet.local/getConfig", status=403)
            transport, session = await _make_transport()
            try:
                with pytest.raises(BadCredentialsException):
                    await transport.get("/getConfig")
            finally:
                await session.close()

    async def test_500_raises_bad_status(self) -> None:
        with aioresponses() as mock:
            mock.get("http://violet.local/getReadings?ALL", status=500)
            transport, session = await _make_transport()
            try:
                with pytest.raises(BadStatusCodeException) as excinfo:
                    await transport.get("/getReadings", query="ALL")
            finally:
                await session.close()
        assert excinfo.value.status_code == 500

    async def test_malformed_json_raises_invalid_payload(self) -> None:
        with aioresponses() as mock:
            mock.get(
                "http://violet.local/getReadings?ALL",
                status=200,
                body="not-json",
                content_type="application/json",
            )
            transport, session = await _make_transport()
            try:
                with pytest.raises(InvalidPayloadException):
                    await transport.get("/getReadings", query="ALL")
            finally:
                await session.close()

    async def test_timeout_raises_timeout_exception(self) -> None:
        with aioresponses() as mock:
            mock.get("http://violet.local/getConfig", exception=TimeoutError())
            transport, session = await _make_transport(default_timeout=0.01)
            try:
                with pytest.raises(TimeoutException):
                    await transport.get("/getConfig")
            finally:
                await session.close()


class TestPost:
    async def test_posts_json_body(self) -> None:
        with aioresponses() as mock:
            mock.post(
                "http://violet.local/setConfig",
                payload={"ok": True},
                status=200,
            )
            transport, session = await _make_transport()
            try:
                result = await transport.post("/setConfig", json={"key": "value"})
            finally:
                await session.close()
        assert result == {"ok": True}

    async def test_401_raises_bad_credentials(self) -> None:
        with aioresponses() as mock:
            mock.post("http://violet.local/setConfig", status=401)
            transport, session = await _make_transport()
            try:
                with pytest.raises(BadCredentialsException):
                    await transport.post("/setConfig", json={})
            finally:
                await session.close()


class TestAuth:
    async def test_no_auth_means_anonymous(self) -> None:
        """`auth=None` is permitted (the public read endpoints accept it)."""
        with aioresponses() as mock:
            mock.get("http://violet.local/getReadings?ALL", payload={"a": 1})
            session = aiohttp.ClientSession()
            transport = VioletTransport(session, BASE, auth=None, default_timeout=10.0)
            try:
                result = await transport.get("/getReadings", query="ALL")
            finally:
                await session.close()
        assert result == {"a": 1}
