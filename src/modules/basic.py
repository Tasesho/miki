import discord
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

    @commands.command()
    async def talk(self, ctx):
        await ctx.send(random.choice(self.saludos))

    @commands.command()
    async def presentarse(self, ctx):
        embed = discord.Embed(
            title="¡Hola a todos! (˶˃ ᵕ ˂˶) .ᐟ.ᐟ ",
            description=f"Soy **Miki**, un bot creado por {ctx.author.mention}. Estoy aquí para darle más vida al chat.",
            color=discord.Color.pink()
        )
        embed.set_footer(text="¡Usa !ayuda para ver mis comandos!")
        await ctx.send(embed=embed)
    
    @commands.command()
    async def say(self, ctx, *, mensaje: str):
        await ctx.send(mensaje)

    @commands.command()
    async def testdm(self, ctx):
        """Prueba si el bot puede enviar DMs"""
        try:
            dm = await ctx.author.create_dm()
            await dm.send("(´▽`) ¡Hola! Este es un mensaje de prueba del bot Miki. ¿Recibes este DM?")
            await ctx.send("(´▽`) He enviado un mensaje de prueba a tu DM!")
        except discord.Forbidden:
            await ctx.send("(´；ω；`) El bot NO puede enviar DMs. Verifica tu privacidad en Discord.")

    @commands.command()
    async def ayuda(self, ctx):
        embed = discord.Embed(
            title="[INFO] Comandos Disponibles",
            description="Aquí están todas las funcionalidades de Miki",
            color=discord.Color.from_rgb(100, 150, 255)
        )
        
        embed.add_field(
            name="[GIF] Búsqueda de GIFs",
            value="**!gif <búsqueda>**\nBusca un GIF aleatorio (Ex: !gif anime)\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[CLIMA] Estado del Clima",
            value="**!clima <ciudad> [país]**\nObtén el clima actual (Default: Chile)\nEj: !clima Santiago o !clima Barcelona España\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[*] Perfil de Usuario",
            value="**!perfil [@usuario]**\nVe tu perfil o el de otro usuario con XP y redes sociales\nPrimera vez: Configura tus redes por DM automáticamente\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[+] Sistema de XP",
            value="Ganas **10 XP por mensaje** (cooldown: 60 segundos)\nFormula: Nivel actual × 100 = XP para siguiente nivel\nRecibe notificación automática al subir de nivel\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[~] Historial de Palabras",
            value="**!historial**\nMuestra las 10 palabras más repetidas (últimos 100 msgs)\n_ _",
            inline=False
        )
        
        embed.add_field(
            name="[*] Herramientas Generales",
            value="**!say <mensaje>** - Repite tu mensaje\n**!presentarse** - Presentación de Miki\n**!talk** - Saludo aleatorio\n**!ayuda** - Esta lista\n_ _",
            inline=False
        )
        
        embed.set_footer(text="¡Diviértete usando Miki! (´▽`)")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Basic(bot))