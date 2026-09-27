from __future__ import annotations

import asyncio


class InventoryService:
    ITEM_NAMES = ("Café", "Pancito", "Daigo")
    COFFEE_XP_REWARD = 50

    def __init__(
        self,
        repository,
        user_repository,
        social_link_service,
        coffee_event_min_minutes: float = 240,
        coffee_event_max_minutes: float = 300,
        coffee_event_duration_seconds: float = 30,
        coffee_event_min_wait_hours: float = 1,
        coffee_event_chance_denominator: int = 5,
        coffee_gift_xp: int = 100,
    ):
        self.repository = repository
        self.user_repository = user_repository
        self.social_link_service = social_link_service
        self.coffee_event_min_minutes = coffee_event_min_minutes
        self.coffee_event_max_minutes = coffee_event_max_minutes
        self.coffee_event_duration_seconds = coffee_event_duration_seconds
        self.coffee_event_min_wait_hours = coffee_event_min_wait_hours
        self.coffee_event_chance_denominator = coffee_event_chance_denominator
        self.coffee_gift_xp = coffee_gift_xp
        self._locks: dict[tuple[int, int], asyncio.Lock] = {}

    async def inventory(self, guild_id: int, user_id: int) -> int:
        return await self.repository.get_inventory(guild_id, user_id)

    async def award_consumable(self, guild_id: int, user_id: int) -> int:
        return await self.repository.add_consumable(guild_id, user_id)

    async def use_consumable(
        self, guild_id: int, user_id: int, username: str
    ) -> dict | None:
        async with self._lock_for(guild_id, user_id):
            if not await self.repository.remove_consumable(guild_id, user_id):
                return None
            try:
                xp_result = await self.user_repository.add_xp(
                    guild_id, user_id, username, self.COFFEE_XP_REWARD
                )
            except Exception:
                await self.repository.add_consumable(guild_id, user_id)
                raise
        return xp_result

    async def gift_consumable(
        self,
        guild_id: int,
        user_id: int,
        target_user_id: int,
        source_id: str,
        username: str = "",
        gift_xp: int | None = None,
        target_is_miki: bool = False,
    ) -> dict | None:
        if user_id == target_user_id:
            return None
        async with self._lock_for(guild_id, user_id):
            if not await self.repository.remove_consumable(guild_id, user_id):
                return None
            try:
                if target_is_miki:
                    points = await self.repository.add_miki_affinity(guild_id, user_id)
                    return {"target": "miki", "affinity_points": points}

                link = await self.social_link_service.record_gift(
                    guild_id, user_id, target_user_id, source_id
                )
                if link is None:
                    await self.repository.add_consumable(guild_id, user_id)
                    return None
                reward_xp = self.coffee_gift_xp if gift_xp is None else gift_xp
                if reward_xp > 0:
                    link["gift_xp_result"] = await self.user_repository.add_xp(
                        guild_id, user_id, username, reward_xp
                    )
                return link
            except Exception:
                await self.repository.add_consumable(guild_id, user_id)
                raise

    async def miki_affinity(self, guild_id: int, user_id: int) -> int:
        return await self.repository.get_miki_affinity(guild_id, user_id)

    def _lock_for(self, guild_id: int, user_id: int) -> asyncio.Lock:
        key = (guild_id, user_id)
        lock = self._locks.get(key)
        if lock is None:
            lock = self._locks[key] = asyncio.Lock()
        return lock
