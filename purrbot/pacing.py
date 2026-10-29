import threading
import time
from collections.abc import Callable

from slack_sdk.errors import SlackApiError

DEFAULT_RATE = 1.0
DEFAULT_CAPACITY = 3.0
DEFAULT_MAX_WAIT = 2.0
RETRY_CAP_SECONDS = 10.0

class TokenBucket:
    def __init__(
        self,
        rate: float = DEFAULT_RATE,
        capacity: float = DEFAULT_CAPACITY,
        now: Callable[[], float] = time.time,
    ) -> None:
        self.rate = rate
        self.capacity = capacity
        self._now = now
        self._tokens = capacity
        self._last = now()

    def take(self, max_wait: float = DEFAULT_MAX_WAIT) -> float:
        now = self._now()
        elapsed = max(0.0, now - self._last)
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last = now
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return 0.0
        wait = (1.0 - self._tokens) / self.rate
        self._tokens -= 1.0
        if wait > max_wait:
            return 0.0
        return wait


class ChannelPacer:
    def __init__(
        self,
        rate: float = DEFAULT_RATE,
        capacity: float = DEFAULT_CAPACITY,
        max_wait: float = DEFAULT_MAX_WAIT,
        now: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._rate = rate
        self._capacity = capacity
        self._max_wait = max_wait
        self._now = now
        self._sleep = sleep
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def wait(self, channel_id: str) -> None:
        with self._lock:
            bucket = self._buckets.get(channel_id)
            if bucket is None:
                bucket = TokenBucket(self._rate, self._capacity, self._now)
                self._buckets[channel_id] = bucket
            delay = bucket.take(self._max_wait)
        if delay > 0:
            self._sleep(delay)


def _rate_limited(error: SlackApiError) -> bool:
    try:
        if error.response.status_code == 429:
            return True
        return error.response.get("error") in {"ratelimited", "rate_limited"}
    except AttributeError:
        return False

def _retry_after(error: SlackApiError) -> float:
    try:
        return float(error.response.headers.get("Retry-After", 1.0))
    except (AttributeError, TypeError, ValueError):
        return 1.0


def post(poster: Callable[..., object], channel_id: str, **kwargs) -> bool:
    channel_pacer.wait(channel_id)
    try:
        poster(**kwargs)
    except SlackApiError as error:
        if not _rate_limited(error):
            raise
        time.sleep(min(_retry_after(error), RETRY_CAP_SECONDS))
        try:
            poster(**kwargs)
        except SlackApiError:
            return False
    return True



channel_pacer = ChannelPacer()
