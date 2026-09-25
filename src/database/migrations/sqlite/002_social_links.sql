CREATE TABLE IF NOT EXISTS social_links (
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    affinity_xp INTEGER NOT NULL DEFAULT 0 CHECK (affinity_xp >= 0),
    affinity_rank INTEGER NOT NULL DEFAULT 1 CHECK (affinity_rank BETWEEN 1 AND 10),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (guild_id, user_id, target_user_id),
    CHECK (user_id != target_user_id)
);

CREATE TABLE IF NOT EXISTS social_link_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('gift', 'reaction')),
    affinity_xp INTEGER NOT NULL CHECK (affinity_xp > 0),
    source_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (guild_id, user_id, target_user_id, action, source_id)
);

CREATE INDEX IF NOT EXISTS idx_social_links_user
    ON social_links (guild_id, user_id, affinity_rank DESC, affinity_xp DESC);

CREATE INDEX IF NOT EXISTS idx_social_links_target
    ON social_links (guild_id, target_user_id);

CREATE INDEX IF NOT EXISTS idx_social_link_interactions_daily
    ON social_link_interactions (guild_id, user_id, action, created_at);
