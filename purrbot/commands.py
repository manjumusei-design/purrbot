import random
from datetime import datetime

from purrbot import content, images
from purrbot.catify import catify
from purrbot.optout import OptOutStore
from purrbot.shush import DEFAULT_SHUSH_MINUTES, ShushStore

def _fresh_cat_fact_text() -> str:
    return content.CAT_FACT_PREFIX + images.fetch_cat_fact()

def register(app, store: OptOutStore, shush: ShushStore) -> None:
    @app.command("/meow")
    def meow(ack, say) -> None:
        ack()
        say(text=content.CAT_PICTURE_TITLE,  blocks=images.cat_picture_blocks(content.CAT_PICTURE_TITLE))

    @app.command("/quack")
    def quack(ack, say) -> None:
        say(text=content.DUCK_PICTURE_TITLE, blocks=images.duck_picture_blocks(content.DUCK_PICTURE_TITLE))

    @app.command("/catify")
    def catify_command(ack, say, respond, command) -> None:
        ack()
        raw_text = command.get("text", "").strip()
        if not raw_text:
            respond(text=content.CATIFY_EMPTY_HINT)
            return
        said = catify(raw_text)
        say(text=f"<@{command['user_id']}> said {said}", mrkdwn=False)

    @app.command("/httpcat")
    def httpcat(ack, say, respond, command) -> None:
        ack()
        raw_code = command.get("text", "").strip()
        if not raw_code:
            respond(text=content.HTTPCAT_MISSING_CODE)
            return
        if not raw_code.isdigit():
            respond(text=content.HTTPCAT_NOT_A_NUMBER)
            return
        code = int(raw_code)
        if code not in content.STATUS_CODES:
            respond(text=content.HTTPCAT_UNKNOWN_CODE)
            return
        say(blocks=images.status_picture_blocks(code))

    @app.command("/cat_gif")
    def cat_gif(ack, say) -> None:
        ack()
        say(text=content.CAT_GIF_PICTURE_TITLE, blocks=images.cat_gif_picture_blocks())


    @app.command("/cat_fact")
    def cat_fact(ack, say) -> None:
        ack()
        fact_text = _fresh_cat_fact_text()
        say(text=fact_text, blocks=images.cat_fact_blocks(fact_text))

    @app.action(content.CAT_FACT_BUTTON_ACTION_ID)
    def refresh_cat_fact(ack, respond) -> None:
        ack()
        fact_text = _fresh_cat_fact_text()
        respond(
            replace_original=True,
            text=fact_text,
            blocks=images.cat_fact_blocks(fact_text),
        )

    @app.command("/meow_button")
    def meow_button(ack, say) -> None:
        ack()
        say(text=content.MEOW_BUTTON_LABEL, blocks=images.meow_button_blocks())

    @app.action(content.MEOW_BUTTON_ACTION_ID)
    def press_meow_button(ack, body, say) -> None:
        ack()
        message = body["message"]
        say(
            text=random.choice(content.BUTTON_PHRASES),
            thread_ts=message.get("thread_ts") or message["ts"],
            mrkdwn=False,
        )

    @app.command(:/purrbot-help)
    def help_command(ack, respond) -> None:
        ack()
        respond(text=content.HELP_TEXT, mrkdwn = False)

    @app.command("/purrbot-optout")
    def optout(ack, respond, command) -> None:
        ack()
        store.add(command["user_id"])
        respond(text=content.OPTOUT_CONFIRM)

    @app.command("/purrbot-optin")
    def optin(ack, respond, command) -> None:
        ack()
        store.remove(command["user_id"])
        respond(text=content.OPTIN_CONFIRM)



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
                return
        channel_id = command["channel_id"]
        if minutes == 0:
            shush.unmute(channel_id)
            respond(text=content.SHUSH_BAD_MINUTES)
            return
        until = shush.mute(channel_id, minutes)
        until_text = datetime.fromtimestamp(until).strftime("%H:%M")
        respond(text=content.SHUSH_CONFIRM.format(time=until_text))