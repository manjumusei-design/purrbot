# Purrbot

This is a cat themed slack bot that reacts to cat speak/terms with cat pictures, to duck speak with duck pictures and can function as a chatbot (limited by HCAI).

# Features

- Cat reactions - A message containing any cat-like word in the list such as 'meow', 'mrrp' 'nya' etc will get a random cat emoji reaction and a random cat picture threaded under it.

- Duck reflex - 'Quack', 'duck', 'duckie' etc, same treatment as Cat reactions where it gets a random duck picture threaded under the comment.

- Reaction reflex - Any emoji in the list, when you react it to a message will get a random related emoji.

- Picture titles rotate - Cat and duck pictures will never get the same caption line in a row.

- Failover - Image fetches go through a provider circuit breaker for failover

- Streaks - Cat and status-code meows build a streak in Slack 

- Leaderboards - The live board and contains the hall of fame and lists the top 10 with medals (emojis ofc) for the first three.

- Feud - '/purbot-feud' is a rolling seven day cat vs duck scoreboard with both sides battling it out

- Pacing - To avoid reflex storms under slacks per channel reply so spam cant overload endpoints

- Cat gifs - 'cat_gif' posts an animated gif from cataas

- There are also /help commands, '/purrbot-optout or /purrbot-optin', as well as shushing the bot for x amounf of minutes

- DM persona - Text the bot privately to find out :3 



## setup

1. create the Slack app at api.slack.com/apps, then paste `manifest.yaml` into
   **Settings → App Manifest** and save — it carries all 15 slash commands, the home tab,
   and the `users:read` scope
2. **Basic Information → App-Level Tokens**: generate one with the `connections:write`
   scope — that value is `APP_TOKEN`
3. **OAuth & Permissions → Install to Workspace** — the `xoxb-…` value is `BOT_TOKEN
4. `/invite @PurrBot` into a test channel

## run

with uv:

```bash
uv sync
uv run python -m purrbot.main
```

without uv:

```bash
python3 -m venv .venv
.venv/bin/pip install slack-bolt requests python-dotenv tzdata fastapi uvicorn httpx pytest ruff
.venv/bin/python -m purrbot.main
```

or with the compose file:

```bash
docker compose build
docker compose up -d
```

The full VPS runbook, state-volume notes, and update flow live in [DEPLOY.md](DEPLOY.md).

## environment

`.env` in the repo root (don't have one? copy `.env.example`):

| variable | meaning |
|---|---|
| `BOT_TOKEN` | the `xoxb-…` bot user token |
| `APP_TOKEN` | the `xapp-…` socket mode app token |
| `AI_API_KEY` | optional; without it DMs answer "the brain is unplugged". any OpenAI-compatible key works |
| `AI_MODEL` | model id for the persona, default `qwen/qwen3-32b` |
| `AI_URL` | OpenAI-compatible base url, default `https://ai.hackclub.com/proxy/v1` |
| `PURRBOT_STATE_DIR` | where the sqlite db, memory, and event files live, default `.`; the container sets `/app/state` |
| `PURRBOT_DEBUG` | optional; `1` logs raw slack socket frames to the compose logs — the frame catcher |