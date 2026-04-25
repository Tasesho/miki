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

async def setup(bot):
    await bot.add_cog(Weather(bot))