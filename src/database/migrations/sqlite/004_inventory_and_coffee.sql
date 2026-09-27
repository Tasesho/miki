CREATE TABLE IF NOT EXISTS inventories (
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    consumables INTEGER NOT NULL DEFAULT 0 CHECK (consumables >= 0),
    updated_at TEXT NOT NULL,
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS miki_affinity (
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    affinity_points INTEGER NOT NULL DEFAULT 0 CHECK (affinity_points >= 0),
    updated_at TEXT NOT NULL,
    PRIMARY KEY (guild_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_inventories_user
    ON inventories (guild_id, user_id);

CREATE INDEX IF NOT EXISTS idx_miki_affinity_user
    ON miki_affinity (guild_id, user_id);
