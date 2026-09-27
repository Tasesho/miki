from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

VALID_ENVIRONMENTS = {"development", "staging", "production"}


@dataclass(frozen=True)
class Settings:
    environment: str
    discord_token: str
    database_path: str
    postgres_database_url: str | None
    internal_api_token: str
    command_prefix: str
    weather_api_key: str | None
    giphy_api_key: str | None
    log_level: str
    social_link_base_xp: int
    social_link_reaction_xp: int
    coffee_event_min_minutes: float
    coffee_event_max_minutes: float
    coffee_event_duration_seconds: float
    coffee_event_min_wait_hours: float
    coffee_event_chance_denominator: int

    @classmethod
    def from_env(cls, *, require_token: bool = False) -> Settings:
        load_dotenv()

        environment = os.getenv("MIKI_ENV", "development").lower()
        if environment not in VALID_ENVIRONMENTS:
            valid = ", ".join(sorted(VALID_ENVIRONMENTS))
            raise ValueError(f"MIKI_ENV must be one of: {valid}")

        token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN") or ""
        if require_token and not token:
            raise ValueError("DISCORD_TOKEN is not configured.")

        database_path = os.getenv("DATABASE_PATH", "data/miki.db")
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        default_social_link_base_xp = "100"
        social_link_base_xp = int(os.getenv("SOCIAL_LINK_BASE_XP", default_social_link_base_xp))
        social_link_reaction_xp = int(os.getenv("SOCIAL_LINK_REACTION_XP", "1"))
        if social_link_base_xp <= 0 or social_link_reaction_xp <= 0:
            raise ValueError("Social Link XP settings must be positive integers.")

        coffee_event_min_minutes = float(os.getenv("COFFEE_EVENT_MIN_MINUTES", "240"))
        coffee_event_max_minutes = float(os.getenv("COFFEE_EVENT_MAX_MINUTES", "300"))
        if coffee_event_min_minutes <= 0 or coffee_event_max_minutes < coffee_event_min_minutes:
            raise ValueError("Coffee event interval settings are invalid.")
        coffee_event_duration_seconds = float(os.getenv("COFFEE_EVENT_DURATION_SECONDS", "30"))
        if coffee_event_duration_seconds <= 0:
            raise ValueError("Coffee event duration must be positive.")
        coffee_event_min_wait_hours = float(os.getenv("COFFEE_EVENT_MIN_WAIT_HOURS", "1"))
        coffee_event_chance_denominator = int(
            os.getenv("COFFEE_EVENT_CHANCE_DENOMINATOR", "5")
        )
        if coffee_event_min_wait_hours <= 0 or coffee_event_chance_denominator <= 0:
            raise ValueError("Coffee event probability settings are invalid.")

        return cls(
            environment=environment,
            discord_token=token,
            database_path=database_path,
            postgres_database_url=os.getenv("POSTGRES_DATABASE_URL"),
            internal_api_token=os.getenv("INTERNAL_API_TOKEN", "miki-local-development-token"),
            command_prefix=os.getenv("COMMAND_PREFIX", "!"),
            weather_api_key=os.getenv("WEATHER_API_KEY"),
            giphy_api_key=os.getenv("GIPHY_API_KEY"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            social_link_base_xp=social_link_base_xp,
            social_link_reaction_xp=social_link_reaction_xp,
            coffee_event_min_minutes=coffee_event_min_minutes,
            coffee_event_max_minutes=coffee_event_max_minutes,
            coffee_event_duration_seconds=coffee_event_duration_seconds,
            coffee_event_min_wait_hours=coffee_event_min_wait_hours,
            coffee_event_chance_denominator=coffee_event_chance_denominator,
        )


settings = Settings.from_env()

# Backwards-compatible import for older modules and local scripts.
TOKEN = settings.discord_token
