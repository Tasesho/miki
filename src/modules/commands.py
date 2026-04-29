import discord
from discord.ext import commands
import requests

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "TU_API_KEY_AQUI"  # Lo ideal es sacarlo de config.py
        self.base_url = "http://api.openweathermap.org/data/2.5/weather?"

    def get_weather_data(self, city_name):
        """Método auxiliar para pegarle a la API"""
        complete_url = f"{self.base_url}appid={self.api_key}&q={city_name}&units=metric&lang=es"
        response = requests.get(complete_url)
        return response.json()

    @commands.command(name="tiempo", help="Muestra el clima de una ciudad.")
    async def tiempo(self, ctx, *, ciudad: str):
        # 1. Obtenemos los datos (Lógica de negocio)
        data = self.get_weather_data(ciudad)

        if data.get("cod") != "404":
            main = data["main"]
            weather = data["weather"][0]
            
            # 2. Construcción del Embed (Lógica de Interfaz/UI)
            embed = discord.Embed(
                title=f"Clima en {data['name']}, {data['sys']['country']}",
                color=discord.Color.blue(),
                description=weather["description"].capitalize()
            )
            embed.add_field(name="Temperatura", value=f"{main['temp']}°C", inline=True)
            embed.add_field(name="Humedad", value=f"{main['humidity']}%", inline=True)
            embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png")
            embed.set_footer(text=f"Solicitado por {ctx.author.name}")

            await ctx.send(embed=embed)
        else:
            await ctx.send(f" No pude encontrar la ciudad: **{ciudad}**")

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear", help="Borra los últimos N mensajes del canal")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, numero: int):
        """
        Borra los últimos N mensajes del canal (incluye el comando)
        Solo funciona si el usuario es administrador
        El bot necesita permiso de 'Manage Messages'
        """
        # Validar que el número sea positivo
        if numero <= 0:
            await ctx.send("(´；ω；`) El número debe ser mayor a 0")
            return
        
        # Limitar a máximo 100 mensajes por seguridad
        if numero > 100:
            await ctx.send("(´；ω；`) El máximo es 100 mensajes")
            numero = 100
        
        try:
            # Borrar N+1 mensajes (N + el mensaje del comando)
            deleted = await ctx.channel.purge(limit=numero + 1)
            
            # Enviar confirmación (este mensaje se autoborra en 3 segundos)
            confirmation = await ctx.send(f"(´▽`) Borrados {len(deleted) - 1} mensajes")
            await confirmation.delete(delay=3)
        except discord.Forbidden:
            await ctx.send("(´；ω；`) No tengo permisos para borrar mensajes en este canal")
        except Exception as e:
            await ctx.send(f"(´；ω；`) Error: {e}")

async def setup(bot):
    await bot.add_cog(Weather(bot))
    await bot.add_cog(Moderation(bot))