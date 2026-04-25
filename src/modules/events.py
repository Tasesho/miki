import discord
from discord.ext import commands
import time
from database.manager import DBManager

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()
        self.xp_cooldown = {}  # {user_id: timestamp}
        self.triggers = {
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

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" Miki está online: {self.bot.user}")
        await self.db.init_db()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        # Sistema de XP
        user_id = message.author.id
        current_time = time.time()
        last_xp_time = self.xp_cooldown.get(user_id, 0)
        
        if current_time - last_xp_time >= 60:
            usuario = await self.db.get_usuario(user_id)
            if usuario is None:
                await self.db.registrar_usuario(user_id, message.author.name)
                usuario = await self.db.get_usuario(user_id)
            
            xp_result = await self.db.actualizar_xp(user_id, 10)
            self.xp_cooldown[user_id] = current_time
            
            if xp_result and xp_result['subio_nivel']:
                await message.channel.send(
                    f"(´▽`){message.author.mention} - *¡Subiste al nivel {xp_result['nivel_actual']}!*"
                )

        # Triggers de respuesta (solo en servidores, no en DM)
        if isinstance(message.channel, discord.TextChannel):
            msg = message.content.lower()
            for key, resp in self.triggers.items():
                if key in msg:
                    await message.channel.send(resp)
                    break

async def setup(bot):
    await bot.add_cog(Events(bot))