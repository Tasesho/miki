# Miki Discord Bot

Miki is a Python Discord bot built with `discord.py`, SQLite, and Docker. The project uses modular Cogs, a shared service layer, repositories for data access, and environment-based configuration for development, staging, and production.

Current release: **Coffee Update — Inventario y Café Suelto**

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
SOCIAL_LINK_BASE_XP=100
SOCIAL_LINK_REACTION_XP=1
COFFEE_EVENT_DURATION_SECONDS=30
COFFEE_EVENT_MIN_WAIT_HOURS=1
COFFEE_EVENT_CHANCE_DENOMINATOR=5
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

## Welcome-card dashboard (foundation)

The dashboard is a local-only web service backed by PostgreSQL. It currently has no
Discord authentication, so do not expose it to the internet. Start it with:

```bash
docker compose up -d postgres miki-dashboard
```

Open `http://127.0.0.1:8081`, enter a Discord server ID, then edit and save its
welcome-card settings. The dashboard applies the PostgreSQL migrations automatically.
For delivery to work, enable **Server Members Intent** for Miki in the Discord
Developer Portal, then rebuild the bot after saving a card:

```bash
docker compose up -d --build miki-bot
```

Miki must have **View Channel**, **Send Messages**, and **Attach Files** in the
configured welcome channel. Available template variables are `{user}` and `{server}`.
The dashboard's **Send test card** button sends through Miki itself and reports the
request/result in `docker compose logs -f miki-bot`. Set a long, matching
`INTERNAL_API_TOKEN` in `.env` before exposing this stack beyond local development.
You can confirm a saved card directly in the database:

```bash
docker compose exec postgres psql -U miki -d miki -c "SELECT guild_id, enabled, channel_id, title, updated_at FROM guild_welcome_cards;"
```

Run the real PostgreSQL persistence test against the Compose database with:

```bash
TEST_POSTGRES_DATABASE_URL=postgresql://miki:replace_with_a_long_secret@127.0.0.1:5432/miki pytest tests/test_welcome_cards_postgres.py
```

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
- [Social Links](docs/SOCIAL_LINKS.md)
- [Development Workflow](docs/WORKFLOW.md)

## Current Commands

Miki currently provides slash commands for profile, weather, GIF search, leaderboard,
configuration, Social Links, information, moderation cleanup, word history, and
utility features. See [Social Links](docs/SOCIAL_LINKS.md) for the relationship rules
and commands.

Social Link commands:

```text
/social-link view
/social-link view user:@member
/social-link list
/info social-link
/config social-link experiencia:10   # Admin only
```

## Coffee Update

Miki incluye un sistema de consumibles y eventos comunitarios llamado **Café
Suelto**. Los consumibles se guardan por servidor y usuario, por lo que no se
mezclan entre servidores ni se pierden al reiniciar el bot.

### Café Suelto

El evento utiliza el canal general configurado mediante `/setup start`.

1. Miki espera el cooldown mínimo configurado, una hora por defecto.
2. Después realiza una sola tirada por minuto.
3. Con el valor predeterminado, la probabilidad es `1/5` por minuto.
4. Miki publica un mensaje con la reacción `☕` ya añadida.
5. El primer usuario que reaccione con `☕` gana un consumible.
6. El mensaje se elimina automáticamente al terminar su duración.

La reacción de Miki no cuenta como participación y las reacciones con otros
emojis se ignoran. Un lock por servidor evita que dos usuarios ganen el mismo
evento.

### Inventario y comandos

```text
/cafe inventario
/cafe usar
/cafe regalar usuario:@usuario
```

- `/cafe inventario` muestra los consumibles disponibles y la afinidad con Miki.
- `/cafe usar` consume un objeto y otorga `50 XP` globales.
- `/cafe regalar` entrega un objeto a otro usuario, otorga `+1` Social Link y
  entrega `100 XP` al usuario que hace el regalo.
- Regalarle un objeto a Miki aumenta la afinidad con Miki, pero no otorga XP global.
- No se permiten regalos a uno mismo ni a otros bots.

### Configuración desde Discord

Los administradores pueden ejecutar:

```text
/setup cafe
```

El panel permite configurar por servidor:

- Horas de espera mínima antes de volver a intentar un evento.
- Duración del mensaje del evento en segundos.
- Probabilidad `1/N` por minuto después del cooldown.
- XP otorgada por regalar un consumible a otro usuario.

Los valores iniciales del entorno son:

```env
COFFEE_EVENT_DURATION_SECONDS=30
COFFEE_EVENT_MIN_WAIT_HOURS=1
COFFEE_EVENT_CHANCE_DENOMINATOR=5
```

Para pruebas, el entorno local puede usar una duración menor, como `10` segundos.
