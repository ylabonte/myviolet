"""Credential-redacting wrapper around `aiohttp.BasicAuth`.

`aiohttp.BasicAuth` is a NamedTuple, so its default ``__repr__`` exposes
the plaintext password. This subclass overrides ``__repr__`` and ``__str__``
so credentials never end up in tracebacks, logs, or Home Assistant
diagnostics dumps. The ``encode()`` method (which is what aiohttp actually
calls when sending the request) is untouched.
"""

from __future__ import annotations

import aiohttp


class SafeBasicAuth(aiohttp.BasicAuth):
    """`aiohttp.BasicAuth` subclass whose repr never reveals the password."""

    __slots__ = ()

    def __repr__(self) -> str:
        return f"SafeBasicAuth(login={self.login!r}, password=***)"

    def __str__(self) -> str:
        return self.__repr__()
