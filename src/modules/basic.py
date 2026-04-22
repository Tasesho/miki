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
    async def ayuda(self, ctx):
        respuesta = """```
Comandos disponibles:
- !gif        - Busca un GIF (Ex: !gif anime)
- !clima      - Clima actual (!clima Ciudad Pais)
- !historial  - Palabras más repetidas (últimos 100 msgs)
- !say        - Repite tu mensaje.
- !presentarse - Presentación de Miki.
- !talk       - Saludo aleatorio.
- !ayuda      - Esta lista.
```"""
        await ctx.send(respuesta)

async def setup(bot):
    await bot.add_cog(Basic(bot))