from __future__ import annotations


class ProfileService:
    def __init__(self, users, profiles):
        self.users = users
        self.profiles = profiles

    async def get_profile(self, guild_id: int, user) -> dict | None:
        member = await self.users.get_guild_member(guild_id, user.id)
        if member is None:
            return None

        profile_fields = await self.profiles.get_values(guild_id, user.id)
        return {
            **member,
            "profile_fields": profile_fields,
            "twitter": profile_fields.get("twitter"),
            "github": profile_fields.get("github"),
            "instagram": profile_fields.get("instagram"),
            "website": profile_fields.get("website"),
        }

    async def ensure_profile(self, guild_id: int, user) -> None:
        await self.users.ensure_guild_member(guild_id, user.id, user.name)

    async def set_field(self, guild_id: int, user, field_key: str, value: str) -> dict | None:
        field_key = field_key.lower().strip()
        field = await self.profiles.get_field(field_key)
        if field is None:
            return None

        await self.ensure_profile(guild_id, user)
        await self.profiles.set_value(guild_id, user.id, field_key, value.strip())
        return field

    async def available_fields(self) -> list[dict]:
        return await self.profiles.get_fields()

    def format_profile_url(self, field: dict, value: str) -> str:
        template = field.get("url_template")
        if not template:
            return value
        if field["key"] == "website" and value.startswith(("http://", "https://")):
            return value
        return template.format(value=value)
