# Miki Architecture

Miki uses one codebase for development, staging, and production. Runtime behavior changes through environment variables, not duplicated project folders.

## Layers

- `src/bot.py`: Discord process entrypoint. It creates the application container, runs startup, and loads Cogs.
- `src/app.py`: dependency container. It wires settings, database, repositories, services, and external clients.
- `src/config.py`: centralized environment loading and validation.
- `src/modules/`: Discord Cogs. These should stay thin and handle Discord-specific input/output only.
- `src/services/`: business logic reusable by Discord and a future dashboard.
- `src/repositories/`: data access boundaries. SQL belongs here, not in commands.
- `src/database/`: SQLite connection and migration runner.
- `src/setup/`: future interactive setup flow primitives. No setup command is registered yet.

The SQLite connection exposes the project's async database interface through a
small `sqlite3` facade. This keeps repository APIs asynchronous while avoiding the
Python 3.14 `aiosqlite` worker/future issue observed in the development runtime.

## Configuration

Required for runtime:

- `DISCORD_TOKEN`

Common optional values:

- `MIKI_ENV`: `development`, `staging`, or `production`.
- `DATABASE_PATH`: defaults to `data/miki.db`.
- `COMMAND_PREFIX`: defaults to `!`.
- `LOG_LEVEL`: defaults to `INFO`.
- `WEATHER_API_KEY`
- `GIPHY_API_KEY`

`TOKEN` is still accepted as a temporary compatibility fallback, but `DISCORD_TOKEN` is the standard name.

## Database

SQLite remains the runtime database. The connection uses:

- foreign keys enabled
- WAL journal mode
- busy timeout
- configurable database path

Migrations live in `src/database/migrations/sqlite/` and are tracked in `schema_migrations`. PostgreSQL migration files remain separate under `src/database/migrations/postgresql/`.

## Guild Foundation

The schema contains foundations for:

- `guild_settings`: guild-scoped configuration values
- `guild_modules`: future per-guild module toggles
- `guild_setup_state`: future interactive setup state
- `guild_members`, `guild_profiles`, `guild_triggers`: existing guild-scoped bot data
- `social_links`, `social_link_interactions`: directed Social Link progress and action history

No new user-facing setup or module-toggle feature is exposed yet.

## Social Links

Social Links are implemented as a separate subsystem over the shared SQLite
database. Relationships are directed and guild-scoped:

```text
guild_id + source_user_id + target_user_id
```

The `social_links` table stores current XP and rank. The
`social_link_interactions` table records message-based rewards and makes repeated
reactions, replies, and mentions idempotent. The public commands live in the
`SocialLinks` Cog; configuration is exposed through the admin `config` group.

Detailed rules and user-facing commands are documented in
[Social Links](SOCIAL_LINKS.md).

## Dashboard Readiness

A future web dashboard should import and reuse services from `src/services/` and repositories from `src/repositories/`. It should not duplicate command logic from `src/modules/`.
