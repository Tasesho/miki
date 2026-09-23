from __future__ import annotations

import os
from pathlib import Path

import aiohttp
from aiohttp import web

from dashboard.repository import PostgresWelcomeCardRepository
from dashboard.welcome_cards import WelcomeCardSettings, WelcomeCardValidationError

STATIC_DIR = Path(__file__).parent / "static"


def _guild_id(value: str) -> int:
    try:
        guild_id = int(value)
    except ValueError as error:
        raise web.HTTPBadRequest(text="guild_id must be an integer") from error
    if guild_id <= 0:
        raise web.HTTPBadRequest(text="guild_id must be positive")
    return guild_id


async def get_welcome_card(request: web.Request) -> web.Response:
    settings = await request.app["welcome_cards"].get(_guild_id(request.match_info["guild_id"]))
    return web.json_response(settings.to_dict())


async def put_welcome_card(request: web.Request) -> web.Response:
    try:
        settings = WelcomeCardSettings.from_payload(await request.json())
    except (WelcomeCardValidationError, ValueError) as error:
        raise web.HTTPBadRequest(text=str(error)) from error
    saved = await request.app["welcome_cards"].save(
        _guild_id(request.match_info["guild_id"]), settings
    )
    return web.json_response(saved.to_dict())


async def send_test_card(request: web.Request) -> web.Response:
    guild_id = _guild_id(request.match_info["guild_id"])
    headers = {"Authorization": f"Bearer {request.app['internal_api_token']}"}
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{request.app['bot_internal_url']}/internal/guilds/{guild_id}/welcome-card/test",
                headers=headers,
            ) as response:
                body = await response.text()
    except aiohttp.ClientError as error:
        raise web.HTTPServiceUnavailable(text="Miki bot is unavailable.") from error
    if response.status != 200:
        raise web.HTTPBadRequest(text=body)
    return web.json_response({"sent": True})


async def dashboard_page(request: web.Request) -> web.FileResponse:
    return web.FileResponse(STATIC_DIR / "index.html")


async def setup_repository(app: web.Application) -> None:
    repository = app["welcome_cards"]
    await repository.connect()
    await repository.migrate()


async def close_repository(app: web.Application) -> None:
    await app["welcome_cards"].close()


def create_app(
    database_url: str,
    bot_internal_url: str = "http://miki-bot:8090",
    internal_api_token: str = "miki-local-development-token",
) -> web.Application:
    app = web.Application()
    app["welcome_cards"] = PostgresWelcomeCardRepository(database_url)
    app["bot_internal_url"] = bot_internal_url.rstrip("/")
    app["internal_api_token"] = internal_api_token
    app.router.add_get("/api/guilds/{guild_id}/welcome-card", get_welcome_card)
    app.router.add_put("/api/guilds/{guild_id}/welcome-card", put_welcome_card)
    app.router.add_post("/api/guilds/{guild_id}/welcome-card/test", send_test_card)
    app.router.add_get("/", dashboard_page)
    app.router.add_static("/assets", STATIC_DIR)
    app.on_startup.append(setup_repository)
    app.on_cleanup.append(close_repository)
    return app


def main() -> None:
    database_url = os.environ.get("POSTGRES_DATABASE_URL")
    if not database_url:
        raise RuntimeError("POSTGRES_DATABASE_URL is required for the dashboard.")
    web.run_app(
        create_app(
            database_url,
            os.getenv("BOT_INTERNAL_URL", "http://miki-bot:8090"),
            os.getenv("INTERNAL_API_TOKEN", "miki-local-development-token"),
        ),
        host="0.0.0.0",
        port=int(os.getenv("DASHBOARD_PORT", "8080")),
    )


if __name__ == "__main__":
    main()
