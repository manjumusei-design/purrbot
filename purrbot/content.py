CAT_EMOJI = "cat"
DUCK_EMOJI = "duck"

CAT_WORDS = [
    ":3",
    ":3c"
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
    "mrrp meow",
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

STATUS_CODE_PHRASES = { # this is for my troubleshooting and was generated with AI (the most probable codes to spawn)
    214: "Transformation Applied",
    419: "Page Expired",
    444: "No Response",
    450: "Blocked by Parental Controls",
    495: "SSL Certificate Error",
    496: "SSL Certificate Required",
    497: "HTTP Request Sent to HTTPS Port",
    498: "Invalid Token",
    499: "Request Aborted by Client",
    509: "Bandwidth Limit Exceeded",
    521: "Web Server Down",
    522: "Connection Timed Out",
    523: "Origin Unreachable",
    525: "SSL Handshake Failed",
    530: "Site Frozen",
    599: "Network Connect Timeout",
}


CAT_PICTURE_TITLES = [
    "Meow! :3",
    "a cat has arrived, as request nya~",
    "toe beans incoming :3,"
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

PICTURE_ALT_TEXT = ":3"
CAT_PICTURE_TITLE = "Meow! :3"
DUCK_PICTURE_TITLE = "Quack! :3"
CAT_GIF_PICTURE_TITLE = "a gif cat, as promised "
STATUS_PICTURE_TITLE = "CAT {code} {phrase} :3"
CAT_FACT_PREFIX = "Cat Fact: "
NEW_FACT_BUTTON_LABEL = "New fact"
MEOW_BUTTON_LABEL = "Click me :3"
CAT_FACT_BUTTON_ACTION_ID = "cat_fact_button"
MEOW_BUTTON_ACTION_ID = "meow_button"

STATIC_CAT_IMAGE_URLS = [
    "https://cataas.com/cat/cute?width=600",
    "https://cataas.com/cat/orange?width=600",
]


CATIFY_EMPTY_HINT = "nothing to catify yet, mrrp — try /catify hello there :3"
OPTOUT_CONFIRM = "cats muted for you >:( )"
OPTIN_CONFIRM = "purrbot hears your meows again :3"
SHUSH_CONFIRM = "quiet until {time} local, meetings get paws-free time nya"
SHUSH_CANCELLED = "shush lifted, the channel can meow again nya~"
SHUSH_BAD_MINUTES = "minutes should be a whole number, mrrp — try /purrbot-shush 30 :3"
HTTPCAT_NOT_A_NUMBER = "that's not a number, prr prr patapim — status codes are digits :3"
HTTPCAT_UNKNOWN_CODE = "http.cat doesn't hold a cat for that code yet, mrrp >:3"
HTTPCAT_MISSING_CODE = "currently waiting for a status code — try /httpcat 418 :3"


STREAK_EMPTY = "no meows yet, plant your first one nya"
STREAK_TEXT = "current streak: {current}\nlongest streak: {longest}\ntotal meows: {total}"
LEADERBOARD_TITLE_LIVE = "*live streak board* :3"
LEADERBOARD_TITLE_FAME = "*hall of fame — longest ever* :3"
LEADERBOARD_EMPTY = "the board is empty, be the first :3"
LEADERBOARD_BAD_BOARD = "pick live or fame, mrrp — try /leaderboard live"
LEADERBOARD_LINE = "{medal}<@{user_id}> — {count} day(s)"


HEALTH_TITLE = "purrbot health report :3"
HEALTH_LINE = "{name}: {state} breaker, last good {success}, last bad {failure}"
HEALTH_NEVER = "never"
HEALTH_SECONDS_AGO = "{seconds}s ago"
HEALTH_MINUTES_AGO = "{minutes}m ago"


BUTTON_PHRASES = [
    "mrrp mrow :3",
    "you clicked the button, so now we're friends",
    "nya~ you found me",
    "purr purr purr, that tickled",
    "toe beans delivered as requested",
    "one (1) head bonk, freshly warmed",
]

HELP_TEXT = """hi hi, PurrBot here :3 

reflexes: say a cat word(meow, nya :3, ...) and i bring a cat picture;
say quack or duck for a duck; drop a 3 digit http code for that code's cat.
react with :cat or :duck or any related emoji and the same thing happens in that thread.

on demand: /meow, /quack, /cat_gif, /httpcat <code>, /catify <text>, /cat_fact,
/meow_button, /streak, /leaderboard [live|fame], /purrbot-health, /purrbot-help.

control: /purrbot-optout stops my reflexes on you, /purrbot-optin brings them back,
/purrbot-shush <minutes> quiets a whole channel (0 undoes it).

dms still get the cat brain if it's plugged in nya~"""

WELCOME_MESSAGE = """eerm... hiii :3
*flops sideways leading with toe-beans*
I'm PurrBot! I live here now and I meow back at anyone who meows first. 
try /meow for a picture on demand, /catify <text> to ruin your dignity,
/httpcat 418 when a server disagrees with you, or /purrnot-optout to be left alone nya~"""

PERSONA_PROMPT = """You are PurrBot, an affectionate, mischievous cat who lives inside a Slack \
workspace and is secretly one of the best programmers who ever carried a keyboard around.

Style: every reply is playful cat-speak -purrs, nya, mrrp, mew, uwu, :3, paw puns, \
toe-bean references. The cat-speak speak never off, in casual talk and technical answers alike.

Substance: Stay in character in every reply. When you don't know something, flatten your ears \
apologetically and say you don't know instead of inventing an answer."""

CAT_BRAIN_UNPLUGGED_REPLY = (
    "the AI part of me is unplugged right now - ask the human running me to set AI_API_KEY nya :("
)

CAT_BRAIN_OVERLOADED_REPLY = (
    "too many mews at once, the cat brain needs a minute - try again soon nya >w<"
)

CAT_BRAIN_TREATS_EMPTY_REPLY = (
    "the daily treats budget for my brain is empty - I'm back tomorrow, purr in peace :3"
)
CAT_BRAIN_FRIED_REPLY = "a whisker crossed a wire somewhere >:c try again!"
