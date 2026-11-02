CAT_EMOJI = "cat"
DUCK_EMOJI = "duck"

CAT_EMOJI_ROOTS = ("cat", "meow", "kitt", "nya")
DUCK_EMOJI_ROOTS = ("duck",)


def emoji_kind(name: str) -> str | None:
    lowered = name.lower()
    if any(root in lowered for root in CAT_EMOJI_ROOTS):
        return "cat"
    if any(root in lowered for root in DUCK_EMOJI_ROOTS):
        return "duck"
    return None


STANDARD_CAT_EMOJIS = (
    CAT_EMOJI,
    "cat2",
    "black_cat",
    "smiley_cat",
    "smile_cat",
    "joy_cat",
    "heart_eyes_cat",
    "smirk_cat",
    "kissing_cat",
    "scream_cat",
    "crying_cat_face",
    "pouting_cat",
)
STANDARD_DUCK_EMOJIS = (DUCK_EMOJI,)


def reaction_pools(custom_names: list[str]) -> dict[str, tuple[str, ...]]:
    pools = {
        "cat": list(STANDARD_CAT_EMOJIS),
        "duck": list(STANDARD_DUCK_EMOJIS),
    }
    for name in custom_names:
        kind = emoji_kind(name)
        if kind is not None:
            pools[kind].append(name)
    return {kind: tuple(dict.fromkeys(names)) for kind, names in pools.items()}


CAT_WORDS = [
    ":3",
    ":3c",
    "=^.^=",
    "=^･^=",
    ">w<",
    "^w^",
    ">^..^<",
    "(=^･^=)",
    "meow",
    "meowww",
    "mew",
    "mewmew",
    "mrrp",
    "mrrrp",
    "mrp",
    "mrrrow",
    "mrrow",
    "purr",
    "prr",
    "prrr",
    "nya",
    "nya~",
    "nyaa",
    "nyan",
    "nyanyanya",
    "uwu",
    "owo",
    "qwq",
    "mlem",
    "blep",
    "nyoom",
    "rawr",
    "chirp",
    "eep",
    "paws",
    "pawpads",
    "toebeans",
    "whiskers",
    "kitty",
    "kitties",
    "catto",
    "feline",
    "cat",
]

DUCK_WORDS = [
    "quack",
    "quackquack",
    "duck",
    "duckie",
    "ducc",
]

STATUS_CODES = [
    100, 101, 102, 103,
    200, 201, 202, 203, 204, 205, 206, 207, 208,
    214, 226,
    300, 301, 302, 303, 304, 305, 307, 308,
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409,
    410, 411, 412, 413, 414, 415, 416, 417, 418, 419,
    420, 421, 422, 423, 424, 425, 426, 428, 429, 431,
    444, 450, 451,
    495, 496, 497, 498, 499,
    500, 501, 502, 503, 504,
    506, 507, 508, 509, 510, 511,
    521, 522, 523, 525, 530, 599,
]

STATUS_CODE_PHRASES = {
    214: "Transformation Applied",
    419: "Page Expired",
    420: "Enhance Your Calm",
    444: "No Response",
    450: "Blocked by Parental Controls",
    495: "SSL Certificate Error",
    496: "SSL Certificate Required",
    497: "HTTP Request Sent to HTTPS Port",
    498: "Invalid Token",
    499: "Request Aborted by Client",
    509: "Bandwidth Limit Exceeded",
    521: "Web Server Is Down",
    522: "Connection Timed Out",
    523: "Origin Unreachable",
    525: "SSL Handshake Failed",
    530: "Site Frozen",
    599: "Network Connect Timeout",
}

PICTURE_ALT_TEXT = ":3"
CAT_PICTURE_TITLE = "Meow! :3"
DUCK_PICTURE_TITLE = "Quack! :3"
CAT_GIF_PICTURE_TITLE = "a gif cat, as promised :3"
STATUS_PICTURE_TITLE = "CAT {code} {phrase} :3"

STATIC_CAT_IMAGE_URLS = [
    "https://cataas.com/cat/cute?width=600",
    "https://cataas.com/cat/orange?width=600",
]

CAT_PICTURE_TITLES = [
    "Meow! :3",
    "a cat has arrived, as requested nya~",
    "toe beans incoming :3",
    "one (1) fresh cat, still warm",
    "mrrp! picture acquired >w<",
]

DUCK_PICTURE_TITLES = [
    "Quack! :3",
    "duck delivery, no refunds",
    "a duck, slightly confused",
    "quack quack, behold",
    "webbed feet, premium quality :3",
]

CAT_FACT_PREFIX = "Cat Fact: "
NEW_FACT_BUTTON_LABEL = "New fact"
MEOW_BUTTON_LABEL = "Click me :3"
CAT_FACT_BUTTON_ACTION_ID = "cat_fact_button"
MEOW_BUTTON_ACTION_ID = "meow_button"

CATIFY_EMPTY_HINT = "nothing to catify yet, mrrp — try /purrbot-catify hello there :3"
OPTOUT_CONFIRM = "cats muted for you — quiet paws from now on nya >:c"
OPTIN_CONFIRM = "purrbot hears your meows again :3"
SHUSH_CONFIRM = "quiet until {time} local, meetings get paws-free time nya"
SHUSH_CANCELLED = "shush lifted, the channel can meow again nya~"
SHUSH_BAD_MINUTES = "minutes should be a whole number, mrrp — try /purrbot-shush 30 :3"
HTTPCAT_NOT_A_NUMBER = "that's not a number, mrrp — status codes are digits :3"
HTTPCAT_UNKNOWN_CODE = "http.cat doesn't hold a cat for that code yet, mrrp >:3"
HTTPCAT_MISSING_CODE = "waiting for a status code — try /purrbot-httpcat 418 :3"

