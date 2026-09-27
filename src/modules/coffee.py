from __future__ import annotations

import asyncio
import logging
import random
from datetime import UTC, datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks


class Coffee(commands.Cog):
    coffee_group = app_commands.Group(name="cafe", description="Inventario y eventos de Miki")
    EVENT_EMOJI = "☕"

    def __init__(self, bot):
        self.bot = bot
        self.inventory = bot.app.services.inventory
        self.guild_settings = bot.app.services.guild_settings
        self.event_min_minutes = self.inventory.coffee_event_min_minutes
        self.event_max_minutes = self.inventory.coffee_event_max_minutes
        self.event_duration_seconds = self.inventory.coffee_event_duration_seconds
        self.min_wait_hours = self.inventory.coffee_event_min_wait_hours
        self.chance_denominator = self.inventory.coffee_event_chance_denominator
        self.active_events: dict[int, int] = {}
        self.available_at: dict[int, datetime] = {}
        self.last_roll_minute: dict[int, str] = {}
        self.event_locks: dict[int, asyncio.Lock] = {}
        self.expiry_tasks: set[asyncio.Task] = set()
        self.suelto_loop.start()

    def cog_unload(self) -> None:
        self.suelto_loop.cancel()
        for task in self.expiry_tasks:
            task.cancel()

    @coffee_group.command(name="inventario", description="Muestra tus consumibles y afinidad con Miki")
    async def inventory_command(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("(´；ω；`) Usa este comando en un servidor.", ephemeral=True)
            return
        count = await self.inventory.inventory(interaction.guild.id, interaction.user.id)
        affinity = await self.inventory.miki_affinity(interaction.guild.id, interaction.user.id)
        item = random.choice(self.inventory.ITEM_NAMES) if count else "Sin consumibles"
        await interaction.response.send_message(
            f"(｡•̀ᴗ-)✧ **Inventario de {interaction.user.display_name}**\n"
            f"Consumibles: **{count}** ({item})\n"
            f"Afinidad con Miki: **{affinity}**"
        )

    @coffee_group.command(name="usar", description="Consume un objeto y gana 50 XP global")
    async def use_command(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("(´；ω；`) Usa este comando en un servidor.", ephemeral=True)
            return
        result = await self.inventory.use_consumable(
            interaction.guild.id, interaction.user.id, interaction.user.name
        )
        if result is None:
            await interaction.response.send_message("(´・ω・`) No tienes consumibles.", ephemeral=True)
            return
        message = f"(≧▽≦) Consumible usado. Ganaste **50 XP**.\nInventario restante: **{await self.inventory.inventory(interaction.guild.id, interaction.user.id)}**"
        if result["subio_nivel"]:
            message += f"\n¡Subiste al nivel **{result['nivel_actual']}**!"
        await interaction.response.send_message(message)

    @coffee_group.command(name="regalar", description="Regala un consumible a otro usuario o a Miki")
    @app_commands.describe(usuario="Usuario destinatario; puedes elegir a Miki")
    async def gift_command(self, interaction: discord.Interaction, usuario: discord.Member):
        if interaction.guild is None:
            await interaction.response.send_message("(´；ω；`) Usa este comando en un servidor.", ephemeral=True)
            return
        if usuario.id == interaction.user.id:
            await interaction.response.send_message("(´・ω・`) No puedes regalarte un consumible.", ephemeral=True)
            return
        if usuario.bot and (self.bot.user is None or usuario.id != self.bot.user.id):
            await interaction.response.send_message("(´・ω・`) Solo puedes regalarle a otro usuario o a Miki.", ephemeral=True)
            return

        result = await self.inventory.gift_consumable(
            interaction.guild.id,
            interaction.user.id,
            usuario.id,
            f"gift:{interaction.id}",
            username=interaction.user.name,
            gift_xp=await self._coffee_config(interaction.guild.id, only_xp=True),
            target_is_miki=usuario.id == self.bot.user.id,
        )
        if result is None:
            await interaction.response.send_message("(´・ω・`) No tienes consumibles.", ephemeral=True)
            return
        if result.get("target") == "miki":
            text = f"(´▽`) Gracias por el regalo, {interaction.user.mention}. Mi afinidad contigo ahora es **{result['affinity_points']}**."
        else:
            text = (
                f"(｡•̀ᴗ-)✧ {interaction.user.mention} regaló un consumible a "
                f"{usuario.mention}. ¡Afinidad +1 y XP +100!"
            )
            if result.get("gift_xp_result", {}).get("subio_nivel"):
                text += f" ¡Subiste al nivel **{result['gift_xp_result']['nivel_actual']}**!"
        await interaction.response.send_message(text)

    @tasks.loop(seconds=10)
    async def suelto_loop(self):
        now = datetime.now(UTC)
        for guild in self.bot.guilds:
            if guild.id in self.active_events:
                continue
            cooldown_hours, event_duration, chance_denominator, _ = await self._coffee_config(
                guild.id
            )
            available_at = self.available_at.setdefault(
                guild.id, now + timedelta(hours=cooldown_hours)
            )
            if now < available_at:
                continue
            minute_key = now.strftime("%Y-%m-%dT%H:%M")
            if self.last_roll_minute.get(guild.id) == minute_key:
                continue
            self.last_roll_minute[guild.id] = minute_key
            if random.randint(1, chance_denominator) != 1:
                continue
            channel_id = await self.guild_settings.get_int(guild.id, "general_channel_id")
            channel = guild.get_channel(channel_id) if channel_id else None
            if (
                channel is None
                or not hasattr(channel, "send")
                or not channel.permissions_for(guild.me).send_messages
            ):
                continue
            try:
                message = await channel.send(
                    f"{self.EVENT_EMOJI} **¡Café Suelto!** {self.EVENT_EMOJI}\n"
                    f"Reacciona con {self.EVENT_EMOJI}; el primero gana un consumible. "
                    f"¡Tienes {event_duration:g} segundos! (ง'̀-'́)ง"
                )
                await message.add_reaction(self.EVENT_EMOJI)
                self.active_events[guild.id] = message.id
                task = asyncio.create_task(
                    self._expire_event(guild.id, message.channel.id, message.id, event_duration)
                )
                self.expiry_tasks.add(task)
                task.add_done_callback(self.expiry_tasks.discard)
            except (discord.Forbidden, discord.HTTPException):
                logging.exception("Could not publish coffee event in guild %s", guild.id)

    @suelto_loop.before_loop
    async def before_suelto_loop(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or self.bot.user is None:
            return
        if payload.user_id == self.bot.user.id:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        if str(payload.emoji) != self.EVENT_EMOJI:
            return
        async with self.event_locks.setdefault(guild.id, asyncio.Lock()):
            if self.active_events.get(guild.id) != payload.message_id:
                return
            self.active_events.pop(guild.id, None)
            cooldown_hours, _, _, _ = await self._coffee_config(guild.id)
            self.available_at[guild.id] = datetime.now(UTC) + timedelta(hours=cooldown_hours)
            total = await self.inventory.award_consumable(guild.id, payload.user_id)

        channel = guild.get_channel(payload.channel_id)
        if channel is None:
            return
        member = guild.get_member(payload.user_id)
        name = member.mention if member else f"<@{payload.user_id}>"
        await channel.send(
            f"(≧▽≦) ¡{name} ganó el Café Suelto! Consumibles disponibles: **{total}**."
        )

    async def _expire_event(
        self, guild_id: int, channel_id: int, message_id: int, duration_seconds: float
    ) -> None:
        await asyncio.sleep(duration_seconds)
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return

        async with self.event_locks.setdefault(guild_id, asyncio.Lock()):
            if self.active_events.get(guild_id) == message_id:
                self.active_events.pop(guild_id, None)
                cooldown_hours, _, _, _ = await self._coffee_config(guild_id)
                self.available_at[guild_id] = datetime.now(UTC) + timedelta(
                    hours=cooldown_hours
                )

        channel = guild.get_channel(channel_id)
        if channel is None or not hasattr(channel, "fetch_message"):
            return
        try:
            message = await channel.fetch_message(message_id)
            await message.delete()
            logging.info("Expired coffee event in guild %s", guild_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            logging.debug("Could not delete expired coffee event %s", message_id, exc_info=True)

    async def _coffee_config(
        self, guild_id: int, only_xp: bool = False
    ) -> tuple[float, float, int, int] | int:
        cooldown_hours = await self.guild_settings.get_int(
            guild_id, "coffee_event_min_wait_hours"
        )
        duration = await self.guild_settings.get_int(guild_id, "coffee_event_duration_seconds")
        chance_denominator = await self.guild_settings.get_int(
            guild_id, "coffee_event_chance_denominator"
        )
        gift_xp = await self.guild_settings.get_int(guild_id, "coffee_gift_xp")
        if only_xp:
            return gift_xp if gift_xp is not None else self.inventory.coffee_gift_xp
        return (
            cooldown_hours
            if cooldown_hours is not None
            else self.min_wait_hours,
            duration if duration is not None else self.event_duration_seconds,
            chance_denominator
            if chance_denominator is not None
            else self.chance_denominator,
            gift_xp if gift_xp is not None else self.inventory.coffee_gift_xp,
        )


async def setup(bot):
    await bot.add_cog(Coffee(bot))
