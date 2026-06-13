from __future__ import annotations

import logging
import random
from datetime import datetime

import discord
from discord.ext import commands, tasks


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity = bot.app.services.activity
        self.guild_settings = bot.app.services.guild_settings
        self.leaderboard_service = bot.app.services.leaderboard
        self.triggers = bot.app.services.triggers
        self.fortunes = [
            "La vida es como un café, su valor no se establece por lo caliente que está, sino por cuánto tiempo permanece en tu taza. (´▽`)",
            "No busques a alguien que resuelva tus problemas; busca a alguien que nunca te deje enfrentarlos solo. (ง'̀-'́)ง",
            "El éxito no es final, el fracaso no es fatal: lo que cuenta es el coraje de continuar. (๑•́ ω •̀๑)",
            "A veces lo pequeño es grande. La semilla más diminuta puede convertirse en el árbol más fuerte. (´▽｀)",
            "Tu tiempo es limitado, no lo gastes viviendo la vida de otro. (´・ω・`)",
            "Las personas que son lo suficientemente locas para creer que pueden cambiar el mundo, son las que lo hacen. (´▽`)ノ",
            "No puedes controlar el viento, pero sí puedes ajustar las velas. (~_~)",
            "Cada experto fue una vez un principiante. (´・_・`)",
            "La vida es un 10% lo que te sucede y un 90% cómo reaccionas. (´▽`)",
            "No es sobre tener tiempo, es sobre hacer tiempo. (๑•́ ω •̀๑)",
            "El mejor momento para plantar un árbol fue hace 20 años. El segundo mejor momento es ahora. (´▽｀)",
            "La felicidad no es el destino, es el viaje. (´▽`)ノ",
            "Cuando sientas que el mundo es demasiado, respira profundo y recuerda: tú has superado todo hasta ahora. (๑•́ ω •̀๑)",
            "La gratitud es el antídoto para la negatividad. m(_ _)m",
            "Tu única limitación eres tú mismo. Vuela alto. (´▽`)",
            "En medio de la dificultad reside la oportunidad. (´▽`)",
            "No esperes el momento perfecto, toma el momento e hazlo perfecto. (´・ω・`)",
            "La vida es demasiado corta para desperdiciarla en lo que no te importa. (´▽`)",
            "Sé la energía que quieres atraer. (´▽`)ノ",
            "Recuerda: eres más fuerte de lo que crees. (´▽`)",
            "Las metas sin planos siguen siendo deseos. Actúa hoy. (´▽`)",
            "El cambio comienza cuando decides que es hora de cambiar. (๑•́ ω •̀๑)",
            "Eres el artista de tu propia vida. Pinta tu obra maestra. (´▽`)",
            "No te rindas en el segundo acto. Las mejores historias tienen giros inesperados. (´・_・`)",
            "Tu potencial es infinito. Cree en ti. (´▽`)",
        ]
        self.daily_leaderboard.start()
        self.fortune_loop.start()

    def cog_unload(self) -> None:
        self.daily_leaderboard.cancel()
        self.fortune_loop.cancel()

    @tasks.loop(hours=24)
    async def daily_leaderboard(self):
        logging.info("Running daily leaderboard loop")
        for guild in self.bot.guilds:
            channel_id = await self.guild_settings.get_int(guild.id, "leaderboard_channel_id")
            if channel_id is None:
                logging.info("No leaderboard channel configured in %s", guild.name)
                continue

            channel = guild.get_channel(channel_id)
            leaderboard = await self.leaderboard_service.top_members(guild.id, limit=10)

            if channel and leaderboard and channel.permissions_for(guild.me).send_messages:
                await channel.send(embed=self._build_leaderboard_embed(leaderboard, daily=True))
                logging.info("Sent leaderboard to %s in #%s", guild.name, channel.name)
            else:
                logging.info("Invalid leaderboard channel or no data in %s", guild.name)

    @daily_leaderboard.before_loop
    async def before_daily_leaderboard(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=12)
    async def fortune_loop(self):
        logging.info("Running fortune loop")
        if not self.bot.guilds:
            return

        fortune = random.choice(self.fortunes)
        synonyms = ["general", "chat", "lobby", "principal"]

        for guild in self.bot.guilds:
            target_channel = None
            for channel in guild.text_channels:
                if any(item in channel.name.lower() for item in synonyms) and channel.permissions_for(
                    guild.me
                ).send_messages:
                    target_channel = channel
                    break

            if target_channel:
                embed = discord.Embed(
                    title="Fortuna del Día (´▽`)",
                    description=fortune,
                    color=discord.Color.purple(),
                )
                await target_channel.send(embed=embed)
                logging.info("Sent fortune to %s in #%s", guild.name, target_channel.name)
            else:
                logging.info("No valid fortune channel in %s", guild.name)

    @fortune_loop.before_loop
    async def before_fortune_loop(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id or message.author.bot:
            return
        if message.guild is None:
            return

        xp_result = await self.activity.record_message(
            message.guild.id,
            message.author.id,
            message.author.name,
        )
        if xp_result and xp_result["subio_nivel"]:
            await message.channel.send(
                f"(´▽`){message.author.mention} - *¡Subiste al nivel {xp_result['nivel_actual']}!*"
            )

        if isinstance(message.channel, discord.TextChannel):
            response = await self.triggers.match_response(message.guild.id, message.content)
            if response:
                await message.channel.send(response)

    def _build_leaderboard_embed(self, leaderboard, daily=False):
        title = "Leaderboard Diario (´▽`) - Top 10" if daily else "Leaderboard (´▽`) - Top 10"
        embed = discord.Embed(
            title=title,
            description="Ranking de usuarios por nivel (๑•́ ω •̀๑)",
            color=discord.Color.gold(),
            timestamp=datetime.now(),
        )

        for idx, user in enumerate(leaderboard, 1):
            if idx == 1:
                medal = "🌟 1º"
            elif idx == 2:
                medal = "⭐ 2º"
            elif idx == 3:
                medal = "✨ 3º"
            else:
                medal = f"{idx}º"
            embed.add_field(
                name=f"{medal} {user['username']}",
                value=f"Nivel: **{user['nivel']}** | XP: **{user['xp']}**",
                inline=False,
            )

        embed.set_footer(text="¡Sigue subiendo de nivel! (´▽`)")
        return embed


async def setup(bot):
    await bot.add_cog(Events(bot))
