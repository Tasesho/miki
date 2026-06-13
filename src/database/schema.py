from __future__ import annotations


DEFAULT_PROFILE_FIELDS = (
    ("twitter", "Twitter", "https://twitter.com/{value}"),
    ("github", "GitHub", "https://github.com/{value}"),
    ("instagram", "Instagram", "https://instagram.com/{value}"),
    ("steam", "Steam", "https://steamcommunity.com/id/{value}"),
    ("website", "Website", "{value}"),
)


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version TEXT PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS guild_members (
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        registered_at TEXT NOT NULL,
        xp INTEGER NOT NULL DEFAULT 0,
        nivel INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY (guild_id, user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS profile_fields (
        field_key TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        url_template TEXT,
        enabled INTEGER NOT NULL DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS guild_profiles (
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        field_key TEXT NOT NULL,
        field_value TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (guild_id, user_id, field_key),
        FOREIGN KEY (field_key) REFERENCES profile_fields(field_key)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS guild_settings (
        guild_id INTEGER NOT NULL,
        setting_key TEXT NOT NULL,
        setting_value TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (guild_id, setting_key)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS guild_modules (
        guild_id INTEGER NOT NULL,
        module_key TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 1,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (guild_id, module_key)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS guild_setup_state (
        guild_id INTEGER NOT NULL,
        flow_key TEXT NOT NULL,
        state_json TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (guild_id, flow_key)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS guild_triggers (
        guild_id INTEGER NOT NULL,
        trigger_key TEXT NOT NULL,
        response TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 1,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (guild_id, trigger_key)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_guild_members_leaderboard
    ON guild_members (guild_id, nivel DESC, xp DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_guild_profiles_user
    ON guild_profiles (guild_id, user_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_guild_triggers_enabled
    ON guild_triggers (guild_id, enabled)
    """,
)
