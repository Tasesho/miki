class GuildSettingsService:
    DEFAULTS = {
        "leaderboard_channel_id": None,
        "logs_channel_id": None,
        "welcome_channel_id": None,
        "fortune_channel_id": None,
        "general_channel_id": None,
        "leaderboard_hour": "0",
        "fortune_hour": "12",
        "xp_per_message": "10",
        "xp_cooldown_seconds": "60",
    }

    def __init__(self, db):
        self.db = db

    async def get(self, guild_id, key):
        value = await self.db.get_setting(guild_id, key)
        if value is None:
            return self.DEFAULTS.get(key)
        return value

    async def set(self, guild_id, key, value):
        if key not in self.DEFAULTS:
            return False
        await self.db.set_setting(guild_id, key, value)
        return True

    async def get_int(self, guild_id, key):
        value = await self.get(guild_id, key)
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            default = self.DEFAULTS[key]
            return int(default) if default is not None else None

    def available_keys(self):
        return sorted(self.DEFAULTS.keys())
