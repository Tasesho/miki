from __future__ import annotations

import logging
import os
from hmac import compare_digest

import discord
from aiohttp import web
from discord.ext import commands

from app import Application
from config import Settings


class MikiBot(commands.Bot):
    def __init__(self, app: Application):
        self.app = app
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            command_prefix=app.settings.command_prefix,
            intents=intents,
            help_command=None,
        )
        self.internal_runner: web.AppRunner | None = None

    async def setup_hook(self) -> None:
        await self.app.startup()
        await self._start_internal_api()
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
        logging.info("Miki is online as %s; Discord authentication succeeded", self.user)

    async def close(self) -> None:
        if self.internal_runner is not None:
            await self.internal_runner.cleanup()
        await self.app.shutdown()
        await super().close()

    async def _start_internal_api(self) -> None:
        api = web.Application()
        api.router.add_post("/internal/guilds/{guild_id}/welcome-card/test", self._send_test_card)
        self.internal_runner = web.AppRunner(api)
        await self.internal_runner.setup()
        site = web.TCPSite(self.internal_runner, "0.0.0.0", 8090)
        await site.start()
        logging.info("Dashboard test-card endpoint listening on internal port 8090")

    async def _send_test_card(self, request: web.Request) -> web.Response:
        expected = f"Bearer {self.app.settings.internal_api_token}"
        if not compare_digest(request.headers.get("Authorization", ""), expected):
            raise web.HTTPUnauthorized(text="Invalid internal API credential.")
        try:
            guild_id = int(request.match_info["guild_id"])
        except ValueError as error:
            raise web.HTTPBadRequest(text="guild_id must be an integer") from error
        guild = self.get_guild(guild_id)
        if guild is None:
            raise web.HTTPNotFound(text="Miki is not in this server.")
        logging.info("Welcome-card test requested for guild %s", guild_id)
        if not await self.app.services.welcome_cards.send_test(guild):
            raise web.HTTPConflict(
                text="Card is disabled, channel is unavailable, or permissions are missing."
            )
        return web.json_response({"sent": True})


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
