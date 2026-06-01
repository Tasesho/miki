import discord
from discord.ext import commands, tasks
import time
import random
from database.manager import DBManager
from datetime import datetime
from services.guild_settings import GuildSettingsService


DEFAULT_TRIGGERS = {
    "hola": "ola   (●'◡'●)",
    "xao": "Hasta la Proxima   (˶˃ ᵕ ˂˶) .ᐟ.ᐟ ",
    "miki": "que paso?  ( °ヮ° ) ? ",
    "persona": "Persona referencia?? ",
    "vc": "Unete al vc ╰┈➤[VC]➤",
    "lit": "literalmente bruh...",
    "xd": "lmao  (¬‿¬ )",
    "F": "F en el chat  (╯﹏╰）",
    "sad": "Todo va a estar bien...  (っ´ω`)ﾉ(╥ω╥)",
    "miedo": "Tranqui, yo te protejo  (ง'̀-'́)ง",
    "odio": "No digas eso, el odio es malo  (；￣Д￣)",
    "te amo": "Yo... yo tambien?  (*/ω＼*)",
    "ayuda": "Si necesitas algo, usa !ayuda  ( °∀°)o",
    "pancito": "Invita un poco!  (っ˘ڡ˘ς)",
    "cafe": "Un cafecito para seguir programando  ( ￣▽￣)旦",
    "uwu": "nwn  (✿◡‿◡)",
    "pog": "POGGERS  ( °o°) !!",
    "afk": "No te tardes mucho...  (◕‿◕)",
    "lag": "Es el internet o es el server?  (╯°□°)╯︵ ┻━┻",
    "gg": "GG WP!  (っಠ‿ಠ)っ",
    "basado": "Factores.  (⌐■_■)",
    "miau": "Nyaa~  (＾◡＾)",
    "clima": "Usa !clima si quieres saber de verdad  ( ﾟヮﾟ)",
}

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()
        self.settings = GuildSettingsService(self.db)
        self.xp_cooldown = {}  # {(guild_id, user_id): timestamp}
        self.fortunes = [
            "La vida es como un café, su valor no se establece por lo caliente que está, sino por cuánto tiempo permanece en tu taza. (´▽`)",
            "No busques a alguien que resuelva tus problemas; busca a alguien que nunca te deje enfrentarlos solo. (ง'̀-'́)ง",
            "El éxito no es final, el fracaso no es fatal: lo que cuenta es el coraje de continuar. (๑•́ ω •̀๑)",
            "A veces lo pequeño es grande. La semilla más diminuta puede convertirse en el árbol más fuerte. (´▽｀)",
            "Tu tiempo es limitado, no lo gastes viviendo la vida de otro. (´・ω・`)",
            "Las personas que son lo suficientemente locas para creer que pueden cambiar el mundo, son las que lo hacen. (´▽`)ノ",
            "No puedes controlar el viento, pero sí puedes ajustar las velas. (~_~)",
            "Cada experto fue una vez un principiante. (´・_・`)",
            "La vida es un 10% lo que te sucede y un 90% cómo reaccionas. (´▽`)",
            "No es sobre tener tiempo, es sobre hacer tiempo. (๑•́ ω •̀๑)",
            "El mejor momento para plantar un árbol fue hace 20 años. El segundo mejor momento es ahora. (´▽｀)",
            "La felicidad no es el destino, es el viaje. (´▽`)ノ",
            "Cuando sientas que el mundo es demasiado, respira profundo y recuerda: tú has superado todo hasta ahora. (๑•́ ω •̀๑)",
            "La gratitud es el antídoto para la negatividad. m(_ _)m",
            "Tu única limitación eres tú mismo. Vuela alto. (´▽`)",
            "En medio de la dificultad reside la oportunidad. (´▽`)",
            "No esperes el momento perfecto, toma el momento e hazlo perfecto. (´・ω・`)",
            "La vida es demasiado corta para desperdiciarla en lo que no te importa. (´▽`)",
            "Sé la energía que quieres atraer. (´▽`)ノ",
            "Recuerda: eres más fuerte de lo que crees. (´▽`)",
            "Las metas sin planos siguen siendo deseos. Actúa hoy. (´▽`)",
            "El cambio comienza cuando decides que es hora de cambiar. (๑•́ ω •̀๑)",
            "Eres el artista de tu propia vida. Pinta tu obra maestra. (´▽`)",
            "No te rindas en el segundo acto. Las mejores historias tienen giros inesperados. (´・_・`)",
            "Tu potencial es infinito. Cree en ti. (´▽`)",
        ]
        # Iniciar tasks
        self.daily_leaderboard.start()
        self.fortune_loop.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" Miki está online: {self.bot.user}")
        await self.db.init_db()

    @tasks.loop(hours=24)
    async def daily_leaderboard(self):
        print("\n[LEADERBOARD] Ejecutando loop de leaderboard diario...", flush=True)
        try:
            if not self.bot.guilds:
                print("[LEADERBOARD] El bot no está en ningún servidor o no los ha cargado aún.", flush=True)
                return

            for guild in self.bot.guilds:
                channel_id = await self.settings.get_int(guild.id, "leaderboard_channel_id")
                if channel_id is None:
                    print(f"[LEADERBOARD] Sin canal configurado en {guild.name}", flush=True)
                    continue

                channel = guild.get_channel(channel_id)
                leaderboard = await self.db.get_leaderboard(guild.id, limit=10)

                if channel and leaderboard and channel.permissions_for(guild.me).send_messages:
                    await channel.send(embed=self._build_leaderboard_embed(leaderboard, daily=True))
                    print(f"[LEADERBOARD] Enviado a {guild.name} en #{channel.name}", flush=True)
                else:
                    print(f"[LEADERBOARD] Canal inválido o sin datos en {guild.name}", flush=True)
                    
        except Exception as e:
            print(f"[LEADERBOARD] ❌ Error Crítico: {e}", flush=True)

    @daily_leaderboard.before_loop
    async def before_daily_leaderboard(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=12)
    async def fortune_loop(self):
        print("\n[FORTUNA] Ejecutando loop de fortunas...", flush=True)
        try:
            if not self.bot.guilds:
                print("[FORTUNA] El bot no está en ningún servidor o no los ha cargado aún.", flush=True)
                return
                
            fortune = random.choice(self.fortunes)
            
            for guild in self.bot.guilds:
                canal_destino = None
                
                # 1. Filtro estricto: solo buscar canales que coincidan con estos sinónimos
                sinonimos = ['general', 'chat', 'lobby', 'principal']
                
                for channel in guild.text_channels:
                    if any(s in channel.name.lower() for s in sinonimos) and channel.permissions_for(guild.me).send_messages:
                        canal_destino = channel
                        break
                
                if canal_destino:
                    embed = discord.Embed(title="Fortuna del Día (´▽`)", description=fortune, color=discord.Color.purple())
                    await canal_destino.send(embed=embed)
                    print(f"[FORTUNA] ✅ Enviado a {guild.name} en #{canal_destino.name}", flush=True)
                else:
                    print(f"[FORTUNA] ❌ Ningún canal válido ({', '.join(sinonimos)}) en {guild.name}", flush=True)
                    
        except Exception as e:
            print(f"[FORTUNA] ❌ Error Crítico: {e}", flush=True)

    @fortune_loop.before_loop
    async def before_fortune_loop(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignorar mensajes del bot o de otros bots
        if message.author.id == self.bot.user.id or message.author.bot:
            return
        if message.guild is None:
            return

        # Sistema de XP
        guild_id = message.guild.id
        user_id = message.author.id
        current_time = time.time()
        cooldown_key = (guild_id, user_id)
        xp_cooldown_seconds = await self.settings.get_int(guild_id, "xp_cooldown_seconds")
        xp_per_message = await self.settings.get_int(guild_id, "xp_per_message")
        last_xp_time = self.xp_cooldown.get(cooldown_key, 0)
        
        if current_time - last_xp_time >= xp_cooldown_seconds:
            xp_result = await self.db.actualizar_xp(
                guild_id,
                user_id,
                message.author.name,
                xp_per_message,
            )
            self.xp_cooldown[cooldown_key] = current_time
            
            if xp_result and xp_result['subio_nivel']:
                await message.channel.send(
                    f"(´▽`){message.author.mention} - *¡Subiste al nivel {xp_result['nivel_actual']}!*"
                )

        # Triggers de respuesta (solo en servidores, no en DM)
        if isinstance(message.channel, discord.TextChannel):
            msg = message.content.lower()
            triggers = await self.db.get_guild_triggers(guild_id)
            if not triggers:
                triggers = DEFAULT_TRIGGERS
            for key, resp in triggers.items():
                if key in msg:
                    await message.channel.send(resp)
                    break

    def _build_leaderboard_embed(self, leaderboard, daily=False):
        title = "Leaderboard Diario (´▽`) - Top 10" if daily else "Leaderboard (´▽`) - Top 10"
        embed = discord.Embed(
            title=title,
            description="Ranking de usuarios por nivel (๑•́ ω •̀๑)",
            color=discord.Color.gold(),
            timestamp=datetime.now()
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
        return embed

async def setup(bot):
    await bot.add_cog(Events(bot))
