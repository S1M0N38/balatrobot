# Lua API Reference

Complete reference for the Lua components of Balatrobot.

## Overview

The Lua API provides the game-side components that interface directly with Balatro. These modules handle:

- Game state extraction
- Command processing
- UDP communication
- Action execution
- Logging and debugging

## Core Modules

### main.lua
Entry point for the mod that initializes all components.

### config.lua
Configuration file for mod settings. See the actual `config.lua` file for available options.

## Bot Module

Located in `src/bot.lua` - Defines actions and validation logic.

### Key Components

- Action definitions with validation rules
- Bot settings configuration
- Default bot behavior functions

## API Module

Located in `src/api.lua` - Core UDP communication and game hooks.

### Key Functions

- `BalatrobotAPI.init()` - Initialize the API system
- `BalatrobotAPI.update()` - Handle incoming UDP messages
- `BalatrobotAPI.queueaction()` - Queue bot actions for execution

## Utils Module

Located in `src/utils.lua` - Game state extraction and utility functions.

### Game State Functions

#### `Utils.getGamestate()`
Extract complete game state for bot processing.

```lua
local game_state = Utils.getGamestate()
-- Returns complete game state table
```

#### `Utils.getHandData()`
Get current hand cards.

```lua
local hand = Utils.getHandData()
```

#### `Utils.getJokersData()`
Get active jokers.

```lua
local jokers = Utils.getJokersData()
```

#### `Utils.getShopData()`
Get shop contents (when in shop).

```lua
local shop = Utils.getShopData()
```

#### `Utils.parseaction(data)`
Parse action string from bot commands.

```lua
local action = Utils.parseaction("PLAY_HAND|1,2,3")
```

## Middleware Module

Located in `src/middleware.lua` - Handles game event hooks and action execution.

## Logger Module

Located in `src/botlogger.lua` - Manages action logging and replay functionality.

## Configuration

Configuration options are defined in `config.lua`. See the actual file for current available settings.

## Implementation Notes

The Lua API uses the Hook library to intercept game events and the middleware system to execute bot actions. Game state is extracted through the Utils module functions.

---

*For integration with Python components, see [Python API](python-api.md) and [Architecture](architecture.md).* 