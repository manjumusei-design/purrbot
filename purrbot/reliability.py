import threading
import time
from collections.abc import Callable

FAILURE_THRESHOLD = 3
OPEN_SECONDS = 300.0


class CircuitBreaker:
    def __init__(
        self,
        threshold: int = FAILURE_THRESHOLD,
        open_seconds: float = OPEN_SECONDS,
        now: Callable[[], float] = time.time,
    ) -> None:
        self.threshold = threshold
        self.open_seconds = open_seconds
        self._now = now
        self._failures = 0
        self._state = "closed"
        self._opened_at = 0.0
        self._probe_in_flight = False
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    def allow(self) -> bool:
        with self._lock:
            if self._state == "closed":
                return True
            if self._state == "open":
                if self._now() < self._opened_at + self.open_seconds:
                    return False
                self._state = "half-open"
            if self._probe_in_flight:
                return False
            self._probe_in_flight = True
            return True


    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = "closed"
            self._probe_in_flight = False

    def record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            self._probe_in_flight = False
            if self._state == "half-open" or self._failures >= self.threshold:
                self._state = "open"
                self._opened_at = self._now()
