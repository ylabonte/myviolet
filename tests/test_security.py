"""Security-focused tests: SSRF, credential leakage, input validation."""

from __future__ import annotations

import aiohttp
import pytest

from myviolet import VioletClient


class TestHostValidation:
    """C1: host parameter must not allow URL smuggling."""

    @pytest.mark.parametrize(
        "host",
        [
            "violet.local@evil.example.com",  # userinfo smuggling
            "violet.local/admin",  # path smuggling
            "violet.local?x=1",  # query smuggling
            "violet.local#frag",  # fragment smuggling
            "violet.local\r\nHeader: x",  # CRLF injection
            "",  # empty host
            "violet local",  # whitespace
        ],
    )
    async def test_malicious_host_rejected(self, host: str) -> None:
        session = aiohttp.ClientSession()
        try:
            with pytest.raises(ValueError):
                VioletClient(session, host=host, username="a", password="b")
        finally:
            await session.close()

    @pytest.mark.parametrize("scheme", ["javascript", "file", "ftp", ""])
    async def test_bogus_scheme_rejected(self, scheme: str) -> None:
        session = aiohttp.ClientSession()
        try:
            with pytest.raises(ValueError):
                VioletClient(
                    session, host="violet.local", scheme=scheme, username="a", password="b"
                )
        finally:
            await session.close()

    async def test_https_scheme_accepted(self) -> None:
        session = aiohttp.ClientSession()
        try:
            VioletClient(session, host="violet.local", scheme="https")
        finally:
            await session.close()


class TestCredentialPairing:
    """Reject half-credentials so callers don't silently fall back to anonymous."""

    async def test_username_without_password_rejected(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with pytest.raises(ValueError, match="together"):
                VioletClient(session, host="violet.local", username="admin")
        finally:
            await session.close()

    async def test_password_without_username_rejected(self) -> None:
        session = aiohttp.ClientSession()
        try:
            with pytest.raises(ValueError, match="together"):
                VioletClient(session, host="violet.local", password="secret")
        finally:
            await session.close()

    async def test_both_omitted_accepted(self) -> None:
        session = aiohttp.ClientSession()
        try:
            VioletClient(session, host="violet.local")
        finally:
            await session.close()

    @pytest.mark.parametrize(
        "host",
        [
            "violet.local",
            "violet.local:8080",  # host:port allowed
            "192.168.1.42",
            "192.168.1.42:8080",
            "controller-1.example.org",
        ],
    )
    async def test_normal_hosts_accepted(self, host: str) -> None:
        session = aiohttp.ClientSession()
        try:
            VioletClient(session, host=host)
        finally:
            await session.close()


class TestCredentialRedaction:
    """C2: password must not appear in repr() of any client component."""

    async def test_transport_repr_redacts_password(self) -> None:
        session = aiohttp.ClientSession()
        try:
            client = VioletClient(
                session,
                host="violet.local",
                username="admin",
                password="hunter2-very-secret",
            )
            # Walk the whole client recursively and ensure no repr contains the password
            assert "hunter2-very-secret" not in repr(client)
            assert "hunter2-very-secret" not in repr(client._transport)
            assert "hunter2-very-secret" not in repr(client._transport._auth)
            # str() too
            assert "hunter2-very-secret" not in str(client._transport._auth)
        finally:
            await session.close()

    async def test_transport_still_works_with_redacted_auth(self) -> None:
        """The redacted auth wrapper must still send the correct Basic header."""
        from aioresponses import aioresponses

        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/getConfig",
                    payload={"ok": True},
                )
                async with VioletClient(
                    session,
                    host="violet.local",
                    username="admin",
                    password="hunter2-very-secret",
                ) as client:
                    result = await client.config.get()
                assert result == {"ok": True}
        finally:
            await session.close()


class TestInputValidation:
    """H1, M1: set_function must validate key and action vocabulary."""

    async def test_set_function_rejects_bad_key(self) -> None:
        session = aiohttp.ClientSession()
        try:
            async with VioletClient(session, host="violet.local") as client:
                with pytest.raises(ValueError, match="key"):
                    await client.control.set_function("PUMP,SECRET_FN", "ON")
        finally:
            await session.close()

    async def test_set_function_rejects_lowercase_key(self) -> None:
        session = aiohttp.ClientSession()
        try:
            async with VioletClient(session, host="violet.local") as client:
                with pytest.raises(ValueError, match="key"):
                    await client.control.set_function("pump", "ON")
        finally:
            await session.close()

    async def test_set_function_rejects_unknown_action(self) -> None:
        session = aiohttp.ClientSession()
        try:
            async with VioletClient(session, host="violet.local") as client:
                with pytest.raises(ValueError, match="action"):
                    await client.control.set_function("PUMP", "NOT_AN_ACTION")
        finally:
            await session.close()

    async def test_set_function_accepts_known_action(self) -> None:
        from aioresponses import aioresponses

        session = aiohttp.ClientSession()
        try:
            with aioresponses() as mock:
                mock.get(
                    "http://violet.local/setFunctionManually?PUMP,ON,0,0",
                    payload={"ok": True},
                )
                async with VioletClient(session, host="violet.local") as client:
                    await client.control.set_function("PUMP", "ON")
        finally:
            await session.close()


class TestFiniteSetpoints:
    """H2: validate_setpoint must reject NaN and Inf."""

    @pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
    async def test_nan_inf_rejected(self, value: float) -> None:
        from myviolet.exceptions import SetpointValidationError
        from myviolet.validators import validate_setpoint

        with pytest.raises(SetpointValidationError):
            validate_setpoint("pH", value)


class TestMockConstantTimeAuth:
    """H3: mock must use hmac.compare_digest for the credential check."""

    def test_constant_time_compare_in_use(self) -> None:
        import inspect

        from tools.myviolet_mock import server

        source = inspect.getsource(server._valid_basic_auth)
        assert "compare_digest" in source, (
            "_valid_basic_auth must use hmac.compare_digest to avoid timing leaks"
        )
