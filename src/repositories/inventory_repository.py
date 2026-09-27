from __future__ import annotations

from datetime import UTC, datetime

from database.connection import Database


class InventoryRepository:
    def __init__(self, database: Database):
        self.database = database

    async def get_inventory(self, guild_id: int, user_id: int) -> int:
        async with self.database.connect() as db:
            async with db.execute(
                "SELECT consumables FROM inventories WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()
        return row[0] if row else 0

    async def add_consumable(self, guild_id: int, user_id: int, amount: int = 1) -> int:
        if amount <= 0:
            raise ValueError("amount must be positive")
        now = self._now()
        async with self.database.connect() as db:
            await db.execute(
                """
                INSERT INTO inventories (guild_id, user_id, consumables, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id, user_id) DO UPDATE SET
                    consumables = inventories.consumables + excluded.consumables,
                    updated_at = excluded.updated_at
                """,
                (guild_id, user_id, amount, now),
            )
            await db.commit()
        return await self.get_inventory(guild_id, user_id)

    async def remove_consumable(self, guild_id: int, user_id: int, amount: int = 1) -> bool:
        if amount <= 0:
            raise ValueError("amount must be positive")
        async with self.database.connect() as db:
            cursor = await db.execute(
                """
                UPDATE inventories
                SET consumables = consumables - ?, updated_at = ?
                WHERE guild_id = ? AND user_id = ? AND consumables >= ?
                """,
                (amount, self._now(), guild_id, user_id, amount),
            )
            removed = cursor.rowcount == 1
            await db.commit()
        return removed

    async def add_miki_affinity(self, guild_id: int, user_id: int, amount: int = 1) -> int:
        if amount <= 0:
            raise ValueError("amount must be positive")
        now = self._now()
        async with self.database.connect() as db:
            await db.execute(
                """
                INSERT INTO miki_affinity (guild_id, user_id, affinity_points, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id, user_id) DO UPDATE SET
                    affinity_points = miki_affinity.affinity_points + excluded.affinity_points,
                    updated_at = excluded.updated_at
                """,
                (guild_id, user_id, amount, now),
            )
            await db.commit()
            async with db.execute(
                """
                SELECT affinity_points FROM miki_affinity
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()
        return row[0]

    async def get_miki_affinity(self, guild_id: int, user_id: int) -> int:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT affinity_points FROM miki_affinity
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()
        return row[0] if row else 0

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
