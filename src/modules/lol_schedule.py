from __future__ import annotations

import logging
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from services.lol_schedule_service import (
    LOCAL_TIMEZONE,
    SCHEDULE_PAGE,
    ScheduleUnavailable,
    WorldsMatch,
    WorldsScheduleService,
)
from setup.base import BaseSetupView

POST_HOUR = 12


def schedule_embed(day, matches: list[WorldsMatch]) -> discord.Embed:
    embed = discord.Embed(
        title="(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Worlds de hoy",
        description=f"**{day:%d/%m/%Y}** · Horarios de Santiago (Chile)",
        color=discord.Color.from_rgb(86, 165, 255),
        url=SCHEDULE_PAGE,
    )
    if not matches:
        embed.add_field(
            name="(｡•́︿•̀｡) No hay partidas programadas",
            value="Hoy descansamos. Revisa de nuevo mañana para la próxima jornada.",
            inline=False,
        )
    else:
        for match in matches[:25]:
            start = match.starts_at.astimezone(LOCAL_TIMEZONE)
            status = " · En juego" if match.state == "inProgress" else ""
            if match.state == "completed":
                status = " · Finalizada"
            format_label = f" · Bo{match.best_of}" if match.best_of else ""
            embed.add_field(
                name=f"{start:%H:%M} · {match.teams[0]} vs {match.teams[1]}",
                value=f"{discord.utils.escape_markdown(match.stage)}{format_label}{status} · <t:{int(match.starts_at.timestamp())}:t>",
                inline=False,
            )
    embed.set_footer(text="Fuente: LoL Esports · Los horarios pueden cambiar (´｡• ᵕ •｡`)")
    return embed


def setup_embed(channel: discord.abc.GuildChannel | None, enabled: bool) -> discord.Embed:
    embed = discord.Embed(
        title="(｡•̀ᴗ-)✧ Configuración de Worlds",
        description="Elige el canal y activa o desactiva el anuncio diario con los botones.",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Canal", value=channel.mention if channel else "Sin configurar")
    embed.add_field(name="Anuncio automático", value="Activado" if enabled else "Desactivado")
    embed.add_field(name="Hora", value="12:00 · America/Santiago", inline=False)
    return embed


class ChannelPicker(discord.ui.ChannelSelect):
    def __init__(self, view: ScheduleSetupView):
        super().__init__(
            placeholder="Selecciona el canal de anuncios",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1,
        )
        self.setup_view = view

    async def callback(self, interaction: discord.Interaction) -> None:
        channel = self.values[0]
        await self.setup_view.settings.set(
            self.setup_view.guild_id, "lol_schedule_channel_id", str(channel.id)
        )
        await self.setup_view.refresh(interaction)


class ScheduleSetupView(BaseSetupView):
    def __init__(self, guild_id: int, user_id: int, settings):
        super().__init__(guild_id, user_id)
        self.settings = settings
        self.add_item(ChannelPicker(self))

    async def refresh(self, interaction: discord.Interaction) -> None:
        channel_id = await self.settings.get_int(self.guild_id, "lol_schedule_channel_id")
        channel = interaction.guild.get_channel(channel_id) if channel_id else None
        enabled = await self.settings.get(self.guild_id, "lol_schedule_enabled") == "1"
        await interaction.response.edit_message(embed=setup_embed(channel, enabled), view=self)

    @discord.ui.button(label="Activar", style=discord.ButtonStyle.success)
    async def enable(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        channel_id = await self.settings.get_int(self.guild_id, "lol_schedule_channel_id")
        channel = interaction.guild.get_channel(channel_id) if channel_id else None
        if channel is None:
            await interaction.response.send_message(
                "(｡•́︿•̀｡) Selecciona primero un canal de texto.", ephemeral=True
            )
            return
        permissions = channel.permissions_for(interaction.guild.me)
        if not (permissions.view_channel and permissions.send_messages and permissions.embed_links):
            await interaction.response.send_message(
                "(｡•́︿•̀｡) Necesito ver el canal, enviar mensajes e insertar enlaces allí.",
                ephemeral=True,
            )
            return
        await self.settings.set(self.guild_id, "lol_schedule_enabled", "1")
        await self.refresh(interaction)

    @discord.ui.button(label="Desactivar", style=discord.ButtonStyle.secondary)
    async def disable(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.settings.set(self.guild_id, "lol_schedule_enabled", "0")
        await self.refresh(interaction)


class LolSchedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = bot.app.services.guild_settings
        self.schedule = WorldsScheduleService()
        self.daily_post.start()

    def cog_unload(self) -> None:
        self.daily_post.cancel()

    @app_commands.command(name="lol-schedule", description="Muestra los partidos de Worlds de hoy")
    async def lol_schedule(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        day = datetime.now(LOCAL_TIMEZONE).date()
        try:
            matches = await self.schedule.for_day(day)
        except ScheduleUnavailable:
            logging.exception("Worlds schedule unavailable")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="(｡•́︿•̀｡) No pude consultar Worlds",
                    description="El calendario no responde ahora. Inténtalo de nuevo en unos minutos.",
                    color=discord.Color.orange(),
                )
            )
            return
        await interaction.followup.send(embed=schedule_embed(day, matches))

    @app_commands.command(
        name="lol-schedule-setup", description="Configura el anuncio diario de Worlds"
    )
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def lol_schedule_setup(self, interaction: discord.Interaction) -> None:
        channel_id = await self.settings.get_int(interaction.guild.id, "lol_schedule_channel_id")
        channel = interaction.guild.get_channel(channel_id) if channel_id else None
        enabled = await self.settings.get(interaction.guild.id, "lol_schedule_enabled") == "1"
        await interaction.response.send_message(
            embed=setup_embed(channel, enabled),
            view=ScheduleSetupView(interaction.guild.id, interaction.user.id, self.settings),
            ephemeral=True,
        )

    @tasks.loop(minutes=1)
    async def daily_post(self) -> None:
        now = datetime.now(LOCAL_TIMEZONE)
        if not POST_HOUR <= now.hour < POST_HOUR + 2:
            return
        day = now.date()
        guilds = []
        for guild in self.bot.guilds:
            if await self.settings.get(guild.id, "lol_schedule_enabled") != "1":
                continue
            if await self.settings.get(guild.id, "lol_schedule_last_sent_date") == day.isoformat():
                continue
            channel_id = await self.settings.get_int(guild.id, "lol_schedule_channel_id")
            channel = guild.get_channel(channel_id) if channel_id else None
            if channel is None:
                continue
            perms = channel.permissions_for(guild.me)
            if perms.view_channel and perms.send_messages and perms.embed_links:
                guilds.append((guild, channel))
        if not guilds:
            return
        try:
            matches = await self.schedule.for_day(day)
        except ScheduleUnavailable:
            logging.exception("Could not fetch Worlds schedule for daily announcement")
            return
        if not matches:
            return
        embed = schedule_embed(day, matches)
        for guild, channel in guilds:
            try:
                await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
                await self.settings.set(guild.id, "lol_schedule_last_sent_date", day.isoformat())
            except (discord.Forbidden, discord.HTTPException):
                logging.exception("Could not post Worlds schedule in guild %s", guild.id)

    @daily_post.before_loop
    async def before_daily_post(self) -> None:
        await self.bot.wait_until_ready()

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="(｡•́︿•̀｡) Solo admins",
                    description="Necesitas el permiso Administrar Servidor para configurar esto.",
                    color=discord.Color.orange(),
                ),
                ephemeral=True,
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(LolSchedule(bot))
