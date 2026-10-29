import json
import threading
from datetime import UTC, datetime
from pathlib import Path

class EventLog:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()

    def record(
        self,
        kind: str,
        channel_id: str | None,
        user_id: str | None,
        outcome: str,
        duration_ms: int | None = None,
        extra: dict | None = None,
    ) -> None:
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "kind": kind,
            "channelid": channel_id,
            "user_id": user_id,
            "outcome": outcome,
            "duration_ms": duration_ms,
            "extra": extra or {},
        }
        try:
            line = json.dumps(entry) + "\n"
        except (TypeError, ValueError):
            return
        with self._lock:
            try:
                with self.path.open("a", encoding="utf-8") as log:
                    log.write(line)
                    log.flush()
            except OSError:
                pass