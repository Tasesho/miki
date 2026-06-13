from __future__ import annotations

import discord

from setup.base import SetupManager


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
