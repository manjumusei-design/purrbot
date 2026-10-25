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
        try:
            self.user_ids = set(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, TypeError, ValueError):
            self.user_ids = set()

    def _flush(self) -> None:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=self.path.parent,
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            try:
                json.dump(sorted(self.user_ids), temp_file, indent=4)
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