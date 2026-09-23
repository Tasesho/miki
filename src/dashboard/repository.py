from __future__ import annotations

from pathlib import Path

import asyncpg

from dashboard.welcome_cards import WelcomeCardSettings


class PostgresWelcomeCardRepository:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=5)

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def migrate(self) -> None:
        migrations_dir = Path(__file__).parents[1] / "database" / "migrations" / "postgresql"
        async with self._pool().acquire() as connection:
            await connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
            )
            for path in sorted(migrations_dir.glob("*.sql")):
                applied = await connection.fetchval(
                    "SELECT 1 FROM schema_migrations WHERE version = $1", path.stem
                )
                if applied:
                    continue
                async with connection.transaction():
                    await connection.execute(path.read_text(encoding="utf-8"))
                    await connection.execute(
                        "INSERT INTO schema_migrations (version) VALUES ($1)", path.stem
                    )

    async def get(self, guild_id: int) -> WelcomeCardSettings:
        row = await self._pool().fetchrow(
            "SELECT enabled, channel_id, title, message, extra_message, background_url, accent_color, text_color, show_avatar, show_member_count FROM guild_welcome_cards WHERE guild_id = $1",
            guild_id,
        )
        return WelcomeCardSettings() if row is None else WelcomeCardSettings(**dict(row))

    async def save(self, guild_id: int, settings: WelcomeCardSettings) -> WelcomeCardSettings:
        await self._pool().execute(
            """INSERT INTO guild_welcome_cards (guild_id, enabled, channel_id, title, message, extra_message, background_url, accent_color, text_color, show_avatar, show_member_count) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) ON CONFLICT (guild_id) DO UPDATE SET enabled = EXCLUDED.enabled, channel_id = EXCLUDED.channel_id, title = EXCLUDED.title, message = EXCLUDED.message, extra_message = EXCLUDED.extra_message, background_url = EXCLUDED.background_url, accent_color = EXCLUDED.accent_color, text_color = EXCLUDED.text_color, show_avatar = EXCLUDED.show_avatar, show_member_count = EXCLUDED.show_member_count, updated_at = NOW()""",
            guild_id,
            settings.enabled,
            settings.channel_id,
            settings.title,
            settings.message,
            settings.extra_message,
            settings.background_url,
            settings.accent_color,
            settings.text_color,
            settings.show_avatar,
            settings.show_member_count,
        )
        return await self.get(guild_id)

    def _pool(self) -> asyncpg.Pool:
        if self.pool is None:
            raise RuntimeError("PostgreSQL repository is not connected.")
        return self.pool
