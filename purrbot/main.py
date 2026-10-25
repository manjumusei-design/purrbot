import sys

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from purrbot import commands, config, events
from purrbot.optout import OptOutStore
from purrbot.shush import ShushStore

def main() -> int:
    if not config.BOT_TOKEN or not config.APP_TOKEN:
        print("purrbot needs BOT_TOKEN and APP_TOKEN in .env — see .env.example nya", file=sys.stderr)
        return 1
    app = App(token=config.BOT_TOKEN)
    shush = ShushStore()
    events.register(app, store, shush)
    commands.register(app, store, shush)
    SocketModeHandler(app, config.APP_TOKEN).start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())