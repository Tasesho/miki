from __future__ import annotations

from datetime import UTC, datetime

from database.connection import Database


class UserRepository:
    def __init__(self, database: Database):
        self.database = database

    async def ensure_user(self, user_id: int, username: str) -> None:
        now = self._now()
        async with self.database.connect() as db:
            await db.execute(
                """
                INSERT INTO users (user_id, username, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    updated_at = excluded.updated_at
                """,
                (user_id, username, now, now),
            )
            await db.commit()

    async def ensure_guild_member(self, guild_id: int, user_id: int, username: str) -> None:
        now = self._now()
        await self.ensure_user(user_id, username)
        async with self.database.connect() as db:
            await db.execute(
                """
                INSERT INTO guild_members (guild_id, user_id, username, registered_at, xp, nivel)
                VALUES (?, ?, ?, ?, 0, 1)
                ON CONFLICT(guild_id, user_id) DO UPDATE SET
                    username = excluded.username
                """,
                (guild_id, user_id, username, now),
            )
            await db.commit()

    async def get_guild_member(self, guild_id: int, user_id: int) -> dict | None:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT guild_id, user_id, username, registered_at, xp, nivel
                FROM guild_members
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()

        if row is None:
            return None
        return {
            "guild_id": row[0],
            "discord_id": row[1],
            "username": row[2],
            "fecha_registro": row[3],
            "xp": row[4],
            "nivel": row[5],
        }

    async def add_xp(
        self,
        guild_id: int,
        user_id: int,
        username: str,
        xp_gained: int,
    ) -> dict | None:
        await self.ensure_guild_member(guild_id, user_id, username)

        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT xp, nivel
                FROM guild_members
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()

            if row is None:
                return None

            current_xp, current_level = row
            next_xp = current_xp + xp_gained
            required_xp = current_level * 100
            next_level = current_level

            while next_xp >= required_xp:
                next_xp -= required_xp
                next_level += 1
                required_xp = next_level * 100

            await db.execute(
                """
                UPDATE guild_members
                SET xp = ?, nivel = ?, username = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (next_xp, next_level, username, guild_id, user_id),
            )
            await db.commit()

        return {
            "xp_actual": next_xp,
            "nivel_actual": next_level,
            "subio_nivel": next_level > current_level,
            "nivel_anterior": current_level,
        }

    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> list[dict]:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT user_id, username, nivel, xp
                FROM guild_members
                WHERE guild_id = ?
                ORDER BY nivel DESC, xp DESC
                LIMIT ?
                """,
                (guild_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()

        return [
            {
                "discord_id": row[0],
                "username": row[1],
                "nivel": row[2],
                "xp": row[3],
            }
            for row in rows
        ]

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
