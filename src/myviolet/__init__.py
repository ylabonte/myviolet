"""Async Python library for the Pooldigital Violet pool controller."""

try:
    from ._version import __version__
except ImportError:  # pragma: no cover
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("myviolet")
    except PackageNotFoundError:
        __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
