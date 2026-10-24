import re

_CATIFYING_RULES = [
    (re.compile(r"[rl]"), "w"),
    (re.compile(r"na"), "nya"),
    (re.compile(r"th"), "d"),
]
_EXCLAIMATION_RUN = re.compile(r"!+")
_QUESTION_RUN = re.compile(r"\?+")
_EXCLAMATION_REPLACEMENT = " nya! >w<"
_QUESTION_REPLACEMENT = " nyaaaa?"
_CAT_LIKE_FINISH = re.compile(r"nya|mew|meow|uwu|owo|purr")
_DEFAULT_FINISH = "nya~"


def catify(text: str) -> str:
    catified = text.lower()
    for pattern, replacement in _CATIFYING_RULES:
        catified = pattern.sub(replacement, catified)
    catified = _EXCLAIMATION_RUN.sub(_EXCLAMATION_REPLACEMENT, catified)
    catified = _QUESTION_RUN.sub(_QUESTION_REPLACEMENT, catified)
    if not _CAT_LIKE_FINISH.search(catified):
        catified = catified + _DEFAULT_FINISH
    return catified