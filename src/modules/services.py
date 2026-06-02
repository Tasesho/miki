import discord
from discord.ext import commands
import os
import requests
import re
import random
from collections import Counter
from database.manager import DBManager
from services.guild_settings import GuildSettingsService
from services.profile_service import ProfileService

class Services(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()
        self.profile_service = ProfileService(self.db)
        self.settings = GuildSettingsService(self.db)
    

    @commands.command()
    async def clima(self, ctx, *, ciudad_pais: str = None):
        if ciudad_pais is None:
            await ctx.send("[X] Uso: !clima <ciudad> [país]. Ejemplo: !clima Santiago Chile")
            return
        
        partes = ciudad_pais.rsplit(' ', 1)
        if len(partes) == 2:
            ciudad, pais = partes
        else:
            ciudad = partes[0]
            pais = "Chile"
        
        api_key = os.getenv("WEATHER_API_KEY")
        url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={ciudad},{pais}'
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            temp = datos["current"]["temp_c"]
            sensacion = datos["current"]["feelslike_c"]
            hum = datos["current"]["humidity"]
            cond = datos["current"]["condition"]["text"]
            icon = datos["current"]["condition"]["icon"]
            ciudad_nombre = datos["location"]["name"]
            pais_nombre = datos["location"]["country"]
            
            embed = discord.Embed(
                title=f"[***] {ciudad_nombre}, {pais_nombre}",
                color=discord.Color.from_rgb(0, 191, 255)
            )
            embed.set_thumbnail(url=f"https:{icon}")
            embed.add_field(name="[T] Temperatura", value=f"{temp}°C", inline=True)
            embed.add_field(name="(´・ω・`) Sensación térmica", value=f"{sensacion}°C", inline=True)
            embed.add_field(name="[~] Humedad", value=f"{hum}%", inline=True)
            embed.add_field(name="[≈] Condición", value=cond, inline=False)
            embed.set_footer(text="Datos provistos por WeatherAPI")
            await ctx.send(embed=embed)
        else:
            await ctx.send("(´；ω；`) Ciudad no encontrada.")

    @commands.command()
    async def gif(self, ctx, *, query: str):
        api_key = os.getenv("GIPHY_API_KEY")
        url = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit=10&lang=es"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                gif_random = random.choice(data['data'])
                gif_url = gif_random['images']['original']['url']
                embed = discord.Embed(title=f"GIF: {query.title()}", color=discord.Color.red())
                embed.set_image(url=gif_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"(´；ω；`) No se encontraron GIFs para '{query}'.")
        else:
            await ctx.send("(´；ω；`) Error al buscar el GIF...")

    @commands.command()
    async def historial(self, ctx):
        canal = ctx.channel
        mensajes = [m.content.lower() async for m in canal.history(limit=100)]
        palabras = []
        for texto in mensajes:
            texto = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚüñ\s]", "", texto)
            palabras.extend(texto.split())
        
        contador = Counter(palabras)
        res = "**Top 10 palabras (100 msgs):**\n"
        for p, c in contador.most_common(10):
            res += f"• {p}: {c}\n"
        await ctx.send(res)

    @commands.group(name="profile", aliases=["perfil"], invoke_without_command=True)
    async def profile(self, ctx, user: discord.Member = None):
        """Muestra el perfil del usuario con XP y campos sociales por servidor."""
        if ctx.guild is None:
            await ctx.send("(´；ω；`) Usa este comando dentro de un servidor.")
            return

        if user is None:
            user = ctx.author

        usuario = await self.profile_service.get_profile(ctx.guild.id, user)

        if usuario is None:
            if user == ctx.author:
                await self.profile_service.ensure_profile(ctx.guild.id, user)
                usuario = await self.profile_service.get_profile(ctx.guild.id, user)
            else:
                await ctx.send(
                    f"(´・ω・`) Aún no veo un perfil de {user.mention} en este servidor.\n"
                    "Cuando esa persona escriba o use `!profile`, lo podré mostrar."
                )
                return

        await ctx.send(embed=await self._build_profile_embed(user, usuario))

    @profile.command(name="edit")
    async def profile_edit(self, ctx):
        """Lista los campos editables del perfil."""
        if ctx.guild is None:
            await ctx.send("(´；ω；`) Usa este comando dentro de un servidor.")
            return

        fields = await self.profile_service.available_fields()
        field_names = ", ".join(field["key"] for field in fields)
        await ctx.send(
            "(´▽`) Puedes editar tu perfil por partes, sin rehacerlo completo.\n"
            f"Campos disponibles: **{field_names}**\n"
            "Ejemplos:\n"
            "`!profile set github octocat`\n"
            "`!profile set steam mi_usuario`\n"
            "`!profile set website https://mi-sitio.cl`"
        )

    @profile.command(name="set")
    async def profile_set(self, ctx, field_key: str = None, *, value: str = None):
        """Actualiza un campo individual del perfil."""
        if ctx.guild is None:
            await ctx.send("(´；ω；`) Usa este comando dentro de un servidor.")
            return
        if not field_key or not value:
            await ctx.send(
                "(´・ω・`) Me faltó saber qué quieres guardar.\n"
                "Usa: `!profile set <campo> <valor>`\n"
                "Ejemplos: `!profile set github octocat` o `!profile set steam mi_usuario`"
            )
            return

        field = await self.profile_service.set_field(ctx.guild.id, ctx.author, field_key, value)
        if field is None:
            fields = await self.profile_service.available_fields()
            field_names = ", ".join(item["key"] for item in fields)
            await ctx.send(
                "(´；ω；`) No conozco ese campo para el perfil.\n"
                f"Puedes usar: **{field_names}**\n"
                "Mira la lista con `!profile edit`."
            )
            return

        await ctx.send(
            f"(´▽`) Listo, guardé **{field['display_name']}** en tu perfil de este servidor.\n"
            "Puedes revisarlo con `!profile`."
        )

    @commands.command(aliases=["top"])
    async def leaderboard(self, ctx):
        """Muestra el Top 10 de usuarios con más nivel y XP"""
        if ctx.guild is None:
            await ctx.send("(´；ω；`) Usa este comando dentro de un servidor.")
            return
        try:
            leaderboard = await self.db.get_leaderboard(ctx.guild.id, limit=10)
            
            if not leaderboard:
                await ctx.send("(´；ω；`) Aún no hay datos para el leaderboard.")
                return
                
            embed = discord.Embed(
                title="Leaderboard (´▽`) - Top 10",
                description="Ranking actual de usuarios por nivel (๑•́ ω •̀๑)",
                color=discord.Color.gold()
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
                    inline=False
                )
            
            embed.set_footer(text="¡Sigue subiendo de nivel! (´▽`)")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"(´；ω；`) Error al obtener el leaderboard: {e}")

    @commands.group(name="config", invoke_without_command=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def config(self, ctx):
        """Muestra las claves de configuración disponibles."""
        if ctx.guild is None:
            await ctx.send("(´；ω；`) Usa este comando dentro de un servidor.")
            return
        keys = ", ".join(self.settings.available_keys())
        await ctx.send(
            "(ง'̀-'́)ง Configuración de este servidor.\n"
            f"Opciones disponibles: **{keys}**\n"
            "Ejemplos:\n"
            "`!config set leaderboard_channel_id #ranking`\n"
            "`!config set xp_per_message 15`\n"
            "`!config set xp_cooldown_seconds 60`"
        )

    @config.command(name="set")
    @commands.has_guild_permissions(manage_guild=True)
    async def config_set(self, ctx, key: str = None, *, value: str = None):
        if ctx.guild is None:
            await ctx.send("(´；ω；`) Usa este comando dentro de un servidor.")
            return
        if not key or value is None:
            await ctx.send(
                "(´・ω・`) Me faltó una clave o un valor para guardar.\n"
                "Usa: `!config set <clave> <valor>`\n"
                "Ejemplo: `!config set leaderboard_channel_id #ranking`"
            )
            return

        normalized_value = self._normalize_setting_value(ctx, key, value)
        was_set = await self.settings.set(ctx.guild.id, key, normalized_value)
        if not was_set:
            keys = ", ".join(self.settings.available_keys())
            await ctx.send(
                "(´；ω；`) Esa configuración no existe todavía.\n"
                f"Puedes cambiar: **{keys}**\n"
                "Mira ejemplos con `!config`."
            )
            return

        await ctx.send(
            f"(´▽`) Guardé `{key}` para este servidor.\n"
            "Los cambios se aplican solo aquí, no en otros servidores."
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
            color=discord.Color.from_rgb(100, 150, 255)
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

    def _normalize_setting_value(self, ctx, key, value):
        channel_settings = {
            "leaderboard_channel_id",
            "logs_channel_id",
            "welcome_channel_id",
        }
        if key in channel_settings and ctx.message.channel_mentions:
            return ctx.message.channel_mentions[0].id
        return value.strip()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "(´；ω；`) Esta parte es para admins del servidor.\n"
                "Necesitas el permiso **Manage Guild** para cambiar la configuración."
            )
            return
        raise error


async def setup(bot):
    await bot.add_cog(Services(bot))
