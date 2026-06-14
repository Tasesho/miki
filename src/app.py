from __future__ import annotations

from dataclasses import dataclass

from config import Settings
from database.connection import Database
from database.migrator import MigrationRunner
from repositories.guild_repository import GuildRepository
from repositories.profile_repository import ProfileRepository
from repositories.setup_state_repository import SetupStateRepository
from repositories.user_repository import UserRepository
from services.activity_service import ActivityService
from services.external_clients import GifClient, WeatherClient
from services.guild_module_service import GuildModuleService
from services.guild_settings import GuildSettingsService
from services.leaderboard_service import LeaderboardService
from services.profile_service import ProfileService
from services.trigger_service import TriggerService
from setup.base import SetupManager
from setup.service import SetupStateService
from setup.ui import ChannelSetupView


@dataclass
class Repositories:
    guilds: GuildRepository
    profiles: ProfileRepository
    setup_state: SetupStateRepository
    users: UserRepository


@dataclass
class Services:
    activity: ActivityService
    guild_modules: GuildModuleService
    guild_settings: GuildSettingsService
    leaderboard: LeaderboardService
    profiles: ProfileService
    setup_state: SetupStateService
    setup_manager: SetupManager
    triggers: TriggerService
    weather: WeatherClient
    gifs: GifClient


class Application:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.database = Database(settings.database_path)
        self.migrations = MigrationRunner(self.database)

        self.repositories = Repositories(
            guilds=GuildRepository(self.database),
            profiles=ProfileRepository(self.database),
            setup_state=SetupStateRepository(self.database),
            users=UserRepository(self.database),
        )

        guild_settings = GuildSettingsService(self.repositories.guilds)

        setup_manager = SetupManager()
        setup_manager.register_module(
            "Canales Básicos",
            lambda guild_id, user_id: ChannelSetupView(guild_id, user_id, guild_settings),
        )

        self.services = Services(
            activity=ActivityService(self.repositories.users, guild_settings),
            guild_modules=GuildModuleService(self.repositories.guilds),
            guild_settings=guild_settings,
            leaderboard=LeaderboardService(self.repositories.users),
            profiles=ProfileService(self.repositories.users, self.repositories.profiles),
            setup_state=SetupStateService(self.repositories.setup_state),
            setup_manager=setup_manager,
            triggers=TriggerService(self.repositories.guilds),
            weather=WeatherClient(settings.weather_api_key),
            gifs=GifClient(settings.giphy_api_key),
        )

    async def startup(self) -> None:
        await self.migrations.run()