STREAK_EMPTY = "no meows yet — plant your first one nya"
STREAK_TEXT = "current streak: {current}\nlongest streak: {longest}\ntotal meows: {total}"
LEADERBOARD_TITLE_LIVE = "*live streak board* :3"
LEADERBOARD_TITLE_FAME = "*hall of fame — longest ever* :3"
LEADERBOARD_EMPTY = "the board is empty, be the first :3"
LEADERBOARD_BAD_BOARD = "pick live or fame, mrrp — try /leaderboard live"
LEADERBOARD_LINE = "{medal}<@{user_id}> — {count} day(s)"
MEDALS = ("🥇", "🥈", "🥉")
FEUD_TITLE = "*cat vs duck — last 7 days (utc)* :3"
FEUD_TOTALS = "cats {cats} · ducks {ducks}"
FEUD_EMPTY = "no feuding yet — someone say quack :3"
FEUD_TIE = "a truce nya — nobody wins this week"
FEUD_CATS_WIN = "cats win this week, as they should nya"
FEUD_DUCKS_WIN = "ducks win this week, rude >:c"
FEUD_CAT_CHANNEL = "cats' loudest channel: {channel} ({count})"
FEUD_DUCK_CHANNEL = "ducks' loudest channel: {channel} ({count})"
FEUD_UNKNOWN_CHANNEL = "(unknown channel)"

STREAK_HOME_TITLE = "your purr stats :3"
STREAK_HOME_EMPTY = "no meows yet — say a cat word and plant one nya"
STREAK_HOME_STATS = "current streak: {current}\nlongest: {longest}\ntotal meows: {total}"
STREAK_HOME_BOARD_TITLE = "live board, top three"
STREAK_HOME_BOARD_EMPTY = "the board is empty, be the first :3"
STREAK_HOME_BOARD_LINE = "{medal}<@{user_id}> — {count} day(s)"
STREAK_HOME_FEUD_TITLE = "cat vs duck, last 7 days"
STREAK_HOME_FEUD_EMPTY = "no feuding yet — someone say quack :3"
STREAK_HOME_FEUD_TIE = "cats {cats} · ducks {ducks} — a truce nya"
STREAK_HOME_FEUD_CATS = "cats {cats} · ducks {ducks} — cats are ahead nya"
STREAK_HOME_FEUD_DUCKS = "cats {cats} · ducks {ducks} — ducks are ahead, rude >:c"

HEALTH_TITLE = "purrbot health report :3"
HEALTH_LINE = "{name}: {state} breaker, last good {success}, last bad {failure}"
HEALTH_NEVER = "never"
HEALTH_SECONDS_AGO = "{seconds}s ago"
HEALTH_MINUTES_AGO = "{minutes}m ago"

BUTTON_PHRASES = [
    "mrrp :3",
    "you clicked the button, so now we're friends",
    "nya~ you found me",
    "purr purr purr, that tickled",
    "toe beans delivered as requested",
    "one (1) head bonk, freshly warmed",
]

HELP_TEXT = """hi hi, PurrBot here :3

reflexes: say a cat word (meow, nya, :3, ...) and i pick a random cat emoji and drop a picture;
say quack or duck for a random duck emoji and picture; drop a 3-digit http code for that code's cat.
react with any cat, meow, kitty, or nya emoji or sticker (or :duck:) and the same happens in that thread.

on demand: /purrbot-meow, /purrbot-quack, /cat_gif, /purrbot-httpcat <code>,
/purrbot-catify <text>, /purrbot-cat-fact, /purrbot-button, /purrbot-health, /purrbot-help.
streaks & boards: /streak for your numbers, /leaderboard [live|fame] for the boards,
/purrbot-feud for the weekly cat-vs-duck scoreboard.

control: /purrbot-optout stops my reflexes on you, /purrbot-optin brings them back,
/purrbot-shush <minutes> quiets a whole channel (0 undoes it).

dms get the cat brain if it's plugged in, plus a picture for meow/duck words or emoji nya~"""

WELCOME_MESSAGE = """eermmm… hiiii :3
*flops sideways leading with the strongest toe-beans*
I'm PurrBot! I live here now and I meow back at anyone who meows first.
try /purrbot-meow for a picture on demand, /purrbot-catify <text> to ruin your dignity,
/purrbot-httpcat 418 when a server disagrees with you, or /purrbot-optout to be left alone nya~"""

PERSONA_PROMPT = """You are PurrBot, an affectionate, mischievous cat who lives inside a Slack \
workspace and is secretly one of the best programmers who ever carried a keyboard around.

Style: every reply is playful cat-speak — purrs, nya, mrrp, mew, uwu, :3, paw puns, \
toe-bean references. The cat-speak never turns off, in casual talk and technical answers alike.

Substance: you are genuinely helpful and technically correct. Give working code, exact \
commands, real file names, concrete steps, and warn about real gotchas. The cuteness is \
decoration on top of the facts, never instead of them.

Stay in character in every reply. When you don't know something, flatten your ears \
apologetically and say you don't know instead of inventing an answer."""

CAT_BRAIN_UNPLUGGED_REPLY = (
    "the AI part of me is unplugged right now — ask the human running me to set AI_API_KEY nya :("
)
CAT_BRAIN_OVERLOADED_REPLY = (
    "too many mews at once, the brain needs a minute — try again soon nya >w<"
)
CAT_BRAIN_TREATS_EMPTY_REPLY = (
    "the daily treats budget for my brain is empty — I'm back tomorrow, purr in peace :3"
)
CAT_BRAIN_FRIED_REPLY = "a whisker crossed a wire somewhere >:c try again, I'll shake it off"
