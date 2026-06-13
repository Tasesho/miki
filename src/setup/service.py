from __future__ import annotations

from setup.flow import SetupSession


class SetupStateService:
    def __init__(self, repository):
        self.repository = repository

    async def load(self, guild_id: int, flow_key: str) -> SetupSession:
        state = await self.repository.get_state(guild_id, flow_key)
        return SetupSession(guild_id=guild_id, flow_key=flow_key, state=state or {})

    async def save(self, session: SetupSession) -> None:
        await self.repository.save_state(
            session.guild_id,
            session.flow_key,
            session.state,
        )

    async def clear(self, guild_id: int, flow_key: str) -> None:
        await self.repository.clear_state(guild_id, flow_key)
