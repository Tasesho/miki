from __future__ import annotations

from collections.abc import Callable

import discord


class BaseSetupView(discord.ui.View):
    """
    Base view for all interactive setup panels.
    Ensures only the user who initiated the setup can interact with it.
    """

    def __init__(self, guild_id: int, user_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "(´・ω・`) No tienes permiso para interactuar con este menú.", ephemeral=True
            )
            return False
        return True


class SetupManager:
    """
    Registry and orchestrator for all setup modules.
    Allows future modules (like Economy, AI, Logging) to inject their own
    setup views without bloating the main command.
    """

    def __init__(self):
        # Dictionary mapping a module name to its View factory
        self._modules: dict[str, Callable[[int, int], discord.ui.View]] = {}

    def register_module(
        self, name: str, view_factory: Callable[[int, int], discord.ui.View]
    ) -> None:
        """Registers a new setup module (e.g. 'XP Settings', 'Logging')."""
        self._modules[name] = view_factory

    def get_registered_modules(self) -> list[str]:
        return list(self._modules.keys())

    def get_view(self, name: str, guild_id: int, user_id: int) -> discord.ui.View | None:
        factory = self._modules.get(name)
        if factory:
            return factory(guild_id, user_id)
        return None
