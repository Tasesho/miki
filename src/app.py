from __future__ import annotations

from dataclasses import dataclass

from config import Settings
from dashboard.repository import PostgresWelcomeCardRepository
from database.connection import Database
from database.migrator import MigrationRunner
from repositories.guild_repository import GuildRepository
from repositories.profile_repository import ProfileRepository
from repositories.setup_state_repository import SetupStateRepository
from repositories.social_link_repository import SocialLinkRepository
from repositories.user_repository import UserRepository
from services.activity_service import ActivityService
from services.external_clients import GifClient, WeatherClient
from services.guild_module_service import GuildModuleService
from services.guild_settings import GuildSettingsService
from services.leaderboard_service import LeaderboardService
from services.profile_service import ProfileService
from services.social_link_service import SocialLinkService
from services.trigger_service import TriggerService
from services.welcome_card_service import WelcomeCardService
from setup.base import SetupManager
from setup.service import SetupStateService
from setup.ui import ChannelSetupView


@dataclass
class Repositories:
    guilds: GuildRepository
    profiles: ProfileRepository
    setup_state: SetupStateRepository
    social_links: SocialLinkRepository
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
    social_links: SocialLinkService
    triggers: TriggerService
    weather: WeatherClient
    gifs: GifClient
    welcome_cards: WelcomeCardService


class Application:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.database = Database(settings.database_path)
        self.migrations = MigrationRunner(self.database)
        self.welcome_cards_repository = (
            PostgresWelcomeCardRepository(settings.postgres_database_url)
            if settings.postgres_database_url
            else None
        )

        self.repositories = Repositories(
            guilds=GuildRepository(self.database),
            profiles=ProfileRepository(self.database),
            setup_state=SetupStateRepository(self.database),
            social_links=SocialLinkRepository(
                self.database,
                base_level_xp=settings.social_link_base_xp,
                reaction_xp=settings.social_link_reaction_xp,
            ),
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
            social_links=SocialLinkService(
                self.repositories.social_links,
                guild_settings,
                base_level_xp=settings.social_link_base_xp,
            ),
            triggers=TriggerService(self.repositories.guilds),
            weather=WeatherClient(settings.weather_api_key),
            gifs=GifClient(settings.giphy_api_key),
            welcome_cards=WelcomeCardService(self.welcome_cards_repository),
        )

    async def startup(self) -> None:
        await self.migrations.run()
        if self.welcome_cards_repository is not None:
            await self.welcome_cards_repository.connect()
            await self.welcome_cards_repository.migrate()

    async def shutdown(self) -> None:
        if self.welcome_cards_repository is not None:
            await self.welcome_cards_repository.close()
