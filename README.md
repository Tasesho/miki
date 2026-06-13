# Miki Discord Bot

Miki is a Python Discord bot built with `discord.py`, SQLite, and Docker. The project uses modular Cogs, a shared service layer, repositories for data access, and environment-based configuration for development, staging, and production.

## Requirements

- Python 3.11+
- Docker and Docker Compose for container deployment
- A Discord bot token

## Configuration

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Runtime environment variables:

```env
MIKI_ENV=development
DISCORD_TOKEN=your_discord_bot_token
DATABASE_PATH=data/miki-dev.db
COMMAND_PREFIX=!
LOG_LEVEL=INFO
WEATHER_API_KEY=
GIPHY_API_KEY=
```

`MIKI_ENV` supports `development`, `staging`, and `production`. The same codebase is used for all environments.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest==8.4.0 pytest-asyncio==1.0.0 ruff==0.11.13
python src/bot.py
```

## Docker

```bash
docker compose up -d --build
docker compose logs -f miki-bot
docker compose down
```

Docker stores runtime data in the `miki-data` volume at `/app/data/miki.db`.

## Quality Checks

```bash
ruff check .
ruff format --check .
pytest
```

## Architecture

```text
src/
├── app.py                     # Application container and dependency wiring
├── bot.py                     # Discord entrypoint
├── config.py                  # Environment configuration
├── database/                  # SQLite connection and migrations
├── modules/                   # Discord Cogs
├── repositories/              # Data access layer
├── services/                  # Reusable business logic
└── setup/                     # Future interactive setup foundations
```

Further documentation:

- [Architecture](docs/ARCHITECTURE.md)
- [Development Workflow](docs/WORKFLOW.md)

## Current Commands

Miki currently keeps the existing prefix commands, including profile, weather, GIF search, leaderboard, configuration, moderation cleanup, word history, and utility commands. This refactor does not add new user-facing features.
