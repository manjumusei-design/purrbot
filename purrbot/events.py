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
        if _already_seen(event):
            return
        if event.get("channel_type") == "im":
            _answer_dm(event, say, client, persona)
            return
        if event.get("user") and store.is_opted_out(event["user"]):
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


def _reflex(event, say, client) -> None:
    text = event.get("text", "")
    if detection.cat_word_in(text):
        _thread_picture(say, event, images.cat_picture_blocks())
        _react(client, event, content.CAT_EMOJI)
    elif detection.duck_word_in(text):
        _thread_picture(say, event, images.duck_picture_blocks())
        _react(client, event, content.DUCK_EMOJI)
    else:
        code = detection.status_code_in(text)
        if code is None:
            return
        _thread_picture(say, event, images.status_picture_blocks(code), images.status_picture_title(code))
        _react(client, event, content.CAT_EMOJI)


def _thread_picture(say, event, blocks, text: str | None = None) -> None:
    fallback = {"text": text} if text  is not None else {}
    say(blocks = blocks, thread_ts = event["ts"], **fallback)

def _react(client, event, emoji: str) -> None:
    client.reactions_add(channel=event["channel"], name=emoji, timestamp=event["ts"])

def _answer_dm(event, say,client, persona: ai.CatPersona | None) -> None:
    if persona is None:
        say(text=content.CAT_BRAIN_UNPLUGGED_REPLY)
        return
    history = client.conversations_history(
        channel=event["channel"], limit=config.AI_CONTEXT_MESSAGE_LIMIT
    )
    messages = [
        {
            "role": "assistant" if message.get("bot_id") else "user",
            "content": message.get("text", ""),
        }
        for message in reversed(history.get("messages", []))
    ]
    say(text=persona.reply(messages))
