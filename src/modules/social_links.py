from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands


class SocialLinks(commands.Cog):
    social_link_group = app_commands.Group(
        name="social-link", description="Consulta tus relaciones de Social Link"
    )

    def __init__(self, bot):
        self.bot = bot
        self.service = bot.app.services.social_links

    @social_link_group.command(
        name="view", description="Muestra tu afinidad hacia un usuario de este servidor"
    )
    @app_commands.describe(user="Usuario objetivo; si se omite, muestra tus relaciones")
    async def view(self, interaction: discord.Interaction, user: discord.Member | None = None):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return

        if user is None:
            await self._send_list(interaction)
            return

        if user.id == interaction.user.id:
            await interaction.response.send_message(
                "(´・ω・`) No puedes crear un Social Link contigo mismo.", ephemeral=True
            )
            return
        if user.bot:
            await interaction.response.send_message(
                "(´・ω・`) Los bots no participan en los Social Links.", ephemeral=True
            )
            return

        link = await self.service.get_link(interaction.guild.id, interaction.user.id, user.id)
        await interaction.response.send_message(
            embed=self._build_link_embed(interaction.user, user, link)
        )

    @social_link_group.command(name="list", description="Muestra tus Social Links en este servidor")
    async def list(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return
        await self._send_list(interaction)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or self.bot.user is None:
            return
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        channel = guild.get_channel(payload.channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(payload.channel_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                return
        if not hasattr(channel, "fetch_message"):
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return

        target = message.author
        actor = guild.get_member(payload.user_id)
        if actor is not None and actor.bot:
            return
        if target.bot:
            return
        if target.id == payload.user_id:
            return

        result = await self.service.record_reaction(
            payload.guild_id,
            payload.user_id,
            target.id,
            payload.message_id,
        )
        if result and result["affinity_rank"] > 1:
            logging.debug(
                "Social Link advanced: guild=%s user=%s target=%s rank=%s",
                payload.guild_id,
                payload.user_id,
                target.id,
                result["affinity_rank"],
            )
        if result and result["rank_up"]:
            await self._announce_level_up(channel, payload.user_id, target.id, result)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot:
            return

        targets: dict[int, str] = {}
        referenced = await self._referenced_message(message)
        if (
            referenced is not None
            and referenced.author.id != message.author.id
            and self._is_valid_target(referenced.author)
        ):
            targets[referenced.author.id] = "reply"

        for target in message.mentions:
            if (
                target.id != message.author.id
                and target.id not in targets
                and self._is_valid_target(target)
            ):
                targets[target.id] = "mention"

        for target_id, action in targets.items():
            result = await self.service.record_message_action(
                message.guild.id,
                message.author.id,
                target_id,
                message.id,
                action,
            )
            if result and result["rank_up"]:
                await self._announce_level_up(message.channel, message.author.id, target_id, result)

    async def _referenced_message(self, message: discord.Message) -> discord.Message | None:
        if message.reference is None or message.reference.message_id is None:
            return None

        if isinstance(message.reference.resolved, discord.Message):
            return message.reference.resolved

        if not hasattr(message.channel, "fetch_message"):
            return None
        try:
            return await message.channel.fetch_message(message.reference.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return None

    def _is_valid_target(self, target) -> bool:
        return not target.bot

    async def _announce_level_up(
        self,
        channel,
        source_user_id: int,
        target_user_id: int,
        result: dict,
    ) -> None:
        embed = discord.Embed(
            title="¡Social Link subió de nivel!",
            description=(
                f"¡Felicidades <@{source_user_id}>! Tu relación con <@{target_user_id}> "
                f"ha subido al nivel **{result['affinity_rank']}**.\n\n"
                "Veo que hacen buenas migas (´▽`)"
            ),
            color=discord.Color.green(),
        )
        try:
            await channel.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            logging.debug("Could not announce Social Link level-up", exc_info=True)

    async def _send_list(self, interaction: discord.Interaction):
        links = await self.service.list_links(interaction.guild.id, interaction.user.id)
        embed = discord.Embed(
            title=f"[Social Links] {interaction.user.display_name}",
            description="Tus relaciones dirigidas en este servidor.",
            color=discord.Color.purple(),
        )
        if not links:
            embed.description = "Todavía no tienes Social Links registrados en este servidor."
        else:
            lines = []
            for link in links:
                target = interaction.guild.get_member(link["target_user_id"])
                if target is not None and target.bot:
                    continue
                target_name = target.display_name if target else f"Usuario {link['target_user_id']}"
                title = self.service.rank_title(link["affinity_rank"])
                lines.append(
                    f"**{target_name}** — Nivel {link['affinity_rank']} · {title} · "
                    f"{link['affinity_xp']} XP"
                )
            if lines:
                embed.add_field(name="Relaciones", value="\n".join(lines), inline=False)
            else:
                embed.description = "Todavía no tienes Social Links válidos en este servidor."
        await interaction.response.send_message(embed=embed)

    def _build_link_embed(self, source, target, link: dict) -> discord.Embed:
        rank = link["affinity_rank"]
        xp = link["affinity_xp"]
        current_progress, level_cost = self.service.progress(xp, rank)
        if level_cost is None:
            progress = "Nivel máximo alcanzado"
        else:
            progress = f"{current_progress}/{level_cost} XP para el siguiente nivel"

        embed = discord.Embed(
            title=f"[Social Link] {source.display_name} → {target.display_name}",
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Nivel", value=str(rank), inline=True)
        embed.add_field(name="Rango", value=self.service.rank_title(rank), inline=True)
        embed.add_field(name="Afinidad", value=f"{xp} XP", inline=True)
        embed.add_field(name="Progreso", value=progress, inline=False)
        return embed


async def setup(bot):
    await bot.add_cog(SocialLinks(bot))
