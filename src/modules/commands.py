from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weather_client = bot.app.services.weather

    @app_commands.command(name="tiempo", description="Muestra el clima de una ciudad")
    async def tiempo(self, interaction: discord.Interaction, ciudad: str):
        await interaction.response.defer()
        weather = await self.weather_client.current(ciudad)
        if weather is None:
            await interaction.followup.send(f" No pude encontrar la ciudad: **{ciudad}**")
            return

        embed = discord.Embed(
            title=f"Clima en {weather.city}, {weather.country}",
            color=discord.Color.blue(),
            description=weather.condition.capitalize(),
        )
        embed.add_field(name="Temperatura", value=f"{weather.temperature_c}°C", inline=True)
        embed.add_field(name="Humedad", value=f"{weather.humidity}%", inline=True)
        embed.set_thumbnail(url=weather.icon_url)
        embed.set_footer(text=f"Solicitado por {interaction.user.name}")
        await interaction.followup.send(embed=embed)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Borra los últimos N mensajes del canal")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, numero: int):
        if numero <= 0:
            await interaction.response.send_message("(´；ω；`) El número debe ser mayor a 0", ephemeral=True)
            return

        if numero > 100:
            await interaction.response.send_message("(´；ω；`) El máximo es 100 mensajes", ephemeral=True)
            numero = 100

        await interaction.response.defer(ephemeral=True)
        try:
            # Para Slash commands no hay mensaje de comando que borrar, limit=numero es exacto.
            deleted = await interaction.channel.purge(limit=numero)
            await interaction.followup.send(f"(´▽`) Borrados {len(deleted)} mensajes")
        except discord.Forbidden:
            await interaction.followup.send("(´；ω；`) No tengo permisos para borrar mensajes en este canal")
        except Exception as exc:
            await interaction.followup.send(f"(´；ω；`) Error: {exc}")

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("(´；ω；`) No tienes permisos para usar esto.", ephemeral=True)
        elif isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message("(´；ω；`) No tengo permisos suficientes.", ephemeral=True)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Weather(bot))
    await bot.add_cog(Moderation(bot))
