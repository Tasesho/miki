from __future__ import annotations


class GuildModuleService:
    def __init__(self, guild_repository):
        self.guild_repository = guild_repository

    async def is_enabled(self, guild_id: int, module_key: str) -> bool:
        return await self.guild_repository.is_module_enabled(guild_id, module_key)

    async def set_enabled(self, guild_id: int, module_key: str, enabled: bool) -> None:
        await self.guild_repository.set_module_enabled(guild_id, module_key, enabled)
