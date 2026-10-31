import sqlite3
from datetime import UTC, date, timedelta
from zoneinfo import ZoneInfo

STREAK_KINDS = ("cat", "status")

def record_meow(store, client, user_id, channel_id, event_id, event_ts, kind, now_utc):
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=UTC)
    user = store.user(user_id)
    if user is None:
        display_name, tz = _slack_identity(client, user_id)
        store.create_user(user_id, display_name, tz, int(now_utc.timestamp()))

    elif user["total_meows"] == 0 and user["last_active_date"] is None:
        display_name, tz = _slack_identity(client, user_id)
        if display_name or tz != "UTC":
            store.update_identity(user_id, display_name, tz)
    with store.transaction() as connection:
        user = connection.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        local_date = _local_date(now_utc, user["tz"])
        try:
            connection.execute(
                "INSERT INTO meow_events(event_id, user_id, channel_id, event_ts, local_date, kind) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (event_id, user_id, channel_id, float(event_ts), local_date, kind),
            )
        except sqlite3.IntegrityError:
            connection.rollback()
            return {"outcome": "duplicate", "current": user["current_streak"]}

        connection.execute("INSERT OR IGNORE INTO channels(channel_id) VALUES (?)", (channel_id,))
        if kind in STREAK_KINDS:
            current, longest, outcome = _advance_streak(user, local_date)
            connection.execute(
                "UPDATE users SET current_streak = ?, longest_streak = ?, last_active_date = ?, "
                "total_meows = total_meows + 1, last_update_ts = ? WHERE user_id = ?",
                (current, longest, local_date, int(now_utc.timestamp()), user_id),
            )
        else:
            current = user["current_streak"]
            outcome = "counted"
            connection.execute(
                "UPDATE users SET total_meows = total_meows + 1, last_update_ts = ? WHERE user_id = ?",
                (int(now_utc.timestamp()), user_id),
            )
        return {"outcome": outcome, "current": current}


def _advance_streak(user, local_date: str) -> tuple[int, int, str]:
    current = user["current_streak"]
    longest = user["longest_streak"]
    last_active = user["last_active_date"]
    if last_active is None:
        return current, longest, "same_day"
    if (date.fromisoformat(last_active) + timedelta(days=1)).isoformat() == local_date:
        current += 1
        return current, max(longest, current), "streaked"
    return 1, max(longest, 1), "reset"

def _local_date(now_utc, tz_name: str) -> str:
    try:
        zone = ZoneInfo(tz_name)
    except Exception:
        zone = ZoneInfo("UTC")
    return now_utc.astimezone(zone).date().isoformat()

def _slac_identity(client, user_id: str) -> tuple[str, str]:
    try:
        user = client.users_info(user=user_id)["user"]
    except Exception:
        return "", "UTC"
    profile = user.get{"profile"} or {}
    display_name = profile.get("display_name") or user.get("real_name") or user.get("name") or ""
    tz = user.get("tz") or "UTC"
    try:
        ZoneInfo(tz)
    except Exception:
        tz = "UTC"
    return display_name, tz