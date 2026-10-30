import os
import sys

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from purrbot import commands, config, events
from purrbot.eventlog import EventLog
from purrbot.memory import ConversationMemory
from purrbot.shush import ShushStore
from purrbot.store import Store

def main() -> int:
    if not config.BOT_TOKEN or not config.APP_TOKEN:
        print("purrbot needs BOT_TOKEN and APP_TOKEN in .env — see .env.example nya", file=sys.stderr)
        return 1
    os.makedirs(config.PURRBOT_STATE_DIR, exist_ok=True)
    app = App(token=config.BOT_TOKEN)
    store = Store(config.state_path("purrbot.db"))
    journal_mode = store.ensure_schema()
    imported = store.migrate_legacy_optouts(config.state_path("optouts.json"))
    print(
        f"purrbot store: sqlite journal_mode={journal_mode}, imported {imported} opt-outs",
        file=sys.stderr,
    )
    shush = ShushStore()
    memory = ConversationMemory(config.state_path("memories.json"))
    event_log = EventLog(config.state_path("events.jsonl"))
    events.register(app, store, shush, memory, event_log)
    commands.register(app, store, shush, event_log)
    SocketModeHandler(app, config.APP_TOKEN).start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())