import re

from purrbot import content

_TOKEN_PUNCTUATION = ".,!?;:'\"()[]{}…<>_*~"

_CAT_WORDS = set(content.CAT_WORDS)
_DUCK_WORDS = set(content.DUCK_WORDS)
_STATUS_CODES = set(content.STATUS_CODES)
_STATUS_CODE_PATTERN = re.compile(r"\b(\d{3})\b")


def _normalized_tokens(text: str) -> list[str]:
    tokens = []
    for token in text.lower().split():
        tokens.append(token)
        stripped = token.strip(_TOKEN_PUNCTUATION)
        if stripped != token:
            tokens.append(stripped)
    return tokens

def cat_word_in(text: str) -> bool:
    return any(token in _CAT_WORDS for token in _normalized_tokens(text))



def duck_word_in(text: str) -> bool:
    return any(token in _DUCK_WORDS for token in _normalized_tokens(text))


def status_code_in(text: str) -> int | None:
    for raw_code in _STATUS_CODE_PATTERN.findall(text):
        code = int(raw_code)
        if code in _STATUS_CODES:
            return code
    return None