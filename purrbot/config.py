import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
APP_TOKEN = os.environ.get("APP_TOKEN")

AI_API_KEY = os.environ.get("AI_API_KEY")
AI_MODEL = os.environ.get("AI_MODEL", "qwen/qwen3-32b")
AI_URL = os.environ.get("AI_URL", "https://ai.hackclub.com/proxy/v1")
AI_CONTEXT_MESSAGE_LIMIT = 10
AI_TIMEOUT_SECONDS = 30
