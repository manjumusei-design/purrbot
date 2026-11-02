import random
import time
from datetime import UTC, datetime, timedelta

from purrbot import content, images, pacing, providers
from purrbot.catify import catify
from purrbot.eventlog import EventLog
from purrbot.store import DEFAULT_SHUSH_MINUTES, Store


def _fresh_cat_fact_text() -> str:
    return content.CAT_FACT_PREFIX + images.fetch_cat_fact()


def _channel_label(store: Store, channel_id: str) -> str:
    name = store.channel_name(channel_id)
    return f"#{name}" if name else content.FEUD_UNKNOWN_CHANNEL


def _age_text(timestamp: float | None, now: float) -> str:
    if timestamp is None:
        return content.HEALTH_NEVER
    elapsed = max(0, int(now - timestamp))
    if elapsed < 60:
        return content.HEALTH_SECONDS_AGO.format(seconds=elapsed)
    return content.HEALTH_MINUTES_AGO.format(minutes=elapsed // 60)


def _respond_plain(respond, text: str) -> None:
    blocks = [
        {"type": "section", "text": {"type": "plain_text", "text": text, "emoji": True}}
    ]
    respond(blocks=blocks, text=text)


def register(app, store: Store, event_log: EventLog) -> None:
    def _log_command(command, outcome: str = "ok") -> None:
        event_log.record(
            command["command"],
            command.get("channel_id"),
            command.get("user_id"),
            outcome,
        )

    def _log_action(body, kind: str, outcome: str = "ok") -> None:
        event_log.record(
            kind,
            body.get("channel", {}).get("id"),
            body.get("user", {}).get("id"),
            outcome,
        )

    @app.command("/purrbot-meow")
    def meow(ack, say, command) -> None:
        ack()
        picture = providers.cat_images.picture()
        posted = pacing.post(
            say,
            command["channel_id"],
            text=content.CAT_PICTURE_TITLE,
            blocks=images.cat_picture_blocks(content.CAT_PICTURE_TITLE, picture),
        )
        _log_command(command, "ok" if posted else "dropped")

    @app.command("/purrbot-quack")
    def quack(ack, say, command) -> None:
        ack()
        picture = providers.duck_images.picture()
        posted = pacing.post(
            say,
            command["channel_id"],
            text=content.DUCK_PICTURE_TITLE,
            blocks=images.duck_picture_blocks(content.DUCK_PICTURE_TITLE, picture),
        )
        _log_command(command, "ok" if posted else "dropped")

    @app.command("/purrbot-catify")
    def catify_command(ack, say, respond, command) -> None:
        ack()
        raw_text = command.get("text", "").strip()
        if not raw_text:
            respond(text=content.CATIFY_EMPTY_HINT)
            _log_command(command, "hint")
            return
        said = catify(raw_text)
        posted = pacing.post(
            say,
            command["channel_id"],
            text=f"<@{command['user_id']}> said {said}",
        )
        _log_command(command, "ok" if posted else "dropped")

    @app.command("/purrbot-httpcat")
    def httpcat(ack, say, respond, command) -> None:
        ack()
        raw_code = command.get("text", "").strip()
        if not raw_code:
            respond(text=content.HTTPCAT_MISSING_CODE)
            _log_command(command, "hint")
            return
        if not raw_code.isdigit():
            respond(text=content.HTTPCAT_NOT_A_NUMBER)
            _log_command(command, "hint")
            return
        code = int(raw_code)
        if code not in content.STATUS_CODES:
            respond(text=content.HTTPCAT_UNKNOWN_CODE)
            _log_command(command, "hint")
            return
        posted = pacing.post(say, command["channel_id"], blocks=images.status_picture_blocks(code))
        _log_command(command, "ok" if posted else "dropped")

    @app.command("/cat_gif")
    def cat_gif(ack, say, command) -> None:
        ack()
        posted = pacing.post(
            say,
            command["channel_id"],
            text=content.CAT_GIF_PICTURE_TITLE,
            blocks=images.cat_gif_picture_blocks(),
        )
        _log_command(command, "ok" if posted else "dropped")

    @app.command("/purrbot-cat-fact")
    def cat_fact(ack, say, command) -> None:
        ack()
        fact_text = _fresh_cat_fact_text()
        posted = pacing.post(
            say,
            command["channel_id"],
            text=fact_text,
            blocks=images.cat_fact_blocks(fact_text),
        )
        _log_command(command, "ok" if posted else "dropped")

    @app.action(content.CAT_FACT_BUTTON_ACTION_ID)
    def refresh_cat_fact(ack, respond, body) -> None:
        ack()
        fact_text = _fresh_cat_fact_text()
        respond(
            replace_original=True,
            text=fact_text,
            blocks=images.cat_fact_blocks(fact_text),
        )
        _log_action(body, "action_cat_fact")

    @app.command("/purrbot-button")
    def meow_button(ack, say, command) -> None:
        ack()
        posted = pacing.post(
            say,
            command["channel_id"],
            text=content.MEOW_BUTTON_LABEL,
            blocks=images.meow_button_blocks(),
        )
        _log_command(command, "ok" if posted else "dropped")

    @app.action(content.MEOW_BUTTON_ACTION_ID)
    def press_meow_button(ack, body, say) -> None:
        ack()
        message = body["message"]
        posted = pacing.post(
            say,
            body["channel"]["id"],
            text=random.choice(content.BUTTON_PHRASES),
            thread_ts=message.get("thread_ts") or message["ts"],
        )
        _log_action(body, "action_meow_button", "ok" if posted else "dropped")

    @app.command("/streak")
    def streak_command(ack, respond, command) -> None:
        ack()
        user = store.user(command["user_id"])
        if user is None or user["total_meows"] == 0:
            respond(text=content.STREAK_EMPTY)
            _log_command(command, "empty")
            return
        respond(
            text=content.STREAK_TEXT.format(
                current=user["current_streak"],
                longest=user["longest_streak"],
                total=user["total_meows"],
            )
        )
        _log_command(command)

    @app.command("/leaderboard")
    def leaderboard_command(ack, respond, command) -> None:
        ack()
        board = command.get("text", "").strip().lower() or "live"
        if board not in ("live", "fame"):
            respond(text=content.LEADERBOARD_BAD_BOARD)
            _log_command(command, "hint")
            return
        rows = store.top_current(10) if board == "live" else store.top_longest(10)
        if not rows:
            respond(text=content.LEADERBOARD_EMPTY)
            _log_command(command, "empty")
            return
        title = (
            content.LEADERBOARD_TITLE_LIVE if board == "live" else content.LEADERBOARD_TITLE_FAME
        )
        lines = []
        for index, row in enumerate(rows):
            medal = content.MEDALS[index] if index < len(content.MEDALS) else f"{index + 1}."
            count = row["current_streak"] if board == "live" else row["longest_streak"]
            lines.append(
                content.LEADERBOARD_LINE.format(
                    medal=medal,
                    user_id=row["user_id"],
                    count=count,
                )
            )
        blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": title}},
            {"type": "section", "text": {"type": "mrkdwn", "text": "\n".join(lines)}},
        ]
        respond(text=title, blocks=blocks)
        _log_command(command)

    @app.command("/purrbot-feud")
    def feud_command(ack, respond, command) -> None:
        ack()
        since = (datetime.now(UTC) - timedelta(days=7)).timestamp()
        feud = store.feud(since)
        cats = feud["cat"]["count"]
        ducks = feud["duck"]["count"]
        lines = [content.FEUD_TITLE, content.FEUD_TOTALS.format(cats=cats, ducks=ducks)]
        if cats == 0 and ducks == 0:
            lines.append(content.FEUD_EMPTY)
        elif cats == ducks:
            lines.append(content.FEUD_TIE)
        elif cats > ducks:
            lines.append(content.FEUD_CATS_WIN)
        else:
            lines.append(content.FEUD_DUCKS_WIN)
        for side, template in (
            ("cat", content.FEUD_CAT_CHANNEL),
            ("duck", content.FEUD_DUCK_CHANNEL),
        ):
            champion = feud[side]["top_channel"]
            if champion:
                lines.append(
                    template.format(
                        channel=_channel_label(store, champion),
                        count=feud[side]["top_channel_count"],
                    )
                )
        respond(text="\n".join(lines))
        _log_command(command)

    @app.command("/purrbot-help")
    def help_command(ack, respond, command) -> None:
        ack()
        _respond_plain(respond, content.HELP_TEXT)
        _log_command(command)

    @app.command("/purrbot-optout")
    def optout(ack, respond, command) -> None:
        ack()
        store.opt_out(command["user_id"])
        respond(text=content.OPTOUT_CONFIRM)
        _log_command(command)

    @app.command("/purrbot-optin")
    def optin(ack, respond, command) -> None:
        ack()
        store.opt_in(command["user_id"])
        respond(text=content.OPTIN_CONFIRM)
        _log_command(command)

    @app.command("/purrbot-shush")
    def shush_command(ack, respond, command) -> None:
        ack()
        raw_minutes = command.get("text", "").strip()
        if not raw_minutes:
            minutes = DEFAULT_SHUSH_MINUTES
        else:
            try:
                minutes = int(raw_minutes)
            except ValueError:
                respond(text=content.SHUSH_BAD_MINUTES)
                _log_command(command, "hint")
                return
        channel_id = command["channel_id"]
        if minutes == 0:
            store.clear_channel_shush(channel_id)
            respond(text=content.SHUSH_CANCELLED)
            _log_command(command, "unmuted")
            return
        until = store.set_channel_shush(channel_id, minutes)
        until_text = datetime.fromtimestamp(until).strftime("%H:%M")
        respond(text=content.SHUSH_CONFIRM.format(time=until_text))
        _log_command(command, "muted")

    @app.command("/purrbot-health")
    def health_command(ack, respond, command) -> None:
        ack()
        now = time.time()
        lines = [content.HEALTH_TITLE]
        for provider in (providers.cat_images, providers.duck_images):
            lines.append(
                content.HEALTH_LINE.format(
                    name=provider.name,
                    state=provider.breaker.state,
                    success=_age_text(provider.last_success, now),
                    failure=_age_text(provider.last_failure, now),
                )
            )
        _respond_plain(respond, "\n".join(lines))
        _log_command(command)
