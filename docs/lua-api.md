# Lua API Reference

Complete reference for the Lua components of Balatrobot.

## 📋 Table of Contents

- [Overview](#overview)
- [Core Modules](#core-modules)
- [Bot Module](#bot-module)
- [API Module](#api-module)
- [Utils Module](#utils-module)
- [Middleware Module](#middleware-module)
- [Logger Module](#logger-module)
- [Configuration](#configuration)
- [Hooks](#hooks)

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
Configuration file for bot settings.

```lua
-- Example configuration
return {
    bot_port = 12346,
    game_port = 12345,
    bot_host = "127.0.0.1",
    game_host = "127.0.0.1",
    debug = true,
    log_actions = true,
    speed_factor = 10
}
```

## Bot Module

Located in `src/bot.lua` - Main bot logic and game integration.

### Key Functions

#### `extract_game_state()`
Extracts current game state into a structured format.

```lua
local game_state = extract_game_state()
-- Returns table with hand, jokers, shop, etc.
```

#### `process_bot_command(cmd)`
Processes commands received from the Python bot.

```lua
process_bot_command("play_hand:1,2,3")
```

#### `execute_action(action_type, params)`
Executes game actions based on bot decisions.

```lua
execute_action("play_hand", {1, 2, 3})
execute_action("buy_card", {1})
execute_action("end_shop", {})
```

## API Module

Located in `src/api.lua` - Core game state and action APIs.

### Game State Functions

#### `get_hand_info()`
Returns information about cards in hand.

```lua
local hand = get_hand_info()
-- hand = {
--     {rank = "Ace", suit = "Spades", value = 11},
--     {rank = "King", suit = "Hearts", value = 10},
--     ...
-- }
```

#### `get_joker_info()`
Returns information about active jokers.

```lua
local jokers = get_joker_info()
-- jokers = {
--     {name = "Joker", effect = "+4 Mult", rarity = "Common"},
--     ...
-- }
```

#### `get_shop_info()`
Returns current shop contents and prices.

```lua
local shop = get_shop_info()
-- shop = {
--     cards = {...},
--     vouchers = {...},
--     boosters = {...},
--     reroll_cost = 5
-- }
```

#### `get_blind_info()`
Returns information about current and upcoming blinds.

```lua
local blinds = get_blind_info()
-- blinds = {
--     current = "Small Blind",
--     ondeck = "Big Blind",
--     requirement = 300
-- }
```

### Action Functions

#### `play_selected_cards(indices)`
Play cards at specified positions.

```lua
play_selected_cards({1, 3, 5})
```

#### `discard_selected_cards(indices)`
Discard cards at specified positions.

```lua
discard_selected_cards({2, 4})
```

#### `buy_shop_item(type, index)`
Purchase item from shop.

```lua
buy_shop_item("card", 1)
buy_shop_item("voucher", 1)
buy_shop_item("booster", 2)
```

#### `sell_joker(index)`
Sell joker at specified position.

```lua
sell_joker(2)
```

## Utils Module

Located in `src/utils.lua` - Utility functions and helpers.

### Helper Functions

#### `table_to_string(tbl)`
Convert table to string representation.

```lua
local str = table_to_string({a = 1, b = 2})
-- Returns "a:1,b:2"
```

#### `split_string(str, delimiter)`
Split string by delimiter.

```lua
local parts = split_string("1,2,3", ",")
-- Returns {"1", "2", "3"}
```

#### `deep_copy(tbl)`
Create deep copy of table.

```lua
local copy = deep_copy(original_table)
```

#### `find_card_by_rank(hand, rank)`
Find cards in hand by rank.

```lua
local aces = find_card_by_rank(hand, "Ace")
```

## Middleware Module

Located in `src/middleware.lua` - Request/response processing.

### Functions

#### `process_incoming_data(data)`
Process data received from Python bot.

```lua
local result = process_incoming_data(json_data)
```

#### `format_outgoing_data(game_state)`
Format game state for sending to bot.

```lua
local formatted = format_outgoing_data(G)
```

## Logger Module

Located in `src/botlogger.lua` - Logging and debugging.

### Functions

#### `log_action(action, params)`
Log bot actions for replay.

```lua
log_action("play_hand", {1, 2, 3})
```

#### `log_game_state(state)`
Log current game state.

```lua
log_game_state(G)
```

#### `write_log_file()`
Write accumulated logs to file.

```lua
write_log_file()
```

## Configuration

### Config Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bot_port` | number | 12346 | UDP port for bot communication |
| `game_port` | number | 12345 | UDP port for game communication |
| `bot_host` | string | "127.0.0.1" | Bot host address |
| `game_host` | string | "127.0.0.1" | Game host address |
| `debug` | boolean | false | Enable debug logging |
| `log_actions` | boolean | true | Log all actions |
| `speed_factor` | number | 1 | Game speed multiplier |

## Hooks

### Game Event Hooks

The Lua API uses hooks to intercept game events:

#### `INIT`
Called when game initializes.

```lua
-- Hook into game initialization
hook_init = function()
    initialize_bot_communication()
end
```

#### `UPDATE`
Called every game frame.

```lua
-- Hook into game updates
hook_update = function()
    check_bot_messages()
end
```

#### `CARD_PLAY`
Called when cards are played.

```lua
-- Hook into card play events
hook_card_play = function(cards)
    log_action("card_play", cards)
end
```

### Custom Hooks

You can create custom hooks for specific events:

```lua
-- Custom hook for shop interactions
hook_shop_action = function(action, item)
    log_action("shop_" .. action, item)
    send_to_bot("shop_update", get_shop_info())
end
```

---

*For integration with Python components, see [Python API](python-api.md) and [Architecture](architecture.md).* 