# Spark Utility Discord Bot

## Overview

Spark Utility is a comprehensive Discord bot built in Python using discord.py. It provides a wide range of utility commands, moderation tools, and an advanced ticket system. The bot is designed with a modular architecture using cogs for better organization and maintainability.

## System Architecture

### Backend Architecture
- **Framework**: discord.py with async/await pattern
- **Language**: Python 3.x
- **Database**: SQLite with aiosqlite for async operations
- **Architecture Pattern**: Command-based bot with cog system for modularity

### Key Design Decisions
- **Cog-based organization**: Each major feature set is organized into separate cogs (logging, utility, tickets, moderation, help) for better maintainability
- **Environment-based configuration**: All sensitive data and settings are managed through environment variables
- **Comprehensive logging**: Every command execution is logged with detailed information sent to the bot owner's DMs
- **Interactive UI**: Uses discord.ui for modern button and select menu interactions

## Key Components

### 1. Configuration Management (`config.py`)
- Centralized configuration handling with environment variable support
- Validates required settings (bot token, owner ID)
- Manages API keys for external services (TinyURL, Reddit, Translation)
- Configurable bot settings (max tickets, auto-archive hours, etc.)

### 2. Database Layer (`database.py`)
- SQLite database with async support via aiosqlite
- Schema includes:
  - Guild settings (log channels, ticket categories, staff roles)
  - Ticket management (status, assignments, timestamps)
  - AFK users tracking
  - Reminders system
  - User warnings and moderation logs

### 3. Core Bot (`main.py`)
- Main bot class extending commands.Bot
- Handles bot initialization and cog loading
- Manages intents and permissions
- Sets up database connections

### 4. Logging System (`cogs/logging_system.py`)
- Comprehensive command logging to owner DMs
- Error tracking with stack traces
- Guild-specific log channel support
- Command execution monitoring

### 5. Ticket System (`cogs/tickets.py`)
- Interactive ticket creation with category selection
- Private channel creation with proper permissions
- Ticket claiming and assignment system
- Transcript generation on ticket closure
- Auto-archiving for inactive tickets

### 6. Utility Commands (`cogs/utility.py`)
- Server information commands (serverinfo, userinfo, etc.)
- Fun commands (calculator, polls, quotes)
- API integrations (URL shortening, translation)
- Reminder and timer systems
- AFK status management

### 7. Moderation Tools (`cogs/moderation.py`)
- Message bulk deletion
- User management (ban, kick, timeout)
- Permission checking and validation
- Action logging and audit trails

### 8. Help System (`cogs/help.py`)
- Interactive help with category selection
- Detailed command documentation
- Usage examples and permission requirements

### 9. Utilities (`utils/`)
- **embeds.py**: Standardized embed creation with builder pattern
- **helpers.py**: Common utility functions (time parsing, safe messaging)

## Data Flow

1. **Command Execution**:
   - User triggers command → Bot processes → Cog handles logic → Database interaction (if needed) → Response sent → Action logged

2. **Ticket Creation**:
   - User selects category → Bot creates private channel → Permissions set → Database record created → Staff notified

3. **Logging Flow**:
   - Command executed → Logging system captures details → Embed created → Sent to owner DMs → Optionally logged to guild channel

## External Dependencies

### Required Environment Variables
- `BOT_TOKEN`: Discord bot token
- `OWNER_ID`: Bot owner's Discord user ID
- `PREFIX`: Command prefix (default: '!')

### Optional API Keys
- `TINYURL_API_KEY`: For URL shortening service
- `REDDIT_CLIENT_ID` & `REDDIT_CLIENT_SECRET`: For Reddit integration
- `TRANSLATE_API_KEY`: For translation services

### Python Dependencies
- `discord.py`: Main Discord library
- `aiosqlite`: Async SQLite database operations
- `aiohttp`: HTTP requests for API integrations

## Deployment Strategy

### Environment Setup
- Configure environment variables for bot token and API keys
- Initialize SQLite database on first run
- Set up proper file permissions for database

### Bot Permissions
- Message content intent for command processing
- Member intent for user information commands
- Guild intent for server management
- Manage channels permission for ticket system
- Manage messages for moderation commands

### Scaling Considerations
- SQLite suitable for single-instance deployment
- Database schema designed for guild-specific settings
- Logging system handles high-volume command execution

## Changelog
- July 06, 2025: Complete Discord bot implementation with all requested features
- Added comprehensive utility commands (ping, serverinfo, userinfo, avatar, etc.)
- Implemented advanced ticket system with interactive panels and staff management
- Added moderation commands (ban, kick, clear, timeout, slowmode)
- Included fun commands (poll, calculator, quotes, urban dictionary, meme)
- Built comprehensive logging system sending all actions to owner DMs
- Added logs set command to configure server log channels
- Implemented custom help system with categorized embeds
- Created modular cog-based architecture for maintainability
- All commands include proper error handling and permission checks

## User Preferences

Preferred communication style: Simple, everyday language.