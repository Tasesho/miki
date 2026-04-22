import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.triggers = {
            "hola": "ola   (●'◡'●)",
            "xao": "Hasta la Proxima   (˶˃ ᵕ ˂˶) .ᐟ.ᐟ ",
            "miki": "que paso?  ( °ヮ° ) ? ",
            "persona": "Persona referencia?? ",
            "vc": "Unete al vc ╰┈➤🔊-vc-➤",
            "lit": "literalmente bruh...",
            "xd": "porque el desagrado? (╥﹏╥)",
            "freaky": "𝓯𝓻𝓮𝓪𝓴𝔂",
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" Miki está online: {self.bot.user}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        msg = message.content.lower()
        for key, resp in self.triggers.items():
            if key in msg:
                await message.channel.send(resp)
                break

async def setup(bot):
    await bot.add_cog(Events(bot))