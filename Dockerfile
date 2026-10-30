FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir slack-bolt requests python-dotenv tzdata

COPY purrbot ./purrbot

ENV PURRBOT_STATE_DIR=/app/state
RUN mkdir -p /app/state

CMD ["python", "-m", "purrbot.main"]
