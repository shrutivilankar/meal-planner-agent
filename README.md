# Meal Planner Agent

A Telegram bot that generates dinner recipes on demand. Members in the Telegram chat group can use it to query for dinner recipe ideas.

## How it works

Add the bot to a Telegram group, then send:

```
/generate
```

The bot replies with a generated dinner recipe as a document, so everyone in the group can see and use it. Recipes are also indexed into a local vector database so the agent can learn from them over time.

## Setup

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Create a `.env` file with your Telegram bot token and any other API keys:

```
TELEGRAM_BOT_TOKEN=your-token-here
```

Run the bot (also starts the FastAPI server on `localhost:8000`):

```bash
uv run python src/meal_planner_agent/app.py
```

## API

The app also exposes a simple HTTP endpoint:

- `POST /generate` — returns a generated list of dinner recipes.
