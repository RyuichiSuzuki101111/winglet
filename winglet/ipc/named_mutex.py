# winglet/ipc/named_mutex.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import TracebackType


class NamedMutex:
    def __init__(self, name: str, enable_auto_cleanup: bool = True) -> None: ...
    def acquire(self, blocking: bool = True, timeout: float | None = None) -> bool: ...
    def release(self) -> None: ...
    def __enter__(self) -> bool: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
