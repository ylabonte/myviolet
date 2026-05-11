"""Entry point: ``python -m tools.myviolet_mock``."""

from __future__ import annotations

import logging
import os

from aiohttp import web

from .seed import load_seed
from .server import create_app
from .state import MockState


def _env(key: str, default: str) -> str:
    return os.environ.get(key, default)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    host = _env("MYVIOLET_MOCK_HOST", "0.0.0.0")
    port = int(_env("MYVIOLET_MOCK_PORT", "8080"))
    username = _env("MYVIOLET_MOCK_USER", "admin")
    password = _env("MYVIOLET_MOCK_PASS", "admin")

    state = MockState(load_seed())
    app = create_app(state, username=username, password=password)
    logging.getLogger("myviolet_mock").info(
        "Violet mock listening on http://%s:%d (user=%s)", host, port, username
    )
    web.run_app(app, host=host, port=port, print=None)


if __name__ == "__main__":
    main()
