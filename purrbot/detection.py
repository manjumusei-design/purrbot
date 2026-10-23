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

