from __future__ import annotations

import discord

from setup.base import BaseSetupView, SetupManager


class SetupDropdown(discord.ui.Select):
    def __init__(self, setup_manager: SetupManager, guild_id: int, user_id: int):
        self.setup_manager = setup_manager
        self.guild_id = guild_id
        self.user_id = user_id

        options = []
        modules = setup_manager.get_registered_modules()

        if not modules:
            options.append(
                discord.SelectOption(
                    label="Sin módulos", description="No hay módulos configurables aún."
                )
            )
        else:
            for module_name in modules:
                options.append(
                    discord.SelectOption(
                        label=module_name, description=f"Configurar opciones de {module_name}"
                    )
                )

        super().__init__(
            placeholder="Selecciona un módulo para configurar...",
            min_values=1,
            max_values=1,
            options=options,
            disabled=len(modules) == 0,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_module = self.values[0]
        view = self.setup_manager.get_view(selected_module, self.guild_id, self.user_id)

        if view:
            await interaction.response.send_message(
                f"🔧 Abriendo configuración de **{selected_module}**...", view=view, ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "(´・ω・`) No se pudo cargar el módulo.", ephemeral=True
            )


class ChannelSetupView(BaseSetupView):
    def __init__(self, guild_id: int, user_id: int, guild_settings):
        super().__init__(guild_id, user_id)
        self.guild_settings = guild_settings

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text],
        placeholder="🏆 Selecciona canal para Leaderboard...",
        row=0,
    )
    async def leaderboard_select(
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect
    ):
        was_set = await self.guild_settings.set(
            self.guild_id, "leaderboard_channel_id", str(select.values[0].id)
        )
        if was_set:
            await interaction.response.send_message(
                f"(´▽`) Canal de Leaderboard configurado: {select.values[0].mention}",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "(´；ω；`) Error: 'leaderboard_channel_id' no es válida en GuildSettings.",
                ephemeral=True,
            )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text],
        placeholder="🔮 Selecciona canal para Fortuna...",
        row=1,
    )
    async def fortune_select(
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect
    ):
        was_set = await self.guild_settings.set(
            self.guild_id, "fortune_channel_id", str(select.values[0].id)
        )
        if was_set:
            await interaction.response.send_message(
                f"(´▽`) Canal de Fortuna configurado: {select.values[0].mention}", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "(´；ω；`) Error: 'fortune_channel_id' no es válida en GuildSettings.",
                ephemeral=True,
            )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text],
        placeholder="✨ Selecciona canal principal (Chat/XP)...",
        row=2,
    )
    async def general_select(
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect
    ):
        was_set = await self.guild_settings.set(
            self.guild_id, "general_channel_id", str(select.values[0].id)
        )
        if was_set:
            await interaction.response.send_message(
                f"(´▽`) Canal principal configurado: {select.values[0].mention}", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "(´；ω；`) Error: 'general_channel_id' no es válida en GuildSettings.",
                ephemeral=True,
            )

    @discord.ui.button(label="Terminar Configuración", style=discord.ButtonStyle.green, row=3)
    async def finish_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="(´▽`) ¡Configuración de canales completada exitosamente! Ya estoy listo para funcionar.",
            view=self,
        )
