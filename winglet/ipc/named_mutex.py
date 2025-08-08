# winglet/ipc/named_mutex.py
from __future__ import annotations

import logging
from contextlib import suppress
from typing import TYPE_CHECKING

import win32api
import win32event

if TYPE_CHECKING:
    from types import TracebackType

# Placeholder logger — will be replaced with a configured logger that writes to
# .winglet/logs/log-<timestamp>.txt when running as a daemon
logger = logging.getLogger(__name__)


class NamedMutex:
    def __init__(self, name: str, *, enable_auto_cleanup: bool = True) -> None:
        self._name = name
        self._enable_auto_cleanup = enable_auto_cleanup

        initial_owner = False
        self._handle: int = win32event.CreateMutex(None, initial_owner, name)
        if not self._handle:
            error_code = win32api.GetLastError()
            error_msg = win32api.FormatMessage(error_code).strip()
            msg = f"Failed to create mutex '{name}': [{error_code}] {error_msg}"
            logger.error(msg)
            raise OSError(msg)

    def acquire(self, blocking: bool = True, timeout: float | None = None) -> bool:  # noqa: FBT001, FBT002
        if (not blocking) and (timeout is not None):
            logger.warning('timeout is ignored for non-blocking acquire')

        timeout_ms = (
            0
            if not blocking
            else int(timeout * 1000)
            if timeout is not None
            else win32event.INFINITE
        )

        timeout_expr = (
            'INFINITE'
            if (timeout_ms == win32event.INFINITE)
            else f'{timeout_ms / 1000} seconds'
        )

        logger.info(
            "Acquiring mutex '%s' with timeout %s",
            self._name,
            timeout_expr,
        )
        result = win32event.WaitForSingleObject(self._handle, timeout_ms)

        match result:
            case win32event.WAIT_OBJECT_0:
                logger.info("Mutex '%s' acquired successfully", self._name)
                return True
            case win32event.WAIT_ABANDONED:
                logger.warning(
                    "Mutex '%s' was abandoned (previous owner exited without releasing).",
                    self._name,
                )
                return True
            case win32event.WAIT_TIMEOUT:
                if blocking:
                    logger.info("Mutex '%s' acquisition timed out", self._name)
                else:
                    logger.info("Mutex '%s' is already acquired", self._name)
                return False
            case win32event.WAIT_FAILED:
                error_code = win32api.GetLastError()
                error_msg = win32api.FormatMessage(error_code).strip()
                logger.error(
                    "Failed to acquire mutex '%s': [%d] %s",
                    self._name,
                    error_code,
                    error_msg,
                )
                return False
            case _:
                logger.error(
                    "Unexpected result %d when acquiring mutex '%s'",
                    result,
                    self._name,
                )
                return False

    def release(self) -> None:
        logger.info("Releasing mutex '%s'", self._name)
        if self._handle is None:
            logger.warning("Cannot release mutex '%s': handle is None", self._name)
            return

        win32event.ReleaseMutex(self._handle)

    def __del__(self) -> None:
        if self._enable_auto_cleanup and self._handle is not None:
            with suppress(Exception):
                self.release()
            logger.info("Cleaning up mutex '%s'", self._name)
            with suppress(Exception):
                win32api.CloseHandle(self._handle)
        else:
            logger.info("Skipping cleanup for mutex '%s'", self._name)

    def __enter__(self) -> bool:
        logger.info("Entering context for mutex '%s'", self._name)
        return self.acquire(blocking=True)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        logger.info("Exiting context for mutex '%s'", self._name)
        with suppress(Exception):
            self.release()
