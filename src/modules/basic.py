import discord
from discord import app_commands
from discord.ext import commands
import random


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.saludos = [
            "¡Hola!",
            "¡Saludos! Espero que tengas un buen día.",
            "¡Ey! ¿Qué andas haciendo?",
            "¡Hey! Me alegra verte por aquí.",
        ]

    @app_commands.command(name="talk", description="Miki te saluda aleatoriamente")
    async def talk(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(self.saludos))

    @app_commands.command(name="presentarse", description="Miki se presenta de manera oficial")
    async def presentarse(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="¡Hola a todos! (˶˃ ᵕ ˂˶) .ᐟ.ᐟ ",
            description=f"Soy **Miki**, un bot creado por {interaction.user.mention}. Estoy aquí para darle más vida al chat.",
            color=discord.Color.pink()
        )
        embed.set_footer(text="¡Usa /ayuda para ver mis comandos!")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="say", description="Miki repite lo que dices")
    async def say(self, interaction: discord.Interaction, mensaje: str):
        await interaction.response.send_message(mensaje)

    @app_commands.command(name="testdm", description="Prueba si el bot puede enviar DMs")
    async def testdm(self, interaction: discord.Interaction):
        try:
            dm = await interaction.user.create_dm()
            await dm.send("(´▽`) ¡Hola! Este es un mensaje de prueba del bot Miki. ¿Recibes este DM?")
            await interaction.response.send_message("(´▽`) He enviado un mensaje de prueba a tu DM!")
        except discord.Forbidden:
            await interaction.response.send_message("(´；ω；`) El bot NO puede enviar DMs. Verifica tu privacidad en Discord.")

    @app_commands.command(name="ayuda", description="Muestra la lista de comandos disponibles")
    async def ayuda(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="[INFO] (´▽`) Comandos Disponibles",
            description="Aquí están todas las funcionalidades de Miki (´・ω・`)",
            color=discord.Color.from_rgb(100, 150, 255)
        )
        
        embed.add_field(
            name="[GIF] (´▽`)ノ Búsqueda de GIFs",
            value="**/gif <búsqueda>**\nBusca un GIF aleatorio (Ex: /gif anime)\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[CLIMA] (´・_・`) Estado del Clima",
            value="**/clima <ciudad> [país]** o **/tiempo <ciudad>**\nObtén el clima actual\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[PROFILE] (๑•́ ω •̀๑) Tu Perfil",
            value="**/profile view** - Mira tu perfil o el de alguien\n**/profile edit** - Ve qué puedes editar\n**/profile set** - Guarda una red\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[MODS] (ง'̀-'́)ง Herramientas de Moderación",
            value="**/clear <numero>** (´▽`) Solo admins\nBorra los últimos N mensajes (máx: 100)\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[FORTUNA] (´▽`) Fortuna del Día",
            value="El bot envía frases de sabiduría cada 12 horas en general\nSon mensajes automáticos para motivarte (´▽`)\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[XP] (๑•́ ω •̀๑) Sistema de Experiencia",
            value="Ganas XP al conversar. Cada servidor tiene su propio progreso y ranking.",
            inline=False
        )

        embed.add_field(
            name="[CONFIG] Administración",
            value="**/config view** - Ver opciones\n**/config set** - Cambiar un ajuste\nRequiere permiso Administrar Servidor",
            inline=False
        )
        
        embed.add_field(
            name="[STATS] (´・_・`) Historial de Palabras",
            value="**/historial**\nMuestra las 10 palabras más repetidas (últimos 100 msgs)\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[TOOLS] (´▽`)ノ Herramientas Generales",
            value="**/say**, **/presentarse**, **/talk**, **/testdm**, **/ayuda**\n_ _",
            inline=False
        )
        
        embed.set_footer(text="¡Diviértete usando Miki! (´▽`)")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Basic(bot))
