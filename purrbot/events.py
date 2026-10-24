from purrbot import ai, config, content, detection, images
from purrbot.optout import OptOutStore

DEDUP_WINDOW_SIZE = 1000
_seen_message_ids: dict[str, None] = {}


def register(app, store: OptOutStore) -> None:
    persona = ai.CatPersona(config.AI_API_KEY, config.AI_MODEL, config.AI_URL) if config.AI_API_KEY else None


    @app.event("message")
    def handle_message(event, say, client) -> None:
        if event.get("bot_id"):
            return
        if event.get("subtype"):
            return
        if event.get("channel_type") == "im":
            _answer_dm(event, say, client, persona)
            return
        if event.get("user") and store.is_opted_out(event["user"]):
            return
        if _already_seen(event):
            return
        _reflex(event, say, client)


    @app.event("app_mention")
    def handle_app_mention(event, say) -> None:
        say(text = content.WELCOME_MESSAGE, thread_ts=event["ts"])


def _already_seen(event) -> bool:
    message_id = event.get("client_msg_id") or event["ts"]
    if message_id in _seen_message_ids:
        return True
    _seen_message_ids[message_id] = None
    while len(_seen_message_ids) > DEDUPE_WINDOW_SIZE:
        _seen_message_ids.pop(next(inter(_seen_message_ids)))
    return False

