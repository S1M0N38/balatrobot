# Python API Reference

Complete reference for the Python components of Balatrobot.

## 📋 Table of Contents

- [Bot Class](#bot-class)
- [Actions Enum](#actions-enum)
- [State Enum](#state-enum)
- [Helper Functions](#helper-functions)
- [Game State Module](#game-state-module)

## Bot Class

The base `Bot` class provides the foundation for all bot implementations.

### Constructor

```python
Bot(deck: str, stake: int = 1, seed: str = None, challenge: str = None, bot_port: int = 12346)
```

**Parameters:**
- `deck` (str): Name of the deck to use (e.g., "Red Deck", "Plasma Deck")
- `stake` (int, optional): Difficulty stake level (1-8). Default: 1
- `seed` (str, optional): Game seed for reproducible runs. Default: None (random)
- `challenge` (str, optional): Challenge run identifier. Default: None
- `bot_port` (int, optional): UDP port for communication. Default: 12346

**Example:**
```python
bot = Bot(deck="Blue Deck", stake=3, seed="ABC123", bot_port=12347)
```

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `G` | dict | Current game state received from Lua mod |
| `deck` | str | Selected deck name |
| `stake` | int | Difficulty stake level |
| `seed` | str | Game seed (generated if not provided) |
| `challenge` | str | Challenge identifier |
| `bot_port` | int | UDP communication port |
| `addr` | tuple | Socket address (localhost, port) |
| `running` | bool | Bot execution state |
| `sock` | socket | UDP socket for communication |
| `state` | dict | Persistent bot state dictionary |

### Required Methods

These methods must be implemented by all bot subclasses:

#### skip_or_select_blind(self, G: dict) -> list

Decide whether to skip or play the current blind.

**Parameters:**
- `G` (dict): Complete game state

**Returns:**
- `list`: Action in format `[Actions.SELECT_BLIND]` or `[Actions.SKIP_BLIND]`

**Example:**
```python
def skip_or_select_blind(self, G):
    blind_name = G["ante"]["blinds"]["ondeck"]
    if blind_name in ["Small", "Big"]:
        return [Actions.SKIP_BLIND]
    return [Actions.SELECT_BLIND]
```

#### select_cards_from_hand(self, G: dict) -> list

Choose cards to play or discard from hand.

**Parameters:**
- `G` (dict): Complete game state

**Returns:**
- `list`: Action in format `[Actions.PLAY_HAND, [indices]]` or `[Actions.DISCARD_HAND, [indices]]`

**Example:**
```python
def select_cards_from_hand(self, G):
    # Play first two cards
    return [Actions.PLAY_HAND, [1, 2]]
```

#### select_shop_action(self, G: dict) -> list

Make decisions in the shop phase.

**Parameters:**
- `G` (dict): Complete game state including shop information

**Returns:**
- `list`: Shop action (buy, reroll, or end shop)

**Valid Returns:**
- `[Actions.BUY_CARD, [index]]`
- `[Actions.BUY_VOUCHER, [index]]`
- `[Actions.BUY_BOOSTER, [index]]`
- `[Actions.REROLL_SHOP]`
- `[Actions.END_SHOP]`

#### select_booster_action(self, G: dict) -> list

Handle booster pack selections.

**Parameters:**
- `G` (dict): Game state with booster pack information

**Returns:**
- `list`: Booster action

**Valid Returns:**
- `[Actions.SELECT_BOOSTER_CARD, [card_index], [target_indices]]`
- `[Actions.SKIP_BOOSTER_PACK]`

#### sell_jokers(self, G: dict) -> list

Decide which jokers to sell for money.

**Parameters:**
- `G` (dict): Game state with joker information

**Returns:**
- `list`: Sell action in format `[Actions.SELL_JOKER, [indices]]` or `[Actions.SELL_JOKER, []]`

#### rearrange_jokers(self, G: dict) -> list

Reorder jokers for optimal positioning.

**Parameters:**
- `G` (dict): Game state

**Returns:**
- `list`: Usually `[Actions.REARRANGE_JOKERS, []]`

#### use_or_sell_consumables(self, G: dict) -> list

Decide whether to use or sell consumable cards (tarot, planet, spectral).

**Parameters:**
- `G` (dict): Game state with consumable information

**Returns:**
- `list`: Use or sell action

**Valid Returns:**
- `[Actions.USE_CONSUMABLE, [index], [target_indices]]`
- `[Actions.SELL_CONSUMABLE, [index]]`
- `[Actions.USE_CONSUMABLE, []]` (do nothing)

#### rearrange_consumables(self, G: dict) -> list

Reorder consumable cards.

**Parameters:**
- `G` (dict): Game state

**Returns:**
- `list`: Usually `[Actions.REARRANGE_CONSUMABLES, []]`

#### rearrange_hand(self, G: dict) -> list

Reorder cards in hand.

**Parameters:**
- `G` (dict): Game state

**Returns:**
- `list`: Usually `[Actions.REARRANGE_HAND, []]`

### Utility Methods

#### start_balatro_instance(self) -> None

Launch a new Balatro game instance.

**Note:** Only works on Windows with default Steam installation path.

#### stop_balatro_instance(self) -> None

Terminate the Balatro game instance.

#### sendcmd(self, cmd: str, **kwargs) -> None

Send a raw command to the game.

**Parameters:**
- `cmd` (str): Command string to send

#### actionToCmd(self, action: list) -> str

Convert action list to command string format.

**Parameters:**
- `action` (list): Action in list format

**Returns:**
- `str`: Formatted command string

#### random_seed(self) -> str

Generate a random 7-character game seed.

**Returns:**
- `str`: Random seed string (e.g., "1OGB5WO")

#### run_step(self) -> None

Execute one decision step of the bot.

#### run(self) -> None

Start the main bot execution loop.

## Actions Enum

Enumeration of all available game actions.

```python
class Actions(Enum):
    SELECT_BLIND = 1
    SKIP_BLIND = 2
    PLAY_HAND = 3
    DISCARD_HAND = 4
    END_SHOP = 5
    REROLL_SHOP = 6
    BUY_CARD = 7
    BUY_VOUCHER = 8
    BUY_BOOSTER = 9
    SELECT_BOOSTER_CARD = 10
    SKIP_BOOSTER_PACK = 11
    SELL_JOKER = 12
    USE_CONSUMABLE = 13
    SELL_CONSUMABLE = 14
    REARRANGE_JOKERS = 15
    REARRANGE_CONSUMABLES = 16
    REARRANGE_HAND = 17
    PASS = 18
    START_RUN = 19
    SEND_GAMESTATE = 20
```

### Action Descriptions

| Action | Value | Purpose | Parameters |
|--------|-------|---------|------------|
| `SELECT_BLIND` | 1 | Choose to play current blind | None |
| `SKIP_BLIND` | 2 | Skip current blind | None |
| `PLAY_HAND` | 3 | Play selected cards | Card indices |
| `DISCARD_HAND` | 4 | Discard selected cards | Card indices |
| `END_SHOP` | 5 | Leave the shop | None |
| `REROLL_SHOP` | 6 | Reroll shop contents | None |
| `BUY_CARD` | 7 | Purchase joker from shop | Card index |
| `BUY_VOUCHER` | 8 | Purchase voucher from shop | Voucher index |
| `BUY_BOOSTER` | 9 | Purchase booster pack | Booster index |
| `SELECT_BOOSTER_CARD` | 10 | Use booster card | Card index, targets |
| `SKIP_BOOSTER_PACK` | 11 | Skip booster pack | None |
| `SELL_JOKER` | 12 | Sell joker for money | Joker index |
| `USE_CONSUMABLE` | 13 | Use consumable card | Card index, targets |
| `SELL_CONSUMABLE` | 14 | Sell consumable card | Card index |
| `REARRANGE_JOKERS` | 15 | Reorder jokers | New order |
| `REARRANGE_CONSUMABLES` | 16 | Reorder consumables | New order |
| `REARRANGE_HAND` | 17 | Reorder hand cards | New order |
| `PASS` | 18 | No action (internal use) | None |
| `START_RUN` | 19 | Begin new game run | Deck, stake, seed |
| `SEND_GAMESTATE` | 20 | Request game state (internal) | None |

## State Enum

Enumeration of game states for state tracking.

```python
class State(Enum):
    SELECTING_HAND = 1
    HAND_PLAYED = 2
    DRAW_TO_HAND = 3
    GAME_OVER = 4
    SHOP = 5
    PLAY_TAROT = 6
    BLIND_SELECT = 7
    ROUND_EVAL = 8
    TAROT_PACK = 9
    PLANET_PACK = 10
    MENU = 11
    TUTORIAL = 12
    SPLASH = 13
    SANDBOX = 14
    SPECTRAL_PACK = 15
    DEMO_CTA = 16
    STANDARD_PACK = 17
    BUFFOON_PACK = 18
    NEW_ROUND = 19
```

### State Descriptions

| State | Value | Description |
|-------|-------|-------------|
| `SELECTING_HAND` | 1 | Player choosing cards to play/discard |
| `HAND_PLAYED` | 2 | Hand has been played, processing results |
| `DRAW_TO_HAND` | 3 | Drawing new cards to hand |
| `GAME_OVER` | 4 | Game has ended |
| `SHOP` | 5 | In shop phase |
| `PLAY_TAROT` | 6 | Using a tarot card |
| `BLIND_SELECT` | 7 | Choosing whether to play blind |
| `ROUND_EVAL` | 8 | Round results being calculated |
| `TAROT_PACK` | 9 | Opening tarot booster pack |
| `PLANET_PACK` | 10 | Opening planet booster pack |
| `MENU` | 11 | In main menu |
| `TUTORIAL` | 12 | In tutorial mode |
| `SPLASH` | 13 | Splash screen |
| `SANDBOX` | 14 | Sandbox mode |
| `SPECTRAL_PACK` | 15 | Opening spectral pack |
| `DEMO_CTA` | 16 | Demo call-to-action |
| `STANDARD_PACK` | 17 | Opening standard pack |
| `BUFFOON_PACK` | 18 | Opening buffoon pack |
| `NEW_ROUND` | 19 | Starting new round |

## Helper Functions

### cache_state(game_step: str, G: dict) -> None

Cache current game state to file for analysis.

**Parameters:**
- `game_step` (str): Identifier for the decision point
- `G` (dict): Game state to cache

**Example:**
```python
from gamestates import cache_state

def select_cards_from_hand(self, G):
    cache_state("card_selection", G)
    # ... decision logic
```

## Game State Module

The `gamestates.py` module provides state caching functionality.

### Functions

#### cache_state(game_step: str, G: dict) -> None

Save game state to JSON file with timestamp.

**File Structure:**
```
gamestate_cache/
├── card_selection/
│   ├── 20231201120001123456.json
│   └── 20231201120005234567.json
└── shop_action/
    └── 20231201120010345678.json
```

**JSON Format:**
```json
{
  "waitingFor": "select_cards_from_hand",
  "waitingForAction": true,
  "state": 1,
  "hand": [...],
  "jokers": [...],
  "shop": {...},
  "ante": {...}
}
```

## Usage Examples

### Basic Bot Implementation

```python
from bot import Bot, Actions

class MyBot(Bot):
    def __init__(self):
        super().__init__(deck="Red Deck", stake=1)
        
    def skip_or_select_blind(self, G):
        return [Actions.SELECT_BLIND]
    
    def select_cards_from_hand(self, G):
        return [Actions.PLAY_HAND, [1]]
    
    # ... implement other required methods

# Run the bot
bot = MyBot()
bot.run()
```

### Advanced State Management

```python
class StatefulBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state["strategy"] = "early_game"
        self.state["rounds_played"] = 0
    
    def select_cards_from_hand(self, G):
        self.state["rounds_played"] += 1
        
        if self.state["rounds_played"] > 5:
            self.state["strategy"] = "mid_game"
        
        if self.state["strategy"] == "early_game":
            return self.conservative_play(G)
        else:
            return self.aggressive_play(G)
```

### Error Handling

```python
def robust_card_selection(self, G):
    try:
        hand = G.get("hand", [])
        if not hand:
            return [Actions.PLAY_HAND, []]
        
        # Complex decision logic here
        return self.advanced_strategy(hand)
        
    except Exception as e:
        print(f"Error in card selection: {e}")
        # Safe fallback
        return [Actions.PLAY_HAND, [1]] if G.get("hand") else [Actions.PLAY_HAND, []]
```

---

*This API reference covers all public interfaces for Python bot development. For Lua API details, see [Lua API Reference](lua-api.md).* 