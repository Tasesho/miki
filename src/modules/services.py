from __future__ import annotations

import re
from collections import Counter

import discord
from discord import app_commands
from discord.ext import commands


class Services(commands.Cog):
    profile_group = app_commands.Group(
        name="profile", description="Comandos para gestionar tu perfil"
    )
    config_group = app_commands.Group(
        name="config",
        description="Comandos de configuración (Solo Admins)",
        default_permissions=discord.Permissions(manage_guild=True),
    )

    def __init__(self, bot):
        self.bot = bot
        self.gif_client = bot.app.services.gifs
        self.guild_settings = bot.app.services.guild_settings
        self.leaderboard_service = bot.app.services.leaderboard
        self.profile_service = bot.app.services.profiles
        self.weather_client = bot.app.services.weather

    @app_commands.command(name="clima", description="Obtén el clima actual de una ciudad")
    async def clima(self, interaction: discord.Interaction, ciudad_pais: str):
        await interaction.response.defer()
        ciudad, pais = self._parse_city_country(ciudad_pais.strip())
        weather = await self.weather_client.current(ciudad, pais)
        if weather is None:
            await interaction.followup.send("(´；ω；`) Ciudad no encontrada.")
            return

        embed = discord.Embed(
            title=f"[***] {weather.city}, {weather.country}",
            color=discord.Color.from_rgb(0, 191, 255),
        )
        embed.set_thumbnail(url=weather.icon_url)
        embed.add_field(name="[T] Temperatura", value=f"{weather.temperature_c}°C", inline=True)
        embed.add_field(
            name="(´・ω・`) Sensación térmica",
            value=f"{weather.feels_like_c}°C",
            inline=True,
        )
        embed.add_field(name="[~] Humedad", value=f"{weather.humidity}%", inline=True)
        embed.add_field(name="[≈] Condición", value=weather.condition, inline=False)
        embed.set_footer(text="Datos provistos por WeatherAPI")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="gif", description="Busca un GIF aleatorio")
    async def gif(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        gif_url = await self.gif_client.random_gif_url(query)
        if gif_url is None:
            await interaction.followup.send(f"(´；ω；`) No se encontraron GIFs para '{query}'.")
            return

        embed = discord.Embed(title=f"GIF: {query.title()}", color=discord.Color.red())
        embed.set_image(url=gif_url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="historial",
        description="Muestra las 10 palabras más repetidas en los últimos 100 mensajes",
    )
    async def historial(self, interaction: discord.Interaction):
        await interaction.response.defer()
        mensajes = [m.content.lower() async for m in interaction.channel.history(limit=100)]
        palabras = []
        for texto in mensajes:
            texto = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚüñ\s]", "", texto)
            palabras.extend(texto.split())

        contador = Counter(palabras)
        res = "**Top 10 palabras (100 msgs):**\n"
        for palabra, count in contador.most_common(10):
            res += f"• {palabra}: {count}\n"
        await interaction.followup.send(res)

    @profile_group.command(
        name="view", description="Mira tu perfil o el de alguien en este servidor"
    )
    async def profile_view(self, interaction: discord.Interaction, user: discord.Member = None):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return

        if user is None:
            user = interaction.user

        await interaction.response.defer()
        usuario = await self.profile_service.get_profile(interaction.guild.id, user)
        if usuario is None:
            if user.id == interaction.user.id:
                await self.profile_service.ensure_profile(interaction.guild.id, user)
                usuario = await self.profile_service.get_profile(interaction.guild.id, user)
            else:
                await interaction.followup.send(
                    f"(´・ω・`) Aún no veo un perfil de {user.mention} en este servidor.\n"
                    "Cuando esa persona escriba o use `!profile`, lo podré mostrar."
                )
                return

        await interaction.followup.send(embed=await self._build_profile_embed(user, usuario))

    @profile_group.command(name="edit", description="Mira qué campos puedes editar en tu perfil")
    async def profile_edit(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return

        fields = await self.profile_service.available_fields()
        field_names = ", ".join(field["key"] for field in fields)
        await interaction.response.send_message(
            "(´▽`) Puedes editar tu perfil por partes, sin rehacerlo completo.\n"
            f"Campos disponibles: **{field_names}**\n"
            "Ejemplos:\n"
            "`/profile set campo:github valor:octocat`\n"
            "`/profile set campo:website valor:https://mi-sitio.cl`"
        )

    @profile_group.command(
        name="set", description="Guarda o actualiza un campo en tu perfil social"
    )
    async def profile_set(self, interaction: discord.Interaction, campo: str, valor: str):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return

        field = await self.profile_service.set_field(
            interaction.guild.id, interaction.user, campo, valor
        )
        if field is None:
            fields = await self.profile_service.available_fields()
            field_names = ", ".join(item["key"] for item in fields)
            await interaction.response.send_message(
                "(´；ω；`) No conozco ese campo para el perfil.\n"
                f"Puedes usar: **{field_names}**\n"
                "Mira la lista con `/profile edit`.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"(´▽`) Listo, guardé **{field['display_name']}** en tu perfil de este servidor.\n"
            "Puedes revisarlo con `/profile view`."
        )

    @app_commands.command(name="leaderboard", description="Ranking actual de usuarios por nivel")
    async def leaderboard(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return

        leaderboard = await self.leaderboard_service.top_members(interaction.guild.id, limit=10)
        if not leaderboard:
            await interaction.response.send_message(
                "(´；ω；`) Aún no hay datos para el leaderboard.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Leaderboard (´▽`) - Top 10",
            description="Ranking actual de usuarios por nivel (๑•́ ω •̀๑)",
            color=discord.Color.gold(),
        )
        for idx, user in enumerate(leaderboard, 1):
            medal = self._medal(idx)
            embed.add_field(
                name=f"{medal} {user['username']}",
                value=f"Nivel: **{user['nivel']}** | XP: **{user['xp']}**",
                inline=False,
            )

        embed.set_footer(text="¡Sigue subiendo de nivel! (´▽`)")
        await interaction.response.send_message(embed=embed)

    @config_group.command(
        name="view", description="Muestra las opciones de configuración disponibles"
    )
    async def config_view(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return
        keys = ", ".join(self.guild_settings.available_keys())
        await interaction.response.send_message(
            "(ง'̀-'́)ง Configuración de este servidor.\n"
            f"Opciones disponibles: **{keys}**\n"
            "Ejemplos:\n"
            "`/config set clave:leaderboard_channel_id valor:<id_del_canal>`\n"
            "`/config set clave:xp_per_message valor:15`\n"
            "`/config set clave:xp_cooldown_seconds valor:60`"
        )

    @config_group.command(
        name="set", description="Cambia el valor de una configuración del servidor"
    )
    async def config_set(self, interaction: discord.Interaction, clave: str, valor: str):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return

        normalized_value = self._normalize_setting_value(clave, valor)
        was_set = await self.guild_settings.set(interaction.guild.id, clave, normalized_value)
        if not was_set:
            keys = ", ".join(self.guild_settings.available_keys())
            await interaction.response.send_message(
                "(´；ω；`) Esa configuración no existe todavía.\n"
                f"Puedes cambiar: **{keys}**\n"
                "Mira ejemplos con `/config view`.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"(´▽`) Guardé `{clave}` para este servidor.\n"
            "Los cambios se aplican solo aquí, no en otros servidores."
        )

    @config_group.command(
        name="leaderboard", description="Configura el canal y hora (0-23) del Top 10 diario"
    )
    @app_commands.describe(canal="Canal para el ranking", hora="Hora militar (ej: 14 para 2 PM)")
    async def config_leaderboard(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        hora: app_commands.Range[int, 0, 23],
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return

        await self.guild_settings.set(interaction.guild.id, "leaderboard_channel_id", str(canal.id))
        await self.guild_settings.set(interaction.guild.id, "leaderboard_hour", str(hora))

        await interaction.response.send_message(
            f"(´▽`) Listo. El leaderboard aparecerá a las **{hora}:00** en {canal.mention}.",
            ephemeral=True,
        )

    @config_group.command(
        name="fortune", description="Configura el canal y hora (0-23) de la Fortuna del Día"
    )
    @app_commands.describe(canal="Canal para la fortuna", hora="Hora militar (ej: 8 para 8 AM)")
    async def config_fortune(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        hora: app_commands.Range[int, 0, 23],
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "(´；ω；`) Usa este comando dentro de un servidor.", ephemeral=True
            )
            return

        await self.guild_settings.set(interaction.guild.id, "fortune_channel_id", str(canal.id))
        await self.guild_settings.set(interaction.guild.id, "fortune_hour", str(hora))

        await interaction.response.send_message(
            f"(´▽`) Listo. La fortuna diaria aparecerá a las **{hora}:00** en {canal.mention}.",
            ephemeral=True,
        )

    async def _build_profile_embed(self, user, usuario):
        xp_actual = usuario["xp"]
        nivel = usuario["nivel"]
        xp_para_proximo = nivel * 100
        barra_completa = 10
        barra_llena = int((xp_actual / xp_para_proximo) * barra_completa)
        barra_vacia = barra_completa - barra_llena
        barra = "[" + "■" * barra_llena + "□" * barra_vacia + "]"

        embed = discord.Embed(
            title=f"[Perfil] {usuario['username']}",
            color=discord.Color.from_rgb(100, 150, 255),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="[*] Nivel", value=str(nivel), inline=True)
        embed.add_field(name="[+] XP", value=f"{xp_actual}/{xp_para_proximo}", inline=True)
        embed.add_field(name="Progreso", value=barra, inline=False)
        embed.add_field(name="[=] Registro", value=usuario["fecha_registro"], inline=False)

        fields = await self.profile_service.available_fields()
        values = usuario.get("profile_fields", {})
        redes = []
        for field in fields:
            value = values.get(field["key"])
            if value:
                url = self.profile_service.format_profile_url(field, value)
                redes.append(f"[{field['display_name']}]({url})")

        if redes:
            embed.add_field(name="[~] Redes Sociales", value="\n".join(redes), inline=False)

        return embed

    def _normalize_setting_value(self, key: str, value: str) -> str:
        channel_settings = {
            "leaderboard_channel_id",
            "logs_channel_id",
            "welcome_channel_id",
        }
        if key in channel_settings:
            match = re.search(r"<#(\d+)>", value)
            if match:
                return match.group(1)
        return value.strip()

    def _parse_city_country(self, city_country: str) -> tuple[str, str]:
        parts = city_country.rsplit(" ", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return parts[0], "Chile"

    def _medal(self, position: int) -> str:
        if position == 1:
            return "🌟 1º"
        if position == 2:
            return "⭐ 2º"
        if position == 3:
            return "✨ 3º"
        return f"{position}º"

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "(´；ω；`) Esta parte es para admins del servidor.\n"
                    "Necesitas el permiso **Administrar Servidor**.",
                    ephemeral=True,
                )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Services(bot))
