from __future__ import annotations

import logging
import re

import discord

from dashboard.repository import PostgresWelcomeCardRepository
from services.welcome_card_renderer import WelcomeCardRenderer


class WelcomeCardService:
    def __init__(self, repository: PostgresWelcomeCardRepository | None):
        self.repository = repository
        self.renderer = WelcomeCardRenderer()

    async def send(self, member: discord.Member) -> bool:
        if self.repository is None:
            return False
        settings = await self.repository.get(member.guild.id)
        if not settings.enabled or settings.channel_id is None:
            return False
        channel = self._valid_channel(member.guild, settings.channel_id)
        if channel is None:
            return False
        image = await self.renderer.render(
            settings,
            member.display_name,
            member.guild.member_count or 0,
            str(member.display_avatar.url),
        )
        await channel.send(
            content=self._message_content(settings.extra_message, member, member.guild, channel),
            file=discord.File(image, filename="welcome.png"),
            allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False),
        )
        return True

    async def send_test(self, guild: discord.Guild) -> bool:
        if self.repository is None:
            logging.warning("Welcome-card test requested without PostgreSQL configured")
            return False
        settings = await self.repository.get(guild.id)
        if not settings.enabled or settings.channel_id is None:
            logging.warning("Welcome-card test requested but card is disabled for %s", guild.id)
            return False
        channel = self._valid_channel(guild, settings.channel_id)
        if channel is None:
            return False
        image = await self.renderer.render(settings, "Miki test", guild.member_count or 0, None)
        await channel.send(
            content=self._message_content(settings.extra_message, None, guild, channel),
            file=discord.File(image, filename="welcome-test.png"),
            allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False),
        )
        logging.info("Sent welcome-card test to #%s in %s", channel.name, guild.name)
        return True

    def _valid_channel(self, guild: discord.Guild, channel_id: int) -> discord.TextChannel | None:
        channel = guild.get_channel(channel_id)
        me = guild.me
        if not isinstance(channel, discord.TextChannel) or me is None:
            logging.warning("Welcome channel %s is unavailable in %s", channel_id, guild.id)
            return None
        permissions = channel.permissions_for(me)
        if not permissions.send_messages or not permissions.attach_files:
            logging.warning("Miki lacks welcome-card permissions in #%s", channel.name)
            return None
        return channel

    @staticmethod
    def _message_content(
        template: str,
        member: discord.Member | None,
        guild: discord.Guild,
        configured_channel: discord.TextChannel,
    ) -> str:
        user_mention = member.mention if member else "@Miki test"
        user_name = member.display_name if member else "Miki test"

        def replace(match: re.Match[str]) -> str:
            token = match.group(1).strip()
            if token == "user":
                return user_mention
            if token == "user.name":
                return user_name
            if token == "server.name":
                return guild.name
            if token == "channel":
                return configured_channel.mention
            if token == "channel.name":
                return configured_channel.name
            if token.startswith("channel:"):
                value = token.removeprefix("channel:")
                channel = WelcomeCardService._find_channel(guild, value)
                return channel.mention if channel else f"#{value}"
            if token.startswith("role:"):
                value = token.removeprefix("role:")
                role = WelcomeCardService._find_role(guild, value)
                return role.mention if role else f"@{value}"
            if token.startswith("user:") and token.removeprefix("user:").isdigit():
                return f"<@{token.removeprefix('user:')}>"
            return match.group(0)

        return re.sub(r"\{([^{}]+)\}", replace, template)

    @staticmethod
    def _find_channel(guild: discord.Guild, value: str) -> discord.TextChannel | None:
        if value.isdigit():
            channel = guild.get_channel(int(value))
            return channel if isinstance(channel, discord.TextChannel) else None
        return discord.utils.find(
            lambda item: item.name.casefold() == value.casefold(), guild.text_channels
        )

    @staticmethod
    def _find_role(guild: discord.Guild, value: str) -> discord.Role | None:
        if value.isdigit():
            return guild.get_role(int(value))
        return discord.utils.find(
            lambda item: item.name.casefold() == value.casefold(), guild.roles
        )
