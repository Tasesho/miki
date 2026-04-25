import discord
from discord.ext import commands
from collections import Counter
import os
from config import TOKEN

class MikiBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # carga de modulos
        modules_path = os.path.join(os.path.dirname(__file__), "modules")
        for filename in os.listdir(modules_path):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    await self.load_extension(f'modules.{filename[:-3]}')
                    print(f" Módulo '{filename}' cargado exitosamente.")
                except Exception as e:
                    print(f"Error cargando '{filename}': {e}")
bot = MikiBot()
if __name__ == "__main__":
    print(f"iniciando Miki Bot...")
    bot.run(TOKEN)