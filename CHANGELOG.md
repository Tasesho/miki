# Changelog de BOT_MIKI

This document records all versions of **BOT_MIKI** and its changes.

## [2.0.0] - 2026-05-31
- **Major Release**: Miki now treats each Discord server as its own little world (´▽`)ノ
- **Architecture**: Refactored the data model around `guild_id` so profiles, XP, levels, leaderboard, settings, and future social systems can live independently per server.
- **Database**: Added the new guild-scoped tables `users`, `guild_members`, `guild_profiles`, `profile_fields`, `guild_settings`, and `guild_triggers`.
- **Database**: Added composite keys for server-specific data, including `(guild_id, user_id)`, `(guild_id, user_id, field_key)`, and `(guild_id, setting_key)`.
- **Database**: Added indexes for leaderboard lookups, profile fields, and guild triggers so Miki does not trip over herself when the server grows (ง'̀-'́)ง
- **Migration Note**: This release is intended to start with a clean database in production. Old global profile/XP data is not automatically migrated because it did not have `guild_id`.
- **New Command**: `!profile` / `!perfil` now focuses on showing a user's profile inside the current server.
- **New Command**: `!profile edit` shows editable profile fields with friendly examples.
- **New Command**: `!profile set <field> <value>` lets users update one profile field at a time, such as GitHub, Steam, Instagram, Twitter, or Website.
- **Profile System**: Social links are no longer hardcoded as fixed user columns. They now use extensible profile fields, making future networks easier to add.
- **XP System**: XP cooldown and XP per message are now read per server instead of being hardcoded globally.
- **Leaderboard**: `!leaderboard` / `!top` now ranks users only inside the current server.
- **Configuration**: Added `!config` and `!config set <key> <value>` for server admins with `Manage Guild` permission.
- **Configuration**: Added server settings for leaderboard channel, logs channel, welcome channel, XP per message, and XP cooldown.
- **Permissions**: Admin configuration now depends on Discord permissions, not role names. Much cleaner, much less cursed (´・ω・`)
- **UX**: Improved feedback messages for profile and configuration commands so users get examples instead of cryptic technical hints.
- **Fix**: `weather.py` now has a valid extension `setup()` function so the automatic module loader does not complain during startup.
- **Docs**: Updated `!ayuda` to explain the new profile, XP, and configuration behavior.

## [1.6.0] - 2026-04-29
- **Refactor**: `fortune_loop` now uses a synonym list (`general`, `chat`, `lobby`) for smarter channel detection.
- **Fix**: The bot no longer sends fortune messages to incorrect channels if a "general" channel is not found.
- **Fix**: Corrected silent syntax errors in the `events.py` module that could prevent loops from running.
- **Docs**: Updated `README.md` and `!ayuda` command to reflect all current features and commands.
- **Docs**: Added a note in `README.md` about the future migration to Slash Commands.

## [1.5.0] - 2026-04-28
- **New Command**: `!tiempo <city>` - Alternative weather command for better accessibility
- **New Command**: `!clear <numero>` - Admin-only moderation tool to bulk delete messages (max: 100)
- **New Feature**: `fortune_loop` - Random wisdom/fortunes sent to #general every 6 hours
- **Enhancement**: Fixed bot self-response issues - now correctly ignores its own messages
- **Enhancement**: Daily leaderboard now sends only to #general channel at 12 AM
- **Enhancement**: Improved message tracking and user activity detection
- **Moderation**: Added proper permission checks for admin commands
- **Documentation**: Updated README and help command with new features

## [1.4.0] - 2026-04-26
- **New Feature**: Periodic activity triggers - Bot sends engagement alerts every 30 minutes of channel inactivity
- **New Feature**: Daily leaderboard - Automatic Top 10 ranking display at midnight (12 AM) with user levels and XP
- **Enhancement**: Activity tracking system to monitor last message in each channel
- **Enhancement**: Smart trigger logic - Bot won't send alerts if it was the last one to message
- **Enhancement**: Customizable alert messages with bot personality emojis
- **Database**: New method `get_leaderboard()` to fetch ranked user data efficiently

## [1.3.0] - 2026-04-25
- **New Feature**: User profile system with XP levels and rank progression
- **New Command**: `!perfil` - View and configure user profiles with social media links
- **Database**: Fixed database persistence issue - SQLite database now correctly stored in Docker volume
- **Enhancement**: User data now persists across bot restarts
- **Social Links**: Added support for Twitter, GitHub, Instagram, and personal websites in user profiles
- **XP System**: Automatic XP accumulation with level progression (100 XP per level)

## [1.2.0] - 2026-04-22
- Deep update of documentation with detailed Docker installation.
- Improvement in README structure with navigable table of contents.
- Refactoring of development and configuration documentation.

## [1.1.1] - 2025-02-28
- Bugfix: now !gif command works as intended
## [1.1.0] - 2025-02-28
- Added `!clima` command to display current weather of a city using WeatherAPI.
- Added `!gif` command to search and display GIFs using Giphy API, with attractive **embed** results.
## [1.0.0] - 2025-02-28
- First stable version of **BOT_MIKI**.

---

## 📌 GitHub
You can find the code at:
[My GitHub](https://github.com/Tasesho)  
