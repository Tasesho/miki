from __future__ import annotations


class SocialLinkService:
    RANK_TITLES = {
        1: "Conocido",
        2: "Visitante Frecuente",
        3: "Compañero de Chat",
        4: "Amigo Casual",
        5: "Compañero de Código",
        6: "Amigo Cercano",
        7: "Socio de Madrugada",
        8: "Confidente Técnico",
        9: "Mejor Amigo",
        10: "Confidente Supremo",
    }

    def __init__(self, repository, guild_settings, base_level_xp: int = 100):
        self.repository = repository
        self.guild_settings = guild_settings
        self.base_level_xp = base_level_xp
        self.message_target_daily_limit = repository.REACTION_PER_TARGET_DAILY_LIMIT
        self.message_global_daily_limit = repository.REACTION_GLOBAL_DAILY_LIMIT

    async def get_link(self, guild_id: int, user_id: int, target_user_id: int) -> dict:
        return await self.repository.get_link(guild_id, user_id, target_user_id)

    async def list_links(self, guild_id: int, user_id: int) -> list[dict]:
        return await self.repository.list_links(guild_id, user_id)

    async def record_reaction(
        self, guild_id: int, user_id: int, target_user_id: int, message_id: int
    ) -> dict | None:
        return await self.record_message_action(
            guild_id, user_id, target_user_id, message_id, "reaction"
        )

    async def record_message_action(
        self,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        message_id: int,
        action: str,
    ) -> dict | None:
        affinity_xp = await self.guild_settings.get_int(guild_id, "social_link_xp")
        if affinity_xp is None:
            affinity_xp = 1
        return await self.repository.add_message_affinity(
            guild_id, user_id, target_user_id, message_id, action, affinity_xp
        )

    async def record_gift(
        self,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        source_id: str,
        affinity_xp: int = 1,
    ) -> dict | None:
        if affinity_xp == 1:
            configured_xp = await self.guild_settings.get_int(guild_id, "social_link_xp")
            if configured_xp is not None:
                affinity_xp = configured_xp
        return await self.repository.add_affinity(
            guild_id,
            user_id,
            target_user_id,
            affinity_xp,
            "gift",
            source_id,
        )

    def rank_title(self, rank: int) -> str:
        return self.RANK_TITLES[rank]

    def progress(self, affinity_xp: int, rank: int) -> tuple[int, int | None]:
        if rank >= 10:
            return affinity_xp, None

        threshold = 0
        cost = self.base_level_xp
        for _ in range(1, rank):
            threshold += cost
            cost *= 2
        return affinity_xp - threshold, cost
