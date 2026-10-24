import requests

from purrbot import config, content

TREATS_EMPTY_STATUS = 402
RATE_LIMITED_STATUS = 429

class CatPersona:
    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self.model = model
        self.completions_url = base_url.rstrip("/") + "/chat/completions"
        self.headers = {
            "Authorization": f"Bearer{api_key}",
            "Content-Type": "application/json",
        }


    def reply(self, chat_messages: list[dict]) -> str:
        body = {
            "model": self.model,
            "stream": False,
            "messages": [{"role": "system", "content": content.PERSONA_PROMPT}, *chat_messages],
        }
        try:
            response = requests.post(
                self.completions_url,
                headers=self.headers,
                json=body,
                timeout=config.AI_TIMEOUT_SECONDS,
            )
            if response.status_code == TREATS_EMPTY_STATUS:
                return content.CAT_BRAIN_TREATS_EMPTY_REPLY
            if response.status_code == RATE_LIMITED_STATUS:
                return content.CAT_BRAIN_OVERLOADED_REPLY
            return response.json()["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
            return content.CAT_BRAIN_FRIED_REPLY