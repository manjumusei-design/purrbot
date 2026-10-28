import json
import os
import tempfile
import threading
from pathlib import Path

class ConversationMemory:
    def __init__(self, path: str, limit: int = 40) -> None:
        self.path = Path(path)
        self.limit = limit
        self._users: dict[str, list[dict]] = {}
        self._loaded = False
        self._lock = threading.Lock()

    def history(self, user_id: str) -> list[dict]:
        with self._lock:
            self._ensure_loaded()
            return [dict(message) for message in self._users.get(user_id, [])]

    def append(self, user_id: str, role: str, content: str) -> None:
        with self._lock:
            self._ensure_loaded()
            messages = self._users.setdefault(user_id, [])
            messages.append({"role": role, "content": content})
            if len(messages) > self.limit:
                del messages[: len(messages) - self.limit]

    def flush(self) -> None:
        with self._lock:
            self._ensure_loaded()
            self._write()

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError
            self._users = {
                str(user_id): [
                    {"role": message["role"], "content": message["content"]}
                    for message in messages
                ][-self.limit :]
                for user_id, messages in data.items()
                if isinstance(messages, list)
            }
        except (OSError, KeyError, TypeError, ValueError):
            self._users = {}



    def _write(self) -> None:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir = self.path.parent,
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            try:
                json.dump(self._users, temp_file, indent=2)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            except Exception:
                os.unlink(temp_path)
                raise
        os.replace(temp_path, self.path)
        directory_fd = os.open(self.path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
            