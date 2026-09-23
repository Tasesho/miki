ALTER TABLE guild_welcome_cards
ADD COLUMN IF NOT EXISTS extra_message TEXT NOT NULL DEFAULT '';
