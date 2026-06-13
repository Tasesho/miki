from __future__ import annotations

from config import settings
from database.connection import Database
from database.migrator import MigrationRunner
from repositories.guild_repository import GuildRepository
from repositories.profile_repository import ProfileRepository
from repositories.user_repository import UserRepository


class DBManager:
    """Compatibility facade for older call sites.

    New code should depend on services or repositories directly. This class keeps
    current modules and scripts working while the project moves to clearer data
    access boundaries.
    """

    def __init__(self, db_path: str | None = None):
        self.database = Database(db_path or settings.database_path)
        self.users = UserRepository(self.database)
        self.profiles = ProfileRepository(self.database)
        self.guilds = GuildRepository(self.database)
        self.migrations = MigrationRunner(self.database)

    async def init_db(self) -> None:
        await self.migrations.run()

    async def ensure_user(self, user_id: int, username: str) -> None:
        await self.users.ensure_user(user_id, username)

    async def ensure_guild_member(self, guild_id: int, user_id: int, username: str) -> None:
        await self.users.ensure_guild_member(guild_id, user_id, username)

    async def get_usuario(self, guild_id: int, user_id: int) -> dict | None:
        member = await self.users.get_guild_member(guild_id, user_id)
        if member is None:
            return None
        profile_fields = await self.profiles.get_values(guild_id, user_id)
        return {
            **member,
            "profile_fields": profile_fields,
            "twitter": profile_fields.get("twitter"),
            "github": profile_fields.get("github"),
            "instagram": profile_fields.get("instagram"),
            "website": profile_fields.get("website"),
        }

    async def registrar_usuario(self, guild_id: int, user_id: int, username: str) -> None:
        await self.ensure_guild_member(guild_id, user_id, username)

    async def actualizar_xp(
        self,
        guild_id: int,
        user_id: int,
        username: str,
        xp_ganado: int,
    ) -> dict | None:
        return await self.users.add_xp(guild_id, user_id, username, xp_ganado)

    async def actualizar_redes(self, guild_id: int, user_id: int, **fields: str) -> None:
        for field_key, value in fields.items():
            if value is not None:
                await self.set_profile_value(guild_id, user_id, field_key, value)

    async def get_profile_fields(self) -> list[dict]:
        return await self.profiles.get_fields()

    async def get_profile_field(self, field_key: str) -> dict | None:
        return await self.profiles.get_field(field_key)

    async def get_profile_values(self, guild_id: int, user_id: int) -> dict[str, str]:
        return await self.profiles.get_values(guild_id, user_id)

    async def set_profile_value(
        self,
        guild_id: int,
        user_id: int,
        field_key: str,
        field_value: str,
    ) -> bool:
        return await self.profiles.set_value(guild_id, user_id, field_key, field_value)

    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> list[dict]:
        return await self.users.get_leaderboard(guild_id, limit)

    async def get_setting(self, guild_id: int, setting_key: str) -> str | None:
        return await self.guilds.get_setting(guild_id, setting_key)

    async def set_setting(self, guild_id: int, setting_key: str, setting_value: str) -> None:
        await self.guilds.set_setting(guild_id, setting_key, setting_value)

    async def get_guild_triggers(self, guild_id: int) -> dict[str, str]:
        return await self.guilds.get_triggers(guild_id)
