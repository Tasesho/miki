from __future__ import annotations

from datetime import UTC, datetime

from database.connection import Database


class GuildRepository:
    def __init__(self, database: Database):
        self.database = database

    async def get_setting(self, guild_id: int, key: str) -> str | None:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT setting_value
                FROM guild_settings
                WHERE guild_id = ? AND setting_key = ?
                """,
                (guild_id, key),
            ) as cursor:
                row = await cursor.fetchone()
        return row[0] if row else None

    async def set_setting(self, guild_id: int, key: str, value: str) -> None:
        async with self.database.connect() as db:
            await db.execute(
                """
                INSERT INTO guild_settings (guild_id, setting_key, setting_value, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id, setting_key) DO UPDATE SET
                    setting_value = excluded.setting_value,
                    updated_at = excluded.updated_at
                """,
                (guild_id, key, str(value), self._now()),
            )
            await db.commit()

    async def is_module_enabled(self, guild_id: int, module_key: str) -> bool:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT enabled
                FROM guild_modules
                WHERE guild_id = ? AND module_key = ?
                """,
                (guild_id, module_key),
            ) as cursor:
                row = await cursor.fetchone()
        return True if row is None else bool(row[0])

    async def set_module_enabled(
        self,
        guild_id: int,
        module_key: str,
        enabled: bool,
    ) -> None:
        async with self.database.connect() as db:
            await db.execute(
                """
                INSERT INTO guild_modules (guild_id, module_key, enabled, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id, module_key) DO UPDATE SET
                    enabled = excluded.enabled,
                    updated_at = excluded.updated_at
                """,
                (guild_id, module_key, int(enabled), self._now()),
            )
            await db.commit()

    async def get_triggers(self, guild_id: int) -> dict[str, str]:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT trigger_key, response
                FROM guild_triggers
                WHERE guild_id = ? AND enabled = 1
                """,
                (guild_id,),
            ) as cursor:
                rows = await cursor.fetchall()
        return {row[0]: row[1] for row in rows}

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
