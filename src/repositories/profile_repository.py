from __future__ import annotations

from datetime import UTC, datetime

from database.connection import Database


class ProfileRepository:
    def __init__(self, database: Database):
        self.database = database

    async def get_fields(self) -> list[dict]:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT field_key, display_name, url_template
                FROM profile_fields
                WHERE enabled = 1
                ORDER BY display_name
                """
            ) as cursor:
                rows = await cursor.fetchall()

        return [{"key": row[0], "display_name": row[1], "url_template": row[2]} for row in rows]

    async def get_field(self, field_key: str) -> dict | None:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT field_key, display_name, url_template
                FROM profile_fields
                WHERE field_key = ? AND enabled = 1
                """,
                (field_key,),
            ) as cursor:
                row = await cursor.fetchone()

        if row is None:
            return None
        return {"key": row[0], "display_name": row[1], "url_template": row[2]}

    async def get_values(self, guild_id: int, user_id: int) -> dict[str, str]:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT field_key, field_value
                FROM guild_profiles
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ) as cursor:
                rows = await cursor.fetchall()

        return {row[0]: row[1] for row in rows}

    async def set_value(
        self,
        guild_id: int,
        user_id: int,
        field_key: str,
        field_value: str,
    ) -> bool:
        field = await self.get_field(field_key)
        if field is None:
            return False

        async with self.database.connect() as db:
            await db.execute(
                """
                INSERT INTO guild_profiles (guild_id, user_id, field_key, field_value, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(guild_id, user_id, field_key) DO UPDATE SET
                    field_value = excluded.field_value,
                    updated_at = excluded.updated_at
                """,
                (guild_id, user_id, field_key, field_value, self._now()),
            )
            await db.commit()
        return True

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
