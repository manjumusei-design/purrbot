import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY, display_name TEXT NOT NULL DEFAULT '',
  tz TEXT NOT NULL DEFAULT 'UTC',
  current_streak INTEGER NOT NULL DEFAULT 0, longest_streak INTEGER NOT NULL DEFAULT 0,
  total_meows INTEGER NOT NULL DEFAULT 0,
  last_active_date TEXT, last_update_ts INTEGER, first_meow_at INTEGER NOT NULL,
  opted_out INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS meow_events (
  event_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(user_id),
  channel_id TEXT NOT NULL, event_ts REAL NOT NULL, local_date TEXT NOT NULL, kind TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS events_by_date ON meow_events(local_date);
CREATE INDEX IF NOT EXISTS events_by_user ON meow_events(user_id, local_date);
CREATE TABLE IF NOT EXISTS channels (
  channel_id TEXT PRIMARY KEY, name TEXT NOT NULL DEFAULT '', allowed INTEGER NOT NULL DEFAULT 1
)
"""


class Store:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.journal_mode = ""

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def _transaction(self):

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def ensure_schema(self) -> str:
        with self._connection() as connection:
            self.journal_mode = str(connection.execute("PRAGMA journal_mode=WAL").fetchone()[0])
        with self._transaction() as connection:
            for statement in SCHEMA.split(";"):
                if statement.strip():
                    connection.execute(statement)
        return self.journal_mode

    def user(self, user_id: str) -> sqlite3.Row | None:
        with self._connection() as connection:
            return connection.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()

    def create_user(
            self,
            user_id: str,
            display_name: str = "",
            tz: str = "UTC",
            first_meow_at: int | None = None,
    ) -> None:
        with self._transaction() as connection:
            connection.execute (
                "INSERT OR IGNORE INTO users(user_id, display_name, tz, first_meow_at) "
                "VALUES (?, ?, ?, ?)",
                (user_id, display_name, tz, first_meow_at or int(time.time())),
            )

    def is_opted_out(self, user_id: str) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT opted_out FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return bool(row["opted_out"]) if row is not None else False


    def opt_out(self, user_id: str) -> None:
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO users(user_id, opted_out, first_meow_at) VALUES (?, 1, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET opted_out = 1",
                (user_id, int(time.time())),
            )

    def opt_in(self, user_id: str) -> None:
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO users(user_id, opted_out, first_meow_at) VALUES (?, 0, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET opted_out = 0",
                (user_id, int(time.time())),
            )

    def channel_allowed(self, channel_id: str) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT allowed FROM channels WHERE channel_id = ?", (channel_id,)
            ).fetchone()
        return bool(row["allowed"]) if row is not None else True

    
    def set_channel_allowed(self, channel_id: str, allowed: bool) -> None:
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO channels(channel_id, allowed) VALUES (?, ?) "
                "ON CONFLICT(channel_id) DO UPDATE SET allowed = excluded.allowed",
                (channel_id, int(allowed)),
            )

    def top_current(self, limit: int = 10) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT user_id, display_name, current_streak, longest_streak, total_meows "
                "FROM users WHERE current_streak > 0 "
                "ORDER BY current_streak DESC, longest_streak DESC, total_meows DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def top_longest(self, limit: int = 10) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT user_id, display_name, current_streak, longest_streak, total_meows "
                "FROM users WHERE longest_streak > 0 "
                "ORDER BY longest_streak DESC, current_streak DESC, total_meows DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def migrate_legacy_optouts(self, path: str) -> int:
        legacy = Path(path)
        if not legacy.exists():
            return 0
        try:
            user_ids = json.loads(legacy.read_text(encoding="utf-8"))
            if not isinstance(user_ids, list):
                raise ValueError
        except (OSError, TypeError, ValueError):
            user_ids = []
        with self._transaction() as connection:
            for user_id in user_ids:
                connection.execute(
                    "INSERT INTO users(user_id, opted_out, first_meow_at) VALUES (?, 1, ?) "
                    "ON CONFLICT(user_id) DO UPDATE SET opted_out = 1",
                    (str(user_id), int(time.time())),
                )
        os.replace(legacy, legacy.with_name(legacy.name + ".migrated"))
        return len(user_ids)
    