# Development Workflow

## Branches

Recommended flow:

1. `feature/*`: isolated changes.
2. `dev`: tested with the development bot and private test server.
3. `staging`: release candidate using staging environment variables.
4. `main`: production.

Keep `main` deployable. Merge forward through `dev -> staging -> main`.

## Environments

Use one codebase and separate `.env` files or host-level secrets.

Development example:

```env
MIKI_ENV=development
DISCORD_TOKEN=development_bot_token
DATABASE_PATH=data/miki-dev.db
```

Staging example:

```env
MIKI_ENV=staging
DISCORD_TOKEN=staging_bot_token
DATABASE_PATH=data/miki-staging.db
```

Production example:

```env
MIKI_ENV=production
DISCORD_TOKEN=production_bot_token
DATABASE_PATH=/app/data/miki.db
```

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest==8.4.0 pytest-asyncio==1.0.0 ruff==0.11.13
cp .env.example .env
python src/bot.py
```

## Checks

Run before opening or merging a PR:

```bash
ruff check .
ruff format --check .
pytest
```

Use `ruff format .` when formatting changes are needed.

## Docker

Production-style local run:

```bash
docker compose up -d --build
docker compose logs -f miki-bot
docker compose down
```

The container stores SQLite data in the `miki-data` volume at `/app/data/miki.db`.

## Deployment

Keep deployment simple:

1. Merge to the target branch.
2. Pull the branch on the server.
3. Update environment secrets outside git.
4. Rebuild and restart with Docker Compose.
5. Check logs after startup.
