from database.connection import Database
from database.migrator import MigrationRunner
from repositories.inventory_repository import InventoryRepository


async def test_inventory_and_miki_affinity_are_guild_scoped(tmp_path):
    database = Database(str(tmp_path / "miki.db"))
    await MigrationRunner(database).run()
    repository = InventoryRepository(database)

    assert await repository.add_consumable(1, 10) == 1
    assert await repository.add_consumable(1, 10, 2) == 3
    assert await repository.get_inventory(2, 10) == 0
    assert await repository.remove_consumable(1, 10)
    assert await repository.get_inventory(1, 10) == 2
    assert not await repository.remove_consumable(2, 10)

    assert await repository.add_miki_affinity(1, 10) == 1
    assert await repository.get_miki_affinity(2, 10) == 0
