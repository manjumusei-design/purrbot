import threading
import time
from datetime import UTC, datetime

from slack_sdk.errors import SlackApiError

from purrbot import ai, config, content, detection, images, pacing, providers
from purrbot.eventlog import EventLog
from purrbot.memory import ConversationMemory
from purrbot.shush import ShushStore
from purrbot.store import Store
from purrbot.titles import PictureTitles

DM_DEDUPE_WINDOW_SIZE = 1000
_seen_dm_ids: dict[str, None] = {}
_seen_dm_lock = threading.Lock()
_seeded_users : set[str] = set()
_seeded_lock = threading.Lock()


def register(
    app,
    store: Store,
    shush: ShushStore,
    memory: ConversationMemory,
    event_log: EventLog,
) -> None:
    persona = ai.CatPersona(config.AI_API_KEY, config.AI_MODEL, config.AI_URL) if config.AI_API_KEY else None
    titles = PictureTitles()

    bot_user_id = app.client.auth_test()["user_id"]

    @app.event("message")
    def handle_message(event, say, client) -> None:
        if event.get("bot_id"):
            return
        if event.get("subtype"):
            return
        is_dm = event.get("channel_type") == "im"

        if is_dm:
            if _dm_already_seen(f"{event['channel']}:{_message_key(event)}"):
                return
            _answer_dm(event, say, client, persona, memory, event_log)
            return
        if not reflex_allowed(store, shush, event.get("user"), event["channel"]):
            return
        _reflex(event, say, client, titles, event_log, store)

    @app.event("reaction_added")
    def handle_reaction_added(event, say, client) -> None:
        if event.get("user") == bot_user_id:
            return
        item = event["item"]
        if item.get("type") != "message":
            return
        reaction = event["reaction"].split("::")[0]
        kind = _reaction_kind(reaction)
        if kind is None:
            return
        if not reflex_allowed(store, shush, event.get("user"), item["channel"]):
            return
        started = time.perf_counter()
        outcome = streaks.record_meow(
            store,
            client,
            event.get("user"),
            item["channe"],
            f"reaction:{event['event_ts']}",
            event["event_ts"],
            kind,
            datetime.now(UTC),
        )
        if outcome["outcome"] == "duplicate":
            return
        result = _reaction_reflex(item, reaction, say, titles)
        if result is None:
            return
        log_kind, source, posted = result
        _record(
            event_log,
            log_kind,
            item["channel"],
            event.get("user"),
            "posted" if posted else "dropped",
            started,
            {"provider": source, **_streak_extra(outcome)},
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

def reflex_allowed(store: Store, shush: ShushStore, user_id: str | None, channel_id: str) -> bool:
    if user_id and store.is_opted_out(user_id):
        return False
    if shush.is_muted(channel_id):
        return False
    if not store.channel_allowed(channel_id):
        return False
    return True

def _message_key(event) -> str:
    return event.get("client_msg_id") or event["ts"]


def _dm_already_seen(message_id: str) -> bool:
    with _seen_dm_lock:
        if message_id in _seen_dm_ids:
            return True
        _seen_dm_ids[message_id] = None
        while len(_seen_dm_ids) > DM_DEDUPE_WINDOW_SIZE:
            _seen_dm_ids.pop(next(iter(_seen_dm_ids)))
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
        _react(client, event, content.CAT_EMOJI)
    elif detection.duck_word_in(text):
        source, posted = _post_duck(say, event["channel"], event["ts"], titles)
        _record(
            event_log,
            "duck_picture",
            event["channel"],
            event.get("user"),
            "posted" if posted else "dropped",
            started,
            {"provider": source},
        )
        _react(client, event, content.DUCK_EMOJI)
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
        _record(
            event_log,
            "status_picture",
            event["channel"],
            event.get("user"),
            "posted" if posted else "dropped",
            started,
            {"code": code, "provider": "http.cat"},
        )
        _react(client, event, content.CAT_EMOJI)

def _post_cat(
    say,
    channel_id: str,
    thread_ts: str,
    titles: PictureTitles,
) -> tuple[str, bool]:
    picture = providers.cat_images.picture()
    posted = _thread_picture(
        say,
        channel_id,
        thread_ts,
        images.cat_picture_blocks(titles.next("cat"), picture),
    )
    return picture.source, posted


def _post_duck(
    say,
    channel_id: str,
    thread_ts: str,
    titles: PictureTitles,
) -> tuple[str, bool]:
    picture = providers.duck_images.picture()
    posted = _thread_picture(
        say,
        channel_id,
        thread_ts,
        images.duck_picture_blocks(titles.next("duck"), picture),
    )
    return picture.source, posted



def _reaction_reflex(
    item,
    reaction: str,
    say,
    titles: PictureTitles,
) -> tuple[str, str, bool] | None:
    if reaction == content.CAT_EMOJI:
        source, posted = _post_cat(say, item["channel"], item["ts"], titles)
        return "reaction_cat", source, posted
    if reaction == content.DUCK_EMOJI:
        source, posted = _post_duck(say, item["channel"], item["ts"], titles)
        return "reaction_duck", source, posted
    return None


def _thread_picture(
    say,
    channel_id: str,
    thread_ts: str,
    blocks,
    text: str | None = None,
) -> bool:
    fallback = {"text": text} if text is not None else {}
    return pacing.post(say, channel_id, blocks=blocks, thread_ts=thread_ts, **fallback)


def _react(client, event, emoji: str) -> None:
    client.reactions_add(channel=event["channel"], name=emoji, timestamp=event["ts"])

def _answer_dm(
        event,
        say,
        client,
        persona: ai.CatPersona | None,
        memory: ConversationMemory,
        event_log: EventLog,
) -> None:
    user_id = event.get("user") or event["channel"]
    started = time.perf_counter()
    if persona is None:
        posted = pacing.post(say, event["channel"], text=content.CAT_BRAIN_UNPLUGGED_REPLY)
        _record(
            event_log,
            "dm_persona",
            event["channel"],
            user_id,
            "unplugged" if posted else "dropped",
            started,
        )
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
    posted = pacing.post(say, event["channel"], text=reply)
    _record(
        event_log,
        "dm_persona",
        event["channel"],
        user_id,
        "replied" if posted else "dropped",
        started,
        {"messages": len(messages)},
    )


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
