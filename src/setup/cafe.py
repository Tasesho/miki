from __future__ import annotations

import discord

from setup.base import BaseSetupView


class CafeSettingsModal(discord.ui.Modal, title="Configurar Café Suelto"):
    cooldown = discord.ui.TextInput(
        label="Espera mínima inicial (horas)",
        placeholder="1",
        required=True,
        min_length=1,
        max_length=5,
    )
    duration = discord.ui.TextInput(
        label="Duración del mensaje (segundos)",
        placeholder="30",
        required=True,
        min_length=1,
        max_length=5,
    )
    gift_xp = discord.ui.TextInput(
        label="XP por regalar a otro usuario",
        placeholder="100",
        required=True,
        min_length=1,
        max_length=6,
    )
    chance = discord.ui.TextInput(
        label="Probabilidad: 1 entre N",
        placeholder="5",
        required=True,
        min_length=1,
        max_length=4,
    )

    def __init__(self, guild_settings, guild_id: int, values: tuple[int, int, int, int]):
        super().__init__()
        self.guild_settings = guild_settings
        self.guild_id = guild_id
        self.cooldown.default = str(values[0])
        self.duration.default = str(values[1])
        self.gift_xp.default = str(values[2])
        self.chance.default = str(values[3])

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            cooldown = int(self.cooldown.value)
            duration = int(self.duration.value)
            gift_xp = int(self.gift_xp.value)
            chance = int(self.chance.value)
        except ValueError:
            await interaction.response.send_message(
                "(´；ω；`) Todos los valores deben ser números enteros.", ephemeral=True
            )
            return

        if not 1 <= cooldown <= 168:
            message = "(´・ω・`) La espera mínima debe estar entre 1 hora y 7 días."
        elif not 1 <= duration <= 3600:
            message = "(´・ω・`) La duración debe estar entre 1 segundo y 1 hora."
        elif not 0 <= gift_xp <= 10000:
            message = "(´・ω・`) La recompensa debe estar entre 0 y 10.000 XP."
        elif not 1 <= chance <= 1000:
            message = "(´・ω・`) La probabilidad debe estar entre 1 y 1.000."
        else:
            await self.guild_settings.set(
                self.guild_id, "coffee_event_min_wait_hours", str(cooldown)
            )
            await self.guild_settings.set(
                self.guild_id, "coffee_event_duration_seconds", str(duration)
            )
            await self.guild_settings.set(
                self.guild_id, "coffee_event_chance_denominator", str(chance)
            )
            await self.guild_settings.set(self.guild_id, "coffee_gift_xp", str(gift_xp))
            await interaction.response.send_message(
                f"(｡•̀ᴗ-)✧ Café configurado: espera **{cooldown} h**, "
                f"probabilidad **1/{chance}** por minuto, duración **{duration} s**, "
                f"recompensa **{gift_xp} XP**.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(message, ephemeral=True)


class CafeSetupView(BaseSetupView):
    def __init__(self, guild_id: int, user_id: int, guild_settings):
        super().__init__(guild_id, user_id)
        self.guild_settings = guild_settings

    @discord.ui.button(label="Configurar valores", style=discord.ButtonStyle.primary)
    async def configure_button(self, interaction: discord.Interaction, button):
        cooldown = await self.guild_settings.get_int(
            self.guild_id, "coffee_event_min_wait_hours"
        ) or 1
        duration = await self.guild_settings.get_int(
            self.guild_id, "coffee_event_duration_seconds"
        ) or 30
        gift_xp = await self.guild_settings.get_int(self.guild_id, "coffee_gift_xp")
        if gift_xp is None:
            gift_xp = 100
        chance = await self.guild_settings.get_int(
            self.guild_id, "coffee_event_chance_denominator"
        ) or 5
        await interaction.response.send_modal(
            CafeSettingsModal(
                self.guild_settings, self.guild_id, (cooldown, duration, gift_xp, chance)
            )
        )

    @discord.ui.button(label="Terminar", style=discord.ButtonStyle.green)
    async def finish_button(self, interaction: discord.Interaction, button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="(´▽`) Configuración de Café Suelto guardada.", view=self
        )
