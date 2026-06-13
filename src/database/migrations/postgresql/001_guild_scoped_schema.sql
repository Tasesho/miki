CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS guild_members (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    username TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    xp INTEGER NOT NULL DEFAULT 0,
    nivel INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (guild_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_guild_members_leaderboard
    ON guild_members (guild_id, nivel DESC, xp DESC);

CREATE TABLE IF NOT EXISTS profile_fields (
    field_key TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    url_template TEXT,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS guild_profiles (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    field_key TEXT NOT NULL REFERENCES profile_fields(field_key),
    field_value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (guild_id, user_id, field_key),
    FOREIGN KEY (guild_id, user_id) REFERENCES guild_members(guild_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_guild_profiles_user
    ON guild_profiles (guild_id, user_id);

CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id BIGINT NOT NULL,
    setting_key TEXT NOT NULL,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (guild_id, setting_key)
);

CREATE TABLE IF NOT EXISTS guild_modules (
    guild_id BIGINT NOT NULL,
    module_key TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (guild_id, module_key)
);

CREATE TABLE IF NOT EXISTS guild_setup_state (
    guild_id BIGINT NOT NULL,
    flow_key TEXT NOT NULL,
    state_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (guild_id, flow_key)
);

CREATE TABLE IF NOT EXISTS guild_triggers (
    guild_id BIGINT NOT NULL,
    trigger_key TEXT NOT NULL,
    response TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (guild_id, trigger_key)
);

CREATE INDEX IF NOT EXISTS idx_guild_triggers_enabled
    ON guild_triggers (guild_id, enabled);

INSERT INTO profile_fields (field_key, display_name, url_template)
VALUES
    ('twitter', 'Twitter', 'https://twitter.com/{value}'),
    ('github', 'GitHub', 'https://github.com/{value}'),
    ('instagram', 'Instagram', 'https://instagram.com/{value}'),
    ('steam', 'Steam', 'https://steamcommunity.com/id/{value}'),
    ('website', 'Website', '{value}')
ON CONFLICT (field_key) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    url_template = EXCLUDED.url_template;
