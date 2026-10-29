import threading
import time

from slack_sdk.errors import SlackApiError

from purrbot import ai, config, content, detection, images, pacing, providers
from purrbot.eventlog import EventLog
from purrbot.memory import ConversationMemory
from purrbot.optout import OptOutStore
from purrbot.shush import ShushStore
from purrbot.titles import PictureTitles

DEDUP_WINDOW_SIZE = 1000
_seen_message_ids: dict[str, None] = {}
_seen_lock = threading.Lock()


def register(
    app,
    store: OptOutStore,
    shush: ShushStore,
    memory: ConversationMemory,
    event_log: EventLog,
) -> None:
    persona = ai.CatPersona(config.AI_API_KEY, config.AI_MODEL, config.AI_URL) if config.AI_API_KEY else None
    titles = PictureTitles()

    bot_user_id = app.client.auth_test()["user_id"]

    def _reflex_allowed(user_id: str | None, channel_id: str, dedupe_key: str) -> bool:
        if user_id and store.is_opted_out(user_id):
            return False
        if shush.is_muted(channel_id):
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
            _answer_dm(event, say, client, persona, memory, event_log)
            return
        if not _reflex_allowed(event.get("user"), event["channel"], _message_key(event)):
            return
        _reflex(event, say, client, titles, event_log)



    @app.event("reaction_added")
    def handle_reaction_added(event, say) -> None:
        if event.get("user)") == bot_user_id:
            return
        item = event["item"]
        if item.get("type") != "message":
            return
        reaction = event["reaction"].split("::")[0]
        if not _reflex_allowed(event.get("user"), item["channel"], event["event_ts"]):
            return
        started = time.perf_counter()
        result = _reaction_reflex(item, reaction, say, titles)
        if result is None:
            return
        kind, source, posted = result
        _record(
            event_log,
            kind,
            item["channel"],
            event.get("user"),
            "posted" if posted else "dropped",
            started,
            {"provider": source},
        )
        
    @app.event("app_mention")
    def handle_app_mention(event, say) -> None:
        started = time.perf_counter()
        posted = pacing.post(say, event["channel"], text=content.WELCOME_MESSAGE, thread_ts=event["ts"])
        _record(
            event_log,
            "app_mention",
            event["channel"],
            event.get["user"],
            "posted" if posted else "dropped",
            started,
        )

def _message_key(event) -> str:
    return event.get("client_msg_id") or event["ts"]


def _already_seen(message_id: str) -> bool:
    with _seen_lock:
        if message_id in _seen_message_ids:
            return True
        _seen_message_ids[message_id] = None
        while len(_seen_message_ids) > DEDUPE_WINDOW_SIZE:
            _seen_message_ids.pop(next(iter(_seen_message_ids)))
    return False



def _record(
        event_log: EventLog,
        kind:str,
        channel_id: str | None,
        user_id: str | None,
        outcome: str,
        started: float,
        extra: dict | None = None,
) -> None:
    event_log.record(
        kind,
        channel_id,
        user_id,
        outcome,
        duration_ms=int((time.perf_counter() - started) * 1000),
        extra=extra,
    )


def _reflex(event, say, client, titles: PictureTitles, event_log: EventLog) -> None:
    started = time.perf_counter()
    text = event.get("text", "")
    if detection.cat_word_in(text):
        source, posted = _post_cat(say, event["channel"], event["ts"], titles)
        _react(client, event, content.CAT_EMOJI)
        _record(
            event_log,
            "cat_picture",
            event["channel"],
            event.get("user"),
            "posted" if posted else "dropped",
            started,
            {"provider": source},
        )
    elif detection.duck_word_in(text):
        source, posted = _post_duck(say, event["channel"], event["ts"], titles)
        _react(client, event, content.DUCK_EMOJI)
        _record(
            event_log,
            "duck_picture",
            event["channel"],
            event.get("user"),
            "posted" if posted else "dropped",
            started,
            {"provider": source},
        )
    else:
        code = detection.status_code_in(text)
        if code is None:
            return
        posted = _thread_picture(
            say,
            event["channel"],
            event["ts"],
            images.status_picture_blocks(code),
            images.status_picture_title(code),
        )
        _react(client, event, content.CAT_EMOJI)
        _record(
            event_log,
            "status_picture",
            event["channel"],
            event.get("user"),
            "posted" if posted else "dropped",
            started,
            {"code": code, "provider": "http.cat"},
        )

def _post_cat(say, channel_id: str, thread_ts: str, titles: PictureTitles) -> None:
    picture = providers.cat_images.picture()
    _thread_picture(
        say,
        channel_id,
        thread_ts,
        images.cat_picture_blocks(titles.next("cat"), picture),
    )

def _post_duck(say, channel_id: str, thread_ts: str, titles: PictureTitles) -> None:
    picture = providers.duck_images.picture()
    _thread_picture(
        say,
        channel_id,
        thread_ts,
        images.duck_picture_blocks(titles.next("duck"), picture),
    )

def _reaction_reflex(item, reaction: str, say, titles: PictureTitles) -> None:
    if reaction == content.CAT_EMOJI:
        _post_cat(say, item["channel"], item["ts"], titles)
    elif reaction == content.DUCK_EMOJI:
        _post_duck(say, item["channel"], item["ts"], titles)


def _thread_picture(
    say,
    channel_id: str,
    thread_ts: str,
    blocks,
    text: str | None = None,
) -> None:
    fallback = {"text": text} if text is not None else {}
    pacing.post(say, channel_id, blocks=blocks, thread_ts=thread_ts, **fallback)



def _react(client, event, emoji: str) -> None:
    client.reactions_add(channel=event["channel"], name=emoji, timestamp=event["ts"])

def _answer_dm(
        event,
        say,
        client,
        persona: ai.CatPersona | None,
        memory: ConversationMemory,
) -> None:
    user_id = event.get("user") or event["channel"]
    if persona is None:
        pacing.post(say, event["channel"], text=content.CAT_BRAIN_UNPLUGGED_REPLY)
        return
    if not memory.history(user_id):
        _first_contact(memory, user_id, client, event)
    memory.append(user_id, "user", event.get("text", ""))
    memory.flush()
    messages = memory.history(user_id)
    reply = persona.reply(messages)
    memory.append(user_id, "assistant", reply)
    memory.flush()
    messages = memory.history(user_id)
    reply = persona.reply(messages)
    memory.append(user_id, "assistant", reply)
    memory.flush()
    pacing.post(say, event["channel'], text=reply"])


def _first_contact(memory: ConversationMemory, user_id: str, client, event) -> None:
    try:
        history = client.conversations_history(
            channel=event["channel"], limit=config.AI_CONTEXT_MESSAGE_LIMIT
        )
    except SlackApiError:
        return
    _seed_memory(memory, user_id, history.get("messages", []), event["ts"])


def _seed_memory(
        memory: ConversationMemory,
        user_id: str,
        slack_messages,
        current_ts: str,
) -> None:
    for message in reversed(slack_messages):
        if message.get("ts") == current_ts:
            continue
        text = message.get("text")
        if not text:
            continue
        role = "assistant" if message.get("bot_id") else "user"
        memory.append(user_id, role, text)
