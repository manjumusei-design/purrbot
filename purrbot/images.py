import http

import requests

from purrbot import content
from purrbot.providers import Picture

CAT_GIF_DISCOVERY_URL = "https://cataas.com/cat/gif?json=true"
CAT_FACT_URL = "https://catfact.ninja/fact"
STATUS_IMAGE_URL_FORMAT = "https://http.cat/{code}"
HTTP_TIMEOUT_SECONDS = 10


def status_code_phrase(code: int) -> str:
    known_phrase = content.STATUS_CODE_PHRASES.get(code)
    if known_phrase is not None:
        return known_phrase
    return http.HTTPStatus(code).phrase

def _picture_blocks(title: str, image_url: str) -> list[dict]:
    return [
        {
            "type": "image",
            "title": {"type": "plain_text", "text": title},
            "image_url": image_url,
            "alt_text": content.PICTURE_ALT_TEXT,
        }
    ]

def cat_picture_blocks(title: str, picture: Picture) -> list[dict]:
    return _picture_blocks(title, picture.url)


def cat_gif_picture_blocks() -> list[dict]:
    discovery = requests.get(CAT_GIF_DISCOVERY_URL, timeout=HTTP_TIMEOUT_SECONDS)
    return _picture_blocks(content.CAT_GIF_PICTURE_TITLE, discovery.json()["url"])


def duck_picture_blocks(title: str, picture: Picture) -> list[dict]:
    return _picture_blocks(title, picture.url)

def status_picture_title(code: int) -> str:
    return content.STATUS_PICTURE_TITLE.format(code=code, phrase=status_code_phrase(code))

def status_picture_blocks(code: int) -> list[dict]:
    image_url = STATUS_IMAGE_URL_FORMAT.format(code=code)
    return _picture_blocks(status_picture_title(code), image_url)


def cat_fact_blocks(fact_text: str) -> list[dict]:
    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": fact_text},
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": content.NEW_FACT_BUTTON_LABEL},
                "action_id": content.CAT_FACT_BUTTON_ACTION_ID,
            },
        }
    ]


def meow_button_blocks() -> list[dict]:
    return [
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": content.MEOW_BUTTON_LABEL},
                    "action_id": content.MEOW_BUTTON_ACTION_ID,
                }
            ],
        }
    ]


def fetch_cat_fact() -> str:
    response = requests.get(CAT_FACT_URL, timeout=HTTP_TIMEOUT_SECONDS)
    return response.json()["fact"]