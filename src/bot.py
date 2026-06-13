from __future__ import annotations

import logging
import os

import discord
from discord.ext import commands

from app import Application
from config import Settings


class MikiBot(commands.Bot):
    def __init__(self, app: Application):
        self.app = app
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=app.settings.command_prefix,
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        await self.app.startup()
        modules_path = os.path.join(os.path.dirname(__file__), "modules")
        for filename in sorted(os.listdir(modules_path)):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"modules.{filename[:-3]}"
                try:
                    await self.load_extension(module_name)
                    logging.info("Loaded module %s", module_name)
                except Exception:
                    logging.exception("Error loading module %s", module_name)

        synced = await self.tree.sync()
        logging.info("Synced %d slash commands", len(synced))

    async def on_ready(self) -> None:
        logging.info("Miki is online as %s", self.user)


def main() -> None:
    runtime_settings = Settings.from_env(require_token=True)
    logging.basicConfig(
        level=runtime_settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    app = Application(runtime_settings)
    bot = MikiBot(app)
    bot.run(runtime_settings.discord_token)


if __name__ == "__main__":
    main()
