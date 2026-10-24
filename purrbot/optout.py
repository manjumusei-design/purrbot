import json
import os
import tempfile
from pathlib import Path

class OptOutStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.user_ids: set[str] = set()
        self._load()

    def is_opted_out(self, user_id: str) -> bool:
        return user_id in self.user_ids

    def add(self, user_id: str) -> None:
        self.user_ids.add(user_id)
        self._flush()

    def remove(self, user_id: str) -> None:
        self.user_ids.discard(user_id)
        self._flush()

    def _load(self) -> None:
        if not self.path.exists():
            self.user_ids = set()
            return
        self.user_ids = set(json.loads(self.path.read_text(encoding="utf-8")))

    def _flush(self) -> None:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=self.path.parent,
            delete=False,
        ) as temp_file:
            json.dump(sorted(self.user_ids), temp_file)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = temp_file.name
        os.replace(temp_path, self.path)