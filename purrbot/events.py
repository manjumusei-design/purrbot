from purrbot import ai, config, content, detection, images
from purrbot.optout import OptOutStore
from purrbot.titles import PictureTitles

DEDUP_WINDOW_SIZE = 1000
_seen_message_ids: dict[str, None] = {}


def register(app, store: OptOutStore) -> None:
    persona = ai.CatPersona(config.AI_API_KEY, config.AI_MODEL, config.AI_URL) if config.AI_API_KEY else None
    titles = PictureTitles()

    bot_user_id = app.client.auth_test()["user_id"]

    def _reflex_allowed(user_id: str | None, channel_id: str, dedupe_key: str) -> bool:
        if user_id and store.is_opted_out(user_id):
            return False
        return not _already_seen(dedupe_key)
    

    @app.event("message")
    def handle_message(event, say, client) -> None:
        if event.get("bot_id"):
            return
        if event.get("subtype"):
            return
        is_dm = event.get("channel_type") == "im"
        if is_dm and _already_seen(_message_key(event)):
            return
        if is_dm:
            _answer_dm(event, say, client, persona)
            return
        if not _reflex_allowed(event.get("user"), event["channel"], _message_key(event)):
            return
        _reflex(event, say, client, titles)



    @app.event("reaction_added")
    def handle_reaction_added(event, say) -> None:
        if event.get("user)") == bot_user_id:
            return
        item = event["item"]
        if item.get("type") != "message":
            return
        if not _reflex_allowed(event.get("user"), item["channel"], event["event_ts"]):

    @app.event("app_mention")
    def handle_app_mention(event, say) -> None:
        say(text = content.WELCOME_MESSAGE, thread_ts=event["ts"])


def _message_key(event) -> str:
    return event.get("client_msg_id") or event["ts"]


def _already_seen(message_id: str) -> bool:
    if message_id in _seen_message_ids:
        return True
    _seen_message_ids[message_id] = None
    while len(_seen_message_ids) > DEDUPE_WINDOW_SIZE:
        _seen_message_ids.pop(next(iter(_seen_message_ids)))
    return False


def _reflex(event, say, client, titles: PictureTitles) -> None:
    text = event.get("text", "")
    if detection.cat_word_in(text):
        _post_cat(say, event["ts"], titles)
        _react(client, event, content.CAT_EMOJI)
    elif detection.duck_word_in(text):
        _post_duck(say, event["ts"], titles)
        _react(client, event, content.DUCK_EMOJI)
    else:
        code = detection.status_code_in(text)
        if code is None:
            return
        _thread_picture(
            say,
            event["ts"],
            images.status_picture_blocks(code),
            images.status_picture_title(code),
        )
        _react(client, event, content.CAT_EMOJI)


def _post_cat(say, thread_ts: str, titles: PictureTitles) -> None:
    _thread_picture(say, thread_ts, images.cat_picture_blocks(titles.next("cat")))


def _post_duck(say, thread_ts: str, titles: PictureTitles) -> None:
    _thread_picture(say, thread_ts, images.duck_picture_blocks(titles.next("duck")))


def _reaction_reflex(item, reaction: str, say, titles: PictureTitles) -> None:
    if reaction == content.CAT_EMOJI:
        _post_cat(say, item["ts"], titles)
    elif reaction == content.DUCK_EMOJI:
        _post_duck(say, item["ts"], titles)

def _thread_picture(say, thread_ts: str, blocks, text: str | None = None) -> None:
    fallback = {"text": text} if text is not None else {}
    say(blocks=blocks, thread_ts=thread_ts, **fallback)


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
