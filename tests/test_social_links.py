from database.connection import Database
from database.migrator import MigrationRunner
from repositories.social_link_repository import SocialLinkRepository


async def test_social_links_are_directed_and_guild_scoped(tmp_path):
    database = Database(str(tmp_path / "miki.db"))
    await MigrationRunner(database).run()
    repository = SocialLinkRepository(database, base_level_xp=1, reaction_xp=1)

    first = await repository.add_reaction_affinity(1, 10, 20, 100)
    second = await repository.add_reaction_affinity(1, 10, 20, 101)
    reverse = await repository.add_reaction_affinity(1, 20, 10, 102)
    other_guild = await repository.add_reaction_affinity(2, 10, 20, 100)

    assert first["affinity_xp"] == 1
    assert second["affinity_xp"] == 2
    assert second["affinity_rank"] == 2
    assert reverse["affinity_xp"] == 1
    assert other_guild["affinity_xp"] == 1


async def test_social_link_reaction_limits_and_duplicates(tmp_path):
    database = Database(str(tmp_path / "miki.db"))
    await MigrationRunner(database).run()
    repository = SocialLinkRepository(database, base_level_xp=100, reaction_xp=1)

    assert await repository.add_reaction_affinity(1, 10, 20, 100)
    assert await repository.add_reaction_affinity(1, 10, 20, 100) is None
    assert await repository.add_reaction_affinity(1, 10, 20, 101)
    assert await repository.add_reaction_affinity(1, 10, 20, 102)
    assert await repository.add_reaction_affinity(1, 10, 20, 103) is None
    assert await repository.add_reaction_affinity(1, 10, 10, 104) is None
