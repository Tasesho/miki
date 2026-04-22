import discord
from discord.ext import commands
import os
import requests
import re
from collections import Counter

class Services(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command()
    async def clima(self, ctx, ciudad: str, *, pais: str):
        api_key= os.getenv("WEATHER_API_KEY")
        print(f"Debug: La API Key cargada es: {api_key}") # Esto saldrá en 'docker logs'
        url= f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={ciudad},{pais}'
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            temp = datos["current"]["temp_c"]
            hum = datos["current"]["humidity"]
            cond = datos["current"]["condition"]["text"]
            await ctx.send(f"🌍 **{ciudad.title()}**: {temp}°C, {hum}% hum, {cond}")
        else:
            await ctx.send("❌ Ciudad no encontrada.")

    @commands.command()
    async def gif(self, ctx, *, query: str):
        api_key = os.getenv("GIPHY_API_KEY")
        url = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit=1&lang=es"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                gif_url = data['data'][0]['images']['original']['url']
                embed = discord.Embed(title=f"GIF: {query.title()}", color=discord.Color.red())
                embed.set_image(url=gif_url)
                await ctx.send(embed=embed)
        else:
            await ctx.send("Error al buscar el GIF :c.")

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

async def setup(bot):
    await bot.add_cog(Services(bot))