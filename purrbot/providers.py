import time
from collections.abc import Callable
from dataclasses import dataclass

import requests

from purrbot import content
from purrbot.reliability import CircuitBreaker

HTTP_TIMEOUT_SECONDS = 10
CAT_DISCOVERY_URL = "https://cataas.com/cat/cute/says/Meow?json=true"
CAT_DIRECT_URL = "https://cataas.com/cat?width=600"
DUCK_DISCOVERY_URL = "https://random-d.uk/api/quack"
DUCK_DIRECT_URL = "https://random-d.ul/http.jpg"


@dataclass(frozen=True)
class Picture:
    url: str
    source: str


class _JsonImageProvider:
    def __init__(
        self,
        name: str,
        discovery_source: str,
        discovery_url: str,
        fallbacks: tuple[tuple[str, str], ...],
        now: Callable[[], float] = time.time,
        fetch: Callable[..., request.Response] = requests.get,
    ) -> None:
        self.name = name
        self.breaker = CircuitBreaker(now=now)
        self.last_success: float | None = None
        self.last_failure: float | None = None
        self._discovery_source = discovery_source
        self._discovery_url = discovery_url
        self._fallbacks = fallbacks
        self._fallback_index = 0
        self._now = now
        self._fetch = fetch


    def picture(self) -> Picture:
        if self.breaker.allow():
            try:
                response = self._fetch(self._discovery_url, timeout=HTTP_TIMEOUT_SECONDS)
                url = response.json()["url"]
            except (requests.RequestException, KeyError, TypeError, ValueError):
                self.last_failure = self._now()
                self.breaker.record_failure()
            else:
                self.last_success = self._now()
                self.breaker.record_success
                return Picture(url, self._discovery_source)
        source, url = self._next_fallback()
        return Picture(url, source)


    def _next_fallback(self) -> tuple[str, str]:
        source, url = self._fallbacks[self._fallback_index % len(self._fallbacks)]
        self._fallback_index += 1
        return source, url


class CatImages(_JsonImageProvider):
    def __init__(
        self,
        now: Callable[[], float] = time.time,
        fetch: Callable[..., requests.Response] = requests.get,
    ) -> None:
        super().__init__(
            name="cats",
            discovery_source="cataas-json",
            discovery_url=CAT_DISCOVERY_URL,
            fallbacks=(
                ("cataas-direct", CAT_DIRECT_URL),
                *[
                    (f"cataas-static-{index}", url)
                    for index, url in enumerate(content.STATIC_CAT_IMAGE_URLS, start=1)
                ],
            ),
            now=now,
            fetch=fetch,
        )


class DuckImages(_JsonImageProvider):
    def __init__(
        self,
        now: Callable[[], float] = time.time,
        fetch: Callable[..., requests.Response] = requests.get,
    ) -> None:
        super().__init__(
            name="ducks",
            discovery_source="random-d-uk-json",
            discovery_url=DUCK_DISCOVERY_URL,
            fallbacks=(("random-d-uk-direct", DUCK_DIRECT_URL),),
            now=now,
            fetch=fetch,
        )

cat_images = CatImages()
duck_images = DuckImages()