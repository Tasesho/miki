from __future__ import annotations

from datetime import UTC, datetime

from database.connection import AsyncConnection, Database


class SocialLinkRepository:
    REACTION_PER_TARGET_DAILY_LIMIT = 3
    REACTION_GLOBAL_DAILY_LIMIT = 10
    MESSAGE_ACTIONS = ("reaction", "reply", "mention")

    def __init__(self, database: Database, base_level_xp: int = 100, reaction_xp: int = 1):
        self.database = database
        self.base_level_xp = base_level_xp
        self.reaction_xp = reaction_xp

    async def get_link(self, guild_id: int, user_id: int, target_user_id: int) -> dict:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT guild_id, user_id, target_user_id, affinity_xp, affinity_rank
                FROM social_links
                WHERE guild_id = ? AND user_id = ? AND target_user_id = ?
                """,
                (guild_id, user_id, target_user_id),
            ) as cursor:
                row = await cursor.fetchone()

        return (
            self._link_from_row(row) if row else self._empty_link(guild_id, user_id, target_user_id)
        )

    async def list_links(self, guild_id: int, user_id: int, limit: int = 25) -> list[dict]:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT guild_id, user_id, target_user_id, affinity_xp, affinity_rank
                FROM social_links
                WHERE guild_id = ? AND user_id = ?
                ORDER BY affinity_rank DESC, affinity_xp DESC, target_user_id
                LIMIT ?
                """,
                (guild_id, user_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()

        return [self._link_from_row(row) for row in rows]

    async def add_affinity(
        self,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        affinity_xp: int,
        action: str,
        source_id: str,
    ) -> dict | None:
        if user_id == target_user_id or affinity_xp <= 0:
            return None

        now = self._now()
        async with self.database.connect() as db:
            await db.execute("BEGIN IMMEDIATE")
            inserted = await self._insert_interaction(
                db,
                guild_id,
                user_id,
                target_user_id,
                action,
                affinity_xp,
                source_id,
                now,
            )
            if not inserted:
                await db.rollback()
                return None

            link = await self._upsert_affinity(
                db, guild_id, user_id, target_user_id, affinity_xp, now
            )
            await db.commit()
        return link

    async def add_reaction_affinity(
        self,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        message_id: int,
        affinity_xp: int | None = None,
    ) -> dict | None:
        return await self.add_message_affinity(
            guild_id, user_id, target_user_id, message_id, "reaction", affinity_xp
        )

    async def add_message_affinity(
        self,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        message_id: int,
        action: str,
        affinity_xp: int | None = None,
    ) -> dict | None:
        if action not in self.MESSAGE_ACTIONS:
            raise ValueError(f"Unsupported Social Link message action: {action}")
        if user_id == target_user_id:
            return None
        if affinity_xp is None:
            affinity_xp = self.reaction_xp
        if affinity_xp <= 0:
            return None

        now = self._now()
        today = now[:10]
        source_id = str(message_id)
        async with self.database.connect() as db:
            await db.execute("BEGIN IMMEDIATE")
            already_rewarded = await self._message_interaction_exists(
                db, guild_id, user_id, target_user_id, source_id
            )
            if already_rewarded:
                await db.rollback()
                return None

            async with db.execute(
                """
                SELECT COUNT(*)
                FROM social_link_interactions
                WHERE guild_id = ? AND user_id = ? AND action IN ('reaction', 'reply', 'mention')
                  AND target_user_id = ? AND substr(created_at, 1, 10) = ?
                """,
                (guild_id, user_id, target_user_id, today),
            ) as cursor:
                target_count = (await cursor.fetchone())[0]

            if target_count >= self.REACTION_PER_TARGET_DAILY_LIMIT:
                await db.rollback()
                return None

            async with db.execute(
                """
                SELECT COUNT(*)
                FROM social_link_interactions
                WHERE guild_id = ? AND user_id = ? AND action IN ('reaction', 'reply', 'mention')
                  AND substr(created_at, 1, 10) = ?
                """,
                (guild_id, user_id, today),
            ) as cursor:
                global_count = (await cursor.fetchone())[0]

            if global_count >= self.REACTION_GLOBAL_DAILY_LIMIT:
                await db.rollback()
                return None

            await self._insert_interaction(
                db,
                guild_id,
                user_id,
                target_user_id,
                action,
                affinity_xp,
                source_id,
                now,
            )
            link = await self._upsert_affinity(
                db, guild_id, user_id, target_user_id, affinity_xp, now
            )
            await db.commit()
        return link

    async def _insert_interaction(
        self,
        db: AsyncConnection,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        action: str,
        affinity_xp: int,
        source_id: str,
        created_at: str,
    ) -> bool:
        cursor = await db.execute(
            """
            INSERT OR IGNORE INTO social_link_interactions
                (guild_id, user_id, target_user_id, action, affinity_xp, source_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                guild_id,
                user_id,
                target_user_id,
                action,
                affinity_xp,
                source_id,
                created_at,
            ),
        )
        return cursor.rowcount == 1

    async def _interaction_exists(
        self,
        db: AsyncConnection,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        action: str,
        source_id: str,
    ) -> bool:
        async with db.execute(
            """
            SELECT 1
            FROM social_link_interactions
            WHERE guild_id = ? AND user_id = ? AND target_user_id = ?
              AND action = ? AND source_id = ?
            """,
            (guild_id, user_id, target_user_id, action, source_id),
        ) as cursor:
            return await cursor.fetchone() is not None

    async def _message_interaction_exists(
        self,
        db: AsyncConnection,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        source_id: str,
    ) -> bool:
        async with db.execute(
            """
            SELECT 1
            FROM social_link_interactions
            WHERE guild_id = ? AND user_id = ? AND target_user_id = ?
              AND action IN ('reaction', 'reply', 'mention') AND source_id = ?
            """,
            (guild_id, user_id, target_user_id, source_id),
        ) as cursor:
            return await cursor.fetchone() is not None

    async def _upsert_affinity(
        self,
        db: AsyncConnection,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        affinity_xp: int,
        now: str,
    ) -> dict:
        async with db.execute(
            """
            SELECT affinity_xp, affinity_rank
            FROM social_links
            WHERE guild_id = ? AND user_id = ? AND target_user_id = ?
            """,
            (guild_id, user_id, target_user_id),
        ) as cursor:
            row = await cursor.fetchone()

        current_xp = row[0] if row else 0
        current_rank = row[1] if row else 1
        next_xp = current_xp + affinity_xp
        next_rank = self.rank_for_xp(next_xp, self.base_level_xp)
        await db.execute(
            """
            INSERT INTO social_links
                (guild_id, user_id, target_user_id, affinity_xp, affinity_rank, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(guild_id, user_id, target_user_id) DO UPDATE SET
                affinity_xp = excluded.affinity_xp,
                affinity_rank = excluded.affinity_rank,
                updated_at = excluded.updated_at
            """,
            (guild_id, user_id, target_user_id, next_xp, next_rank, now, now),
        )
        return self._empty_link(guild_id, user_id, target_user_id) | {
            "affinity_xp": next_xp,
            "affinity_rank": next_rank,
            "previous_rank": current_rank,
            "rank_up": next_rank > current_rank,
        }

    @classmethod
    def rank_for_xp(cls, affinity_xp: int, base_level_xp: int = 100) -> int:
        rank = 1
        threshold = 0
        cost = base_level_xp
        while rank < 10 and affinity_xp >= threshold + cost:
            threshold += cost
            rank += 1
            cost *= 2
        return rank

    @staticmethod
    def _link_from_row(row: tuple) -> dict:
        return {
            "guild_id": row[0],
            "user_id": row[1],
            "target_user_id": row[2],
            "affinity_xp": row[3],
            "affinity_rank": row[4],
        }

    @staticmethod
    def _empty_link(guild_id: int, user_id: int, target_user_id: int) -> dict:
        return {
            "guild_id": guild_id,
            "user_id": user_id,
            "target_user_id": target_user_id,
            "affinity_xp": 0,
            "affinity_rank": 1,
        }

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()
