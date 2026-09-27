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


async def test_social_link_rank_is_derived_from_current_xp(tmp_path):
    database = Database(str(tmp_path / "miki.db"))
    await MigrationRunner(database).run()
    repository = SocialLinkRepository(database, base_level_xp=1, reaction_xp=1)

    await repository.add_affinity(1, 10, 20, 3, "gift", "gift:1")
    assert (await repository.get_link(1, 10, 20))["affinity_rank"] == 3

    repository.base_level_xp = 100
    link = await repository.get_link(1, 10, 20)
    assert link["affinity_xp"] == 3
    assert link["affinity_rank"] == 1
