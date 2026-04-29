# (´・ω・`) Discord Bot Miki

![Version](https://img.shields.io/badge/version-1.5.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-purple)

**Miki** is a modern and scalable Discord bot designed to interact with users through commands, text triggers, and integration with external APIs. With modular architecture and Docker support, it's easy to maintain and deploy.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [Configuration](#configuration)
- [Commands](#commands)
- [Project Structure](#project-structure)
- [Changelog](#changelog)
- [License](#license)

## (´▽｀)ノ Features

- (๑•́ ω •̀๑) **Interactive Commands**: Multiple commands with `!` prefix
- (´・ω・`) **User Profiles & XP System**: Earn XP, level up, and showcase your Discord profile with social media links
- ✨ **Social Media Integration**: Link your Twitter, GitHub, Instagram, and website to your profile
- (´・ω・`) **Weather API Integration**: Check real-time weather with `!tiempo` or `!clima`
- (´▽｀) **Giphy API Integration**: Search and share GIFs
-  **Daily Leaderboard**: Automatic Top 10 ranking at midnight (12 AM) with user levels and XP in #general
- 🎯 **Fortune System**: Random wisdom quotes sent to #general every 6 hours
- 🧹 **Moderation Tools**: Admin commands for channel management (bulk delete messages)
- o(´▽｀)ノ **SQLite Database**: Persistent data storage with Docker volume support
- (´・_・`) **Docker Ready**: Easy deployment with Docker Compose
- (´▽｀) **Modular Architecture**: Organized and maintainable code
- (´・ω・`) **Word Statistics**: Message analysis in channels

## (´▽｀) Prerequisites

### Option 1: Local Installation
- **Python 3.11** or higher
- **pip** (Python package manager)
- **Virtual Environment** (recommended)

### Option 2: Docker Installation
- **Docker** 20.10 or higher
- **Docker Compose** 2.0 or higher

## (๑•́ ω •̀๑) Installation

### Local Installation

#### 1. Clone or download the project

```bash
cd /path/to/your/project
```

#### 2. Create and activate a Virtual Environment

**On Windows:**
```bash
python -m venv venv
call venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Discord token

Create a `.env` file in the project root:

```bash
DISCORD_TOKEN=your_token_here
```

(´；ω；`) **Important**: The token must have no spaces at the beginning or end.

#### 5. Run the bot

```bash
python src/bot.py
```

### Docker Installation

#### 1. Prerequisites

Make sure Docker and Docker Compose are installed:

```bash
docker --version
docker-compose --version
```

#### 2. Configure Discord token

Create a `.env` file in the project root:

```bash
DISCORD_TOKEN=your_token_here
```

#### 3. Run with Docker Compose

```bash
docker-compose up -d
```

#### 4. View logs

```bash
docker-compose logs -f miki-bot
```

#### 5. Stop the bot

```bash
docker-compose down
```

## (´・ω・`) Configuration

### Environment Variables

The `.env` file should contain:

```env
DISCORD_TOKEN=your_discord_token
```

**How to get your token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" and create a bot
4. Copy the token
5. Place it in the `.env` file

## ٩(◕‿◕。)۶ Commands

Miki responds to the following commands (prefix `!`):

| Command                       | Description                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------ |
| `!perfil [@usuario]`          | View your profile or another user's profile with XP, levels, and social media. |
| `!historial`                  | Shows the 10 most repeated words in the last 100 messages.                     |
| `!say <text>`                 | Repeats the message you send.                                                  |
| `!presentarse`                | The bot introduces itself.                                                     |
| `!talk`                       | The bot greets you with a random message.                                      |
| `!clima <city> [country]`     | Shows the current weather of a city (Weather API).                             |
| `!tiempo <city>`              | Alternative command for weather.                                               |
| `!gif <search>`               | Search and display a GIF (Giphy API).                                          |
| `!clear <numero>`             | **Admin only** - Deletes the last N messages (max: 100).                       |
| `!testdm`                     | Sends a test Direct Message to check if the bot can contact you.               |
| `!ayuda`                      | Shows available commands.                                                      |

## (´▽｀) Future Development: Slash Commands

To align with Discord's modern standards, there is a plan to migrate all prefix-based commands (`!`) to **Slash Commands**. This will provide a more integrated and user-friendly experience with autocompletion and clear command structures directly within the Discord interface.

## (´▽｀) Project Structure

```
miki/
├── src/
│   ├── bot.py              # Main bot file
│   ├── config.py           # Configuration
│   ├── database/
│   │   ├── __init__.py
│   │   └── manager.py      # Database manager
│   └── modules/
│       ├── __init__.py
│       ├── basic.py        # Basic commands
│       ├── commands.py     # Commands handler
│       ├── events.py       # Bot events
│       ├── services.py     # External services (Weather, Giphy)
│       └── weather.py      # Weather API integration
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (don't include in git)
├── CHANGELOG.md           # Changelog
└── README.md              # This file
```

## (´・ω・`) Changelog

For all versions, new features and bugfixes, see [CHANGELOG.md](CHANGELOG.md).

**Current Version**: 1.5.0

## (๑•́ ω •̀๑) Development

### Add a new command

1. Create or edit a module in `src/modules/`
2. Define your command using the `@bot.command()` decorator
3. Import the module in `src/bot.py`

### Add a new API

1. Create a new file in `src/modules/services.py` or a new module
2. Implement the integration
3. Use it in your commands

## (´▽｀) License

This project is open source and available under the MIT License.

---

**Developed by**: [Tasesho](https://github.com/Tasesho)  
**GitHub**: [Miki Project](https://github.com/Tasesho/miki)
