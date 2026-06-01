class ProfileService:
    def __init__(self, db):
        self.db = db

    async def get_profile(self, guild_id, user):
        return await self.db.get_usuario(guild_id, user.id)

    async def ensure_profile(self, guild_id, user):
        await self.db.ensure_guild_member(guild_id, user.id, user.name)

    async def set_field(self, guild_id, user, field_key, value):
        field_key = field_key.lower().strip()
        field = await self.db.get_profile_field(field_key)
        if field is None:
            return None

        await self.ensure_profile(guild_id, user)
        await self.db.set_profile_value(guild_id, user.id, field_key, value.strip())
        return field

    async def available_fields(self):
        return await self.db.get_profile_fields()

    def format_profile_url(self, field, value):
        template = field.get("url_template")
        if not template:
            return value
        if field["key"] == "website" and value.startswith(("http://", "https://")):
            return value
        return template.format(value=value)
