import re

from purrbot import content

_BRACKETS = "()[]{}"
_WORD_PUNCTUATION = ".,!?;:'\"…"
_EDGE_NOISE = _BRACKETS + _WORD_PUNCTUATION

_CAT_WORDS = set(content.CAT_WORDS)
_DUCK_WORDS = set(content.DUCK_WORDS)
_STATUS_CODES = set(content.STATUS_CODES)
_STATUS_CODE_PATTERN = re.compile(r"\b(\d{3})\b")


def _token_variants(token: str) -> list[str]:
    return [
        token,
        token.strip(_WORD_PUNCTUATION),
        token.strip(_BRACKETS),
        token.strip(_EDGE_NOISE),
    ]


def _matches(text: str, words: set[str]) -> bool:
    return any(variant in words for token in text.lower().split() for variant in _token_variants(token))


def cat_word_in(text: str) -> bool:
    return _matches(text, _CAT_WORDS)


def duck_word_in(text: str) -> bool:
    return _matches(text, _DUCK_WORDS)


def status_code_in(text: str) -> int | None:
    for raw_code in _STATUS_CODE_PATTERN.findall(text):
        code = int(raw_code)
        if code in _STATUS_CODES:
            return code
    return None
