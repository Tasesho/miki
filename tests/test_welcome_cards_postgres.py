import os

import pytest

from dashboard.repository import PostgresWelcomeCardRepository
from dashboard.welcome_cards import WelcomeCardSettings

DATABASE_URL = os.getenv("TEST_POSTGRES_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL, reason="Set TEST_POSTGRES_DATABASE_URL to run PostgreSQL integration tests."
)


async def test_postgres_welcome_card_round_trip():
    repository = PostgresWelcomeCardRepository(DATABASE_URL)
    await repository.connect()
    try:
        await repository.migrate()
        saved = await repository.save(
            912345678,
            WelcomeCardSettings(
                enabled=True,
                channel_id=345,
                title="Welcome {user}",
                message="Hi!",
                extra_message="Visit {channel:rules}, {user}!",
            ),
        )
        loaded = await repository.get(912345678)
    finally:
        await repository.close()

    assert saved == loaded
    assert loaded.enabled is True
    assert loaded.channel_id == 345
    assert loaded.extra_message == "Visit {channel:rules}, {user}!"
