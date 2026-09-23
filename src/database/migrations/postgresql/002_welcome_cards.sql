CREATE TABLE IF NOT EXISTS guild_welcome_cards (
    guild_id BIGINT PRIMARY KEY,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    channel_id BIGINT,
    title TEXT NOT NULL DEFAULT 'Welcome, {user}!',
    message TEXT NOT NULL DEFAULT 'We are happy to have you here.',
    background_url TEXT,
    accent_color VARCHAR(7) NOT NULL DEFAULT '#8B5CF6',
    text_color VARCHAR(7) NOT NULL DEFAULT '#FFFFFF',
    show_avatar BOOLEAN NOT NULL DEFAULT TRUE,
    show_member_count BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT guild_welcome_cards_channel_id_positive CHECK (channel_id IS NULL OR channel_id > 0),
    CONSTRAINT guild_welcome_cards_title_length CHECK (char_length(title) BETWEEN 1 AND 200),
    CONSTRAINT guild_welcome_cards_message_length CHECK (char_length(message) BETWEEN 1 AND 200),
    CONSTRAINT guild_welcome_cards_accent_color CHECK (accent_color ~ '^#[0-9A-Fa-f]{6}$'),
    CONSTRAINT guild_welcome_cards_text_color CHECK (text_color ~ '^#[0-9A-Fa-f]{6}$')
);
