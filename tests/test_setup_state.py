from database.connection import Database
from database.migrator import MigrationRunner
from repositories.setup_state_repository import SetupStateRepository
from setup.service import SetupStateService


async def test_setup_state_round_trip(tmp_path):
    database = Database(str(tmp_path / "miki.db"))
    await MigrationRunner(database).run()
    service = SetupStateService(SetupStateRepository(database))

    session = await service.load(123, "setup")
    session.set_value("step", "intro")
    await service.save(session)

    loaded = await service.load(123, "setup")

    assert loaded.get_value("step") == "intro"
