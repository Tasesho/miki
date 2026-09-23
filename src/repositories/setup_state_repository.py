from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from database.connection import Database


class SetupStateRepository:
    def __init__(self, database: Database):
        self.database = database

    async def get_state(self, guild_id: int, flow_key: str) -> dict[str, Any] | None:
        async with self.database.connect() as db:
            async with db.execute(
                """
                SELECT state_json
                FROM guild_setup_state
                WHERE guild_id = ? AND flow_key = ?
                """,
                (guild_id, flow_key),
            ) as cursor:
                row = await cursor.fetchone()

        if row is None:
            return None
        return json.loads(row[0])

    async def save_state(
        self,
        guild_id: int,
        flow_key: str,
        state: dict[str, Any],
    ) -> None:
        async with self.database.connect() as db:
            await db.execute(
                """
                INSERT INTO guild_setup_state (guild_id, flow_key, state_json, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id, flow_key) DO UPDATE SET
                    state_json = excluded.state_json,
                    updated_at = excluded.updated_at
                """,
                (guild_id, flow_key, json.dumps(state), self._now()),
            )
            await db.commit()

    async def clear_state(self, guild_id: int, flow_key: str) -> None:
        async with self.database.connect() as db:
            await db.execute(
                """
                DELETE FROM guild_setup_state
                WHERE guild_id = ? AND flow_key = ?
                """,
                (guild_id, flow_key),
            )
            await db.commit()

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
