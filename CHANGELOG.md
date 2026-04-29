# Changelog de BOT_MIKI

This document records all versions of **BOT_MIKI** and its changes.

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
