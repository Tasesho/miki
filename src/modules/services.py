import discord
from discord.ext import commands
import os
import requests
import re
import random
from collections import Counter
from database.manager import DBManager

class Services(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()
    

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
        url = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit=50&lang=es"
        
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

    @commands.command()
    async def perfil(self, ctx, user: discord.User = None):
        """Muestra el perfil del usuario con XP y redes sociales"""
        if user is None:
            user = ctx.author
        
        usuario = await self.db.get_usuario(user.id)
        
        if usuario is None:
            if user == ctx.author:
                await ctx.send("(´・ω・`) Te he enviado un DM para configurar tu perfil.")
                try:
                    await self._setup_profile(ctx.author)
                except discord.Forbidden:
                    await ctx.send("(´；ω；`) No puedo enviar mensajes directos.")
            else:
                await ctx.send(f"(´；ω；`) {user.mention} no tiene un perfil registrado.")
            return
        
        # Mostrar perfil
        xp_actual = usuario['xp']
        nivel = usuario['nivel']
        xp_para_proximo = nivel * 100
        
        # Barra de progreso visual
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
        embed.add_field(name="[=] Registro", value=usuario['fecha_registro'], inline=False)
        
        # Redes sociales
        redes_text = ""
        if usuario['twitter']:
            redes_text += f"[Twitter]({usuario['twitter']})\n"
        if usuario['github']:
            redes_text += f"[GitHub]({usuario['github']})\n"
        if usuario['instagram']:
            redes_text += f"[Instagram]({usuario['instagram']})\n"
        if usuario['website']:
            redes_text += f"[Website]({usuario['website']})\n"
        
        if redes_text:
            embed.add_field(name="[~] Redes Sociales", value=redes_text.strip(), inline=False)
        
        await ctx.send(embed=embed)

    async def _setup_profile(self, user):
        """Asistente de configuración por DM"""
        try:
            dm_channel = await user.create_dm()
            
            # Mensaje introductorio
            await dm_channel.send(
                "(´・ω・`) Hola! Vamos a configurar tu perfil. Responde cada pregunta o escribe 'skip' para omitir.\n"
                "Tienes **5 minutos** para responder cada pregunta.\n_ _"
            )
            
            preguntas = [
                ("Twitter", "twitter"),
                ("GitHub", "github"),
                ("Instagram", "instagram"),
                ("Website", "website")
            ]
            
            respuestas = {}
            
            for nombre, campo in preguntas:
                await dm_channel.send(f"[?] {nombre} (link o 'skip'):")
                try:
                    msg = await self.bot.wait_for(
                        'message',
                        check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel),
                        timeout=300
                    )
                    contenido = msg.content.strip()
                    if contenido.lower() != 'skip':
                        respuestas[campo] = contenido
                        await dm_channel.send(f"[✓] {nombre} guardado!")
                    else:
                        respuestas[campo] = None
                        await dm_channel.send(f"[~] {nombre} omitido.")
                except TimeoutError:
                    await dm_channel.send("(´；ω；`) Se acabó el tiempo (5 min). Intenta de nuevo con !perfil")
                    return
            
            # Registrar usuario primero si no existe
            usuario_existente = await self.db.get_usuario(user.id)
            if usuario_existente is None:
                await self.db.registrar_usuario(user.id, user.name)
            
            # Guardar redes sociales
            await self.db.actualizar_redes(
                user.id,
                twitter=respuestas.get('twitter'),
                github=respuestas.get('github'),
                instagram=respuestas.get('instagram'),
                website=respuestas.get('website')
            )
            
            await dm_channel.send("(´▽`) [*] ¡Perfil configurado correctamente!")
            
        except discord.Forbidden:
            # Este error se maneja en el comando perfil directamente
            raise
        except Exception as e:
            print(f"Error en _setup_profile: {e}")
            try:
                await dm_channel.send(f"(´；ω；`) Ocurrió un error: {str(e)}")
            except:
                pass

    @commands.command(aliases=["top"])
    async def leaderboard(self, ctx):
        """Muestra el Top 10 de usuarios con más nivel y XP"""
        try:
            leaderboard = await self.db.get_leaderboard(limit=10)
            
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


async def setup(bot):
    await bot.add_cog(Services(bot))