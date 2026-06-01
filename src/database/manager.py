import aiosqlite
from datetime import datetime
from pathlib import Path


DEFAULT_PROFILE_FIELDS = (
    ("twitter", "Twitter", "https://twitter.com/{value}"),
    ("github", "GitHub", "https://github.com/{value}"),
    ("instagram", "Instagram", "https://instagram.com/{value}"),
    ("steam", "Steam", "https://steamcommunity.com/id/{value}"),
    ("website", "Website", "{value}"),
)


class DBManager:
    def __init__(self, db_path="src/database/miki.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init_db(self):
        """Inicializa tablas separadas por dominio y preparadas para guild_id."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")

            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_members (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    registered_at TEXT NOT NULL,
                    xp INTEGER NOT NULL DEFAULT 0,
                    nivel INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS profile_fields (
                    field_key TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    url_template TEXT,
                    enabled INTEGER NOT NULL DEFAULT 1
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_profiles (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    field_key TEXT NOT NULL,
                    field_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (guild_id, user_id, field_key),
                    FOREIGN KEY (field_key) REFERENCES profile_fields(field_key)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER NOT NULL,
                    setting_key TEXT NOT NULL,
                    setting_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (guild_id, setting_key)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_triggers (
                    guild_id INTEGER NOT NULL,
                    trigger_key TEXT NOT NULL,
                    response TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (guild_id, trigger_key)
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_guild_members_leaderboard
                ON guild_members (guild_id, nivel DESC, xp DESC)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_guild_profiles_user
                ON guild_profiles (guild_id, user_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_guild_triggers_enabled
                ON guild_triggers (guild_id, enabled)
            """)

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

    async def ensure_user(self, user_id, username):
        now = self._now()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, username, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    updated_at = excluded.updated_at
                """,
                (user_id, username, now, now),
            )
            await db.commit()

    async def ensure_guild_member(self, guild_id, user_id, username):
        now = self._now()
        await self.ensure_user(user_id, username)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO guild_members (guild_id, user_id, username, registered_at, xp, nivel)
                VALUES (?, ?, ?, ?, 0, 1)
                ON CONFLICT(guild_id, user_id) DO UPDATE SET
                    username = excluded.username
                """,
                (guild_id, user_id, username, now),
            )
            await db.commit()

    async def get_usuario(self, guild_id, user_id):
        """Obtiene el perfil de progreso y redes de un usuario dentro de un servidor."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT guild_id, user_id, username, registered_at, xp, nivel
                FROM guild_members
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None

            profile_fields = await self.get_profile_values(guild_id, user_id)
            return {
                "guild_id": row[0],
                "discord_id": row[1],
                "username": row[2],
                "fecha_registro": row[3],
                "xp": row[4],
                "nivel": row[5],
                "profile_fields": profile_fields,
                "twitter": profile_fields.get("twitter"),
                "github": profile_fields.get("github"),
                "instagram": profile_fields.get("instagram"),
                "website": profile_fields.get("website"),
            }

    async def registrar_usuario(self, guild_id, user_id, username):
        """Compatibilidad con el nombre antiguo, ahora scoped por guild."""
        await self.ensure_guild_member(guild_id, user_id, username)

    async def actualizar_xp(self, guild_id, user_id, username, xp_ganado):
        """Actualiza XP de un miembro dentro de un servidor."""
        await self.ensure_guild_member(guild_id, user_id, username)
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT xp, nivel
                FROM guild_members
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None

            xp_actual, nivel_actual = row
            nuevo_xp = xp_actual + xp_ganado
            xp_requerido = nivel_actual * 100
            nuevo_nivel = nivel_actual

            while nuevo_xp >= xp_requerido:
                nuevo_xp -= xp_requerido
                nuevo_nivel += 1
                xp_requerido = nuevo_nivel * 100

            await db.execute(
                """
                UPDATE guild_members
                SET xp = ?, nivel = ?, username = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (nuevo_xp, nuevo_nivel, username, guild_id, user_id),
            )
            await db.commit()

            return {
                "xp_actual": nuevo_xp,
                "nivel_actual": nuevo_nivel,
                "subio_nivel": nuevo_nivel > nivel_actual,
                "nivel_anterior": nivel_actual,
            }

    async def actualizar_redes(self, guild_id, user_id, **fields):
        """Actualiza campos de perfil de forma extensible."""
        for field_key, value in fields.items():
            if value is not None:
                await self.set_profile_value(guild_id, user_id, field_key, value)

    async def get_profile_fields(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT field_key, display_name, url_template
                FROM profile_fields
                WHERE enabled = 1
                ORDER BY display_name
                """
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {"key": row[0], "display_name": row[1], "url_template": row[2]}
                    for row in rows
                ]

    async def get_profile_field(self, field_key):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT field_key, display_name, url_template
                FROM profile_fields
                WHERE field_key = ? AND enabled = 1
                """,
                (field_key,),
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                return {"key": row[0], "display_name": row[1], "url_template": row[2]}

    async def get_profile_values(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT field_key, field_value
                FROM guild_profiles
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ) as cursor:
                rows = await cursor.fetchall()
                return {row[0]: row[1] for row in rows}

    async def set_profile_value(self, guild_id, user_id, field_key, field_value):
        field = await self.get_profile_field(field_key)
        if field is None:
            return False

        now = self._now()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO guild_profiles (guild_id, user_id, field_key, field_value, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(guild_id, user_id, field_key) DO UPDATE SET
                    field_value = excluded.field_value,
                    updated_at = excluded.updated_at
                """,
                (guild_id, user_id, field_key, field_value, now),
            )
            await db.commit()
            return True

    async def get_leaderboard(self, guild_id, limit=10):
        """Obtiene el leaderboard de un servidor."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT user_id, username, nivel, xp
                FROM guild_members
                WHERE guild_id = ?
                ORDER BY nivel DESC, xp DESC
                LIMIT ?
                """,
                (guild_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "discord_id": row[0],
                        "username": row[1],
                        "nivel": row[2],
                        "xp": row[3],
                    }
                    for row in rows
                ]

    async def get_setting(self, guild_id, setting_key):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT setting_value
                FROM guild_settings
                WHERE guild_id = ? AND setting_key = ?
                """,
                (guild_id, setting_key),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def set_setting(self, guild_id, setting_key, setting_value):
        now = self._now()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO guild_settings (guild_id, setting_key, setting_value, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id, setting_key) DO UPDATE SET
                    setting_value = excluded.setting_value,
                    updated_at = excluded.updated_at
                """,
                (guild_id, setting_key, str(setting_value), now),
            )
            await db.commit()

    async def get_guild_triggers(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT trigger_key, response
                FROM guild_triggers
                WHERE guild_id = ? AND enabled = 1
                """,
                (guild_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return {row[0]: row[1] for row in rows}

    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
