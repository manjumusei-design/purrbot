import time
from collections.abc import Callable

DEFAULT_SHUSH_MINUTES = 30
MIN_SHUSH_MINUTES = 1
MAX_SHUSH_MINUTES = 1440


class ShushStore:
    def __init__(self, now: Callable[[], float] = time.time) -> None:
        self._now = now
        self._until: dict[str, float] = {}

    def mute(self, channel_id: str, minutes: int) -> float:
        minutes = max(MIN_SHUSH_MINUTES, min(MAX_SHUSH_MINUTES, minutes))
        until = self._now() + minutes * 60
        self._until[channel_id] = until
        return until

    def unmute(self, channel_id: str) -> None:
        self._until.pop(channel_id, None)

    def is_muted(self, channel_id: str) -> bool:
        until = self._until.get(channel_id)
        if until is None:
            return False
        return True