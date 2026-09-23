from __future__ import annotations

import discord

from setup.flow import SetupFlow, SetupSession


class SetupView(discord.ui.View):
    """Base view for future setup flows.

    Feature-specific setup screens should subclass this and persist changes
    through SetupStateService, not by writing directly to the database.
    """

    def __init__(self, flow: SetupFlow, session: SetupSession, *, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.flow = flow
        self.session = session

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return bool(interaction.guild and interaction.guild.id == self.session.guild_id)
