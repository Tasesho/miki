from __future__ import annotations

import time

from services.guild_settings import GuildSettingsService


class ActivityService:
    def __init__(self, user_repository, guild_settings: GuildSettingsService):
        self.user_repository = user_repository
        self.guild_settings = guild_settings
        self.xp_cooldown: dict[tuple[int, int], float] = {}

    async def record_message(
        self,
        guild_id: int,
        user_id: int,
        username: str,
    ) -> dict | None:
        now = time.time()
        cooldown_key = (guild_id, user_id)
        cooldown_seconds = await self.guild_settings.get_int(
            guild_id,
            "xp_cooldown_seconds",
        )
        xp_per_message = await self.guild_settings.get_int(guild_id, "xp_per_message")
        last_xp_time = self.xp_cooldown.get(cooldown_key, 0)

        if cooldown_seconds is None or xp_per_message is None:
            return None

        if now - last_xp_time < cooldown_seconds:
            return None

        result = await self.user_repository.add_xp(
            guild_id,
            user_id,
            username,
            xp_per_message,
        )
        self.xp_cooldown[cooldown_key] = now
        return result
