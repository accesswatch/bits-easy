"""Logging shim for the BITS-EASY runtime.

Inside NVDA, every log call should route through ``logHandler.log`` so that
messages show up in NVDA's log viewer at the user's chosen log level. Outside
NVDA (unit tests, CLI scripts, the build host), ``logHandler`` does not exist,
so we fall back to a stdlib logger that writes to stderr.

All log messages are prefixed with ``BITS-EASY:`` so they are trivially
greppable in ``%APPDATA%/nvda/nvda.log``.
"""

from __future__ import annotations

import contextlib
import logging
import sys
from typing import Any, Callable, Iterator, TypeVar

_T = TypeVar("_T")

_LOG_PREFIX = "BITS-EASY"
_stdlib_configured = False


def _build_stdlib_logger(name: str) -> logging.Logger:
    global _stdlib_configured
    logger = logging.getLogger(name)
    if not _stdlib_configured:
        root = logging.getLogger("bits_easy")
        if not root.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
            root.addHandler(handler)
            root.setLevel(logging.INFO)
            root.propagate = False
        _stdlib_configured = True
    return logger


def get_logger(name: str = "bits_easy") -> Any:
    """Return NVDA's ``log`` if available, otherwise a stdlib logger.

    NVDA's logger ignores ``name`` (it is a single global instance), but stdlib
    loggers honour the hierarchy, so callers can pass ``"bits_easy.engine"``
    and get sensible filtering in tests.
    """

    try:
        from logHandler import log as nvda_log

        return nvda_log
    except Exception:
        return _build_stdlib_logger(name)


@contextlib.contextmanager
def log_and_default(logger: Any, label: str) -> Iterator[None]:
    """Catch any exception inside the block and log it with context.

    Usage::

        with log_and_default(logger, "loading clip library"):
            return json.loads(path.read_text(encoding="utf-8"))
        return default_value

    If the block raises, the exception is logged at ``ERROR`` level with the
    traceback and the caller's fall-through path runs.
    """

    try:
        yield
    except Exception:
        try:
            logger.exception("%s: %s failed", _LOG_PREFIX, label)
        except Exception:
            # If logging itself blows up we still must not crash the addon.
            pass


def run_with_default(
    logger: Any,
    label: str,
    fn: Callable[[], _T],
    default: _T,
) -> _T:
    """Run ``fn`` and return its result, or log+return ``default`` on error.

    Convenience wrapper for the very common load-or-default pattern in the
    runtime's JSON state services.
    """

    try:
        return fn()
    except Exception:
        try:
            logger.exception("%s: %s failed", _LOG_PREFIX, label)
        except Exception:
            pass
        return default


__all__ = ["get_logger", "log_and_default", "run_with_default"]

