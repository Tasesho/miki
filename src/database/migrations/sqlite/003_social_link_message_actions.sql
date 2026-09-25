DROP INDEX IF EXISTS idx_social_link_interactions_daily;

ALTER TABLE social_link_interactions RENAME TO social_link_interactions_legacy;

CREATE TABLE social_link_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('gift', 'reaction', 'reply', 'mention')),
    affinity_xp INTEGER NOT NULL CHECK (affinity_xp > 0),
    source_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (guild_id, user_id, target_user_id, action, source_id)
);

INSERT INTO social_link_interactions
    (id, guild_id, user_id, target_user_id, action, affinity_xp, source_id, created_at)
SELECT id, guild_id, user_id, target_user_id, action, affinity_xp, source_id, created_at
FROM social_link_interactions_legacy;

DROP TABLE social_link_interactions_legacy;

CREATE INDEX idx_social_link_interactions_daily
    ON social_link_interactions (guild_id, user_id, action, created_at);
