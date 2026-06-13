from __future__ import annotations

from pathlib import Path

from database.connection import Database
from database.schema import DEFAULT_PROFILE_FIELDS


class MigrationRunner:
    def __init__(self, database: Database, migrations_dir: Path | None = None):
        self.database = database
        self.migrations_dir = migrations_dir or Path(__file__).parent / "migrations" / "sqlite"

    async def run(self) -> None:
        async with self.database.connect() as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            for path in sorted(self.migrations_dir.glob("*.sql")):
                version = path.stem
                async with db.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = ?",
                    (version,),
                ) as cursor:
                    already_applied = await cursor.fetchone()

                if already_applied:
                    continue

                await db.executescript(path.read_text(encoding="utf-8"))
                await db.execute(
                    "INSERT INTO schema_migrations (version) VALUES (?)",
                    (version,),
                )

            await db.executemany(
                """
                INSERT INTO profile_fields (field_key, display_name, url_template)
                VALUES (?, ?, ?)
                ON CONFLICT(field_key) DO UPDATE SET
                    display_name = excluded.display_name,
                    url_template = excluded.url_template
                """,
                DEFAULT_PROFILE_FIELDS,
            )
            await db.commit()
