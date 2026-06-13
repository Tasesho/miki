from __future__ import annotations


class LeaderboardService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def top_members(self, guild_id: int, limit: int = 10) -> list[dict]:
        return await self.user_repository.get_leaderboard(guild_id, limit)
