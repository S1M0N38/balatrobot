# Bot Development Guide

This guide teaches you how to create custom bots for Balatro using the Balatrobot framework.

## Overview

Balatrobot allows you to create automated players (bots) that can play Balatro by implementing decision-making logic in Python. Your bot communicates with the game through a socket connection, receiving game state information and sending back actions to perform.

A bot is essentially a Python class that inherits from the `Bot` base class and implements specific methods that get called at different points during gameplay. The framework uses an **ActionSchema** API that returns structured dictionaries, making the code readable and type-safe.

A complete working example bot is available at `bots/example.py` which you can reference while building your own bot.

## Development Environment Setup

The Balatrobot project provides a complete development environment with all necessary tools and resources for building bots.

### Bot File Location

When creating new bots, place your files in the `bots/` directory using one of these recommended patterns:

- **Single file bots**: `bots/my_new_bot.py`
- **Complex bots**: `bots/my_new_bot/main.py` (for bots with multiple modules)

Both approaches are considered best practices and allow for easy organization and discovery of your bot implementations.

### Pre-configured Development Environment

The project comes with a fully configured Python development environment:

- **Python Virtual Environment**: Pre-installed with the balatrobot package and all dependencies
- **Code Quality Tools**: Linting, type checking, and formatting configured in `pyproject.toml`
- **Continuous Integration**: Working CI pipeline ensures code quality standards

### Available Documentation and Resources

The repository contains extensive documentation and reference materials:

- **Comprehensive API Documentation**: Complete guides for bot development and API usage
- **Steamodded Wiki**: Included as a git submodule (clone with `--recurse-submodules` for LLM-friendly context)
- **Source Code Access**: Full balatrobot Python source code and Lua implementation for reference
- **Example Implementations**: Working bot examples to learn from and build upon

!!! tip "Enhanced LLM Development Experience"
    This rich documentation ecosystem is particularly beneficial when working
    with Large Language Models (LLMs) for bot development. The complete source
    code, comprehensive documentation, and Steamodded wiki provide extensive
    context that helps LLMs understand the framework and generate more accurate,
    contextually-aware code suggestions.

### Getting Started

To begin developing your bot:

1. Navigate to the `bots/` directory
2. Set up your development environment by copying and sourcing the environment file
3. Create your bot file using the recommended naming convention
4. Use the existing Python environment (balatrobot is already installed)
5. Leverage the code quality tools and CI pipeline for professional development
6. Reference the extensive documentation and source code for guidance

### Environment Setup

Before developing or running bots, you need to set up the development environment by configuring the `.envrc` file:

=== "Windows"

    ``` sh
    cd %AppData%/Balatro/Mods/balatrobot
    copy .envrc.example .envrc
    .envrc
    ```

=== "MacOS"

    ``` sh
    cd "/Users/$USER/Library/Application Support/Balatro/Mods/balatrobot"
    cp .envrc.example .envrc
    source .envrc
    ```

=== "Linux"

    ``` sh
    cd ~/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods/balatrobot
    cp .envrc.example .envrc
    source .envrc
    ```

!!! warning "Always Source Environment"

    Remember to source the `.envrc` file every time you start a new terminal session before developing or running bots. The environment variables are essential for proper bot functionality.

!!! tip "Automatic Environment Loading with direnv"

    For a better development experience, consider using [direnv](https://direnv.net/) to automatically load and unload environment variables when entering and leaving the project directory.

    After installing direnv and hooking it into your shell:

    ```sh
    # Allow direnv to load the .envrc file automatically
    direnv allow .
    ```

    This eliminates the need to manually source `.envrc` every time you work on the project.

## Creating Your First Bot

Let's examine a complete example bot to understand how to implement your own:

```python
"""Simple bot example demonstrating the balatrobot API.

This example shows how to create a basic bot that plays Balatro using
a predefined sequence of actions.
"""

import itertools
from typing import Any, Iterator

from balatrobot import Actions, Bot, Decks, Stakes
from balatrobot.base import ActionSchema

# Predefined sequence of actions using the ActionSchema format
plays: Iterator[ActionSchema] = itertools.cycle(
    [
        # This sequence of plays is winning for the first round
        # for the seed "EXAMPLE" and the deck "Red Deck" with stake 1.
        {"action": Actions.DISCARD_HAND, "args": [2, 3, 4, 6]},
        {"action": Actions.DISCARD_HAND, "args": [1, 2, 6, 8]},
        {"action": Actions.PLAY_HAND, "args": [2, 3, 5, 6, 7]},
        {"action": Actions.PLAY_HAND, "args": [3, 4, 7, 8]},
    ]
)


class MyFirstBot(Bot):
    """Example bot implementation using the ActionSchema API.

    This bot demonstrates a simple strategy using predefined actions.
    It always selects blinds, uses a fixed sequence of plays, and
    skips most optional actions.
    """

    def __init__(
        self,
        deck: Decks = Decks.RED,
        stake: Stakes = Stakes.WHITE,
        seed: str = "EXAMPLE",
    ) -> None:
        super().__init__(deck=deck, stake=stake, seed=seed)

    def skip_or_select_blind(self, env: dict[str, Any]) -> ActionSchema:
        """Always select blinds to play them."""
        return {"action": Actions.SELECT_BLIND, "args": None}

    def select_cards_from_hand(self, env: dict[str, Any]) -> ActionSchema:
        """Use predefined card selection sequence."""
        return next(plays)

    def select_shop_action(self, env: dict[str, Any]) -> ActionSchema:
        """Always leave the shop immediately."""
        return {"action": Actions.END_SHOP, "args": None}

    def select_booster_action(self, env: dict[str, Any]) -> ActionSchema:
        """Skip all booster packs."""
        return {"action": Actions.SKIP_BOOSTER_PACK, "args": None}

    def sell_jokers(self, env: dict[str, Any]) -> ActionSchema:
        """Don't sell any jokers."""
        return {"action": Actions.SELL_JOKER, "args": []}

    def rearrange_jokers(self, env: dict[str, Any]) -> ActionSchema:
        """Don't rearrange jokers."""
        return {"action": Actions.REARRANGE_JOKERS, "args": []}

    def use_or_sell_consumables(self, env: dict[str, Any]) -> ActionSchema:
        """Don't use consumables."""
        return {"action": Actions.USE_CONSUMABLE, "args": []}

    def rearrange_consumables(self, env: dict[str, Any]) -> ActionSchema:
        """Don't rearrange consumables."""
        return {"action": Actions.REARRANGE_CONSUMABLES, "args": []}

    def rearrange_hand(self, env: dict[str, Any]) -> ActionSchema:
        """Don't rearrange hand."""
        return {"action": Actions.REARRANGE_HAND, "args": []}


if __name__ == "__main__":
    bot = MyFirstBot()
    bot.running = True
    bot.run()
```

## ActionSchema Format

The ActionSchema API uses a consistent format for all actions:

```python
# ActionSchema structure
{
    "action": Actions.SOME_ACTION,  # An Actions enum value
    "args": None | [] | [1, 2, 3]   # Arguments for the action (optional)
}
```

## Bot Class Structure

1. **Inheritance**: Your bot must inherit from the `Bot` base class
2. **Constructor**: Call `super().__init__()` with your desired game parameters
3. **Method Implementation**: Implement all required methods (the framework will verify this)
4. **Type Hints**: Use proper type annotations for better code quality

## Constructor Parameters

The bot constructor accepts several parameters to customize the game:

```python
def __init__(
    self,
    deck: Decks = Decks.RED,           # Which deck to use
    stake: Stakes = Stakes.WHITE,      # Difficulty level (1-8)
    seed: str = "EXAMPLE",             # Random seed (optional)
    challenge: str | None = None,      # Challenge mode (optional)
    bot_port: int = 12346,             # Communication port (optional)
) -> None:
```

**Available Decks:**

`Decks.RED`, `Decks.BLUE`, `Decks.YELLOW`, `Decks.GREEN`, `Decks.BLACK`,
`Decks.MAGIC`, `Decks.NEBULA`, `Decks.GHOST`, `Decks.ABANDONED`,
`Decks.CHECKERED`, `Decks.ZODIAC`, `Decks.PAINTED`, `Decks.ANAGLYPH`,
`Decks.PLASMA`, `Decks.ERRATIC`.

**Available Stakes:**

`Stakes.WHITE` (1), `Stakes.RED` (2), `Stakes.GREEN` (3), `Stakes.BLACK` (4),
`Stakes.BLUE` (5), `Stakes.PURPLE` (6), `Stakes.ORANGE` (7), `Stakes.GOLD` (8).

## Required Methods

All bot methods receive an `env` parameter containing the current game state. The game state contains all information about the current situation, including cards in hand, jokers, consumables, blind information, and more.

### `skip_or_select_blind`

Called when the bot needs to choose whether to skip or select a blind.

```python
def skip_or_select_blind(self, env: dict[str, Any]) -> ActionSchema:
    """Decide whether to skip or select a blind.

    Args:
        env: Current game state containing blind information

    Returns:
        ActionSchema with SELECT_BLIND or SKIP_BLIND action
    """
    # Always select blinds to play them
    return {"action": Actions.SELECT_BLIND, "args": None}

    # Or to skip a blind:
    # return {"action": Actions.SKIP_BLIND, "args": None}
```

This method is called at the start of each blind selection phase.

**Available Actions:**

- `Actions.SELECT_BLIND` - Choose to play the blind
- `Actions.SKIP_BLIND` - Skip the blind (costs money)

### `select_cards_from_hand`

Called when the bot needs to choose cards to play or discard during a round.

```python
def select_cards_from_hand(self, env: dict[str, Any]) -> ActionSchema:
    """Select cards from hand to play or discard.

    Args:
        env: Current game state with hand information

    Returns:
        ActionSchema with PLAY_HAND or DISCARD_HAND action
    """
    # Play the first 5 cards
    return {"action": Actions.PLAY_HAND, "args": [1, 2, 3, 4, 5]}

    # Or discard specific cards:
    # return {"action": Actions.DISCARD_HAND, "args": [1, 3, 5]}
```

This method is called during the playing phase when you need to make a hand.

**Available Actions:**

- `Actions.PLAY_HAND` - Play specified cards as a poker hand
- `Actions.DISCARD_HAND` - Discard specified cards to draw new ones

!!! warning 1-based indices
    Card indices are 1-based (first card is 1, not 0). You can access hand information through `env['hand']` to make intelligent decisions.

### `select_shop_action`

Called when the bot is in the shop and needs to decide what to do.

```python
def select_shop_action(self, env: dict[str, Any]) -> ActionSchema:
    """Select an action to perform in the shop.

    Args:
        env: Current game state with shop information

    Returns:
        ActionSchema with shop action
    """
    # Leave the shop immediately
    return {"action": Actions.END_SHOP, "args": None}

    # Or buy a joker (index 0):
    # return {"action": Actions.BUY_CARD, "args": [0]}

    # Or reroll the shop:
    # return {"action": Actions.REROLL_SHOP, "args": None}
```

This method is called during the shop phase between rounds.

**Available Actions:**

- `Actions.END_SHOP` - Leave the shop
- `Actions.REROLL_SHOP` - Reroll shop items (costs money)
- `Actions.BUY_CARD` - Buy a joker card (provide index)
- `Actions.BUY_VOUCHER` - Buy a voucher (provide index)
- `Actions.BUY_BOOSTER` - Buy a booster pack (provide index)

### `select_booster_action`

Called when the bot encounters a booster pack and needs to choose cards or skip.

```python
def select_booster_action(self, env: dict[str, Any]) -> ActionSchema:
    """Select an action for booster packs.

    Args:
        env: Current game state with booster pack information

    Returns:
        ActionSchema with booster action
    """
    # Skip all booster packs
    return {"action": Actions.SKIP_BOOSTER_PACK, "args": None}

    # Or select specific cards from the pack:
    # return {"action": Actions.SELECT_BOOSTER_CARD, "args": [0, 1]}
```

This method is called when opening booster packs.

**Available Actions:**

- `Actions.SKIP_BOOSTER_PACK` - Skip the pack without taking cards
- `Actions.SELECT_BOOSTER_CARD` - Select specific cards from the pack

### `sell_jokers`

Called when the bot can sell jokers for money.

```python
def sell_jokers(self, env: dict[str, Any]) -> ActionSchema:
    """Sell jokers from your collection.

    Args:
        env: Current game state with joker information

    Returns:
        ActionSchema with SELL_JOKER action
    """
    # Don't sell any jokers
    return {"action": Actions.SELL_JOKER, "args": []}

    # Or sell specific jokers (indices 0 and 2):
    # return {"action": Actions.SELL_JOKER, "args": [0, 2]}
```

This method is called during joker management phases.

**Available Actions:**

- `Actions.SELL_JOKER` - Sell specific jokers (provide indices list)

### `rearrange_jokers`

Called when the bot can rearrange the order of jokers.

```python
def rearrange_jokers(self, env: dict[str, Any]) -> ActionSchema:
    """Rearrange jokers in your collection.

    Args:
        env: Current game state with joker information

    Returns:
        ActionSchema with REARRANGE_JOKERS action
    """
    # Don't rearrange jokers
    return {"action": Actions.REARRANGE_JOKERS, "args": []}

    # Or specify new order:
    # return {"action": Actions.REARRANGE_JOKERS, "args": [2, 0, 1]}
```

This method is called during joker management phases.

**Available Actions:**

- `Actions.REARRANGE_JOKERS` - Rearrange jokers (provide new order)

### `use_or_sell_consumables`

Called when the bot can use or sell consumable cards (Tarot, Planet, Spectral).

```python
def use_or_sell_consumables(self, env: dict[str, Any]) -> ActionSchema:
    """Use or sell consumable cards.

    Args:
        env: Current game state with consumable information

    Returns:
        ActionSchema with consumable action
    """
    # Don't use consumables
    return {"action": Actions.USE_CONSUMABLE, "args": []}

    # Or use a specific consumable:
    # return {"action": Actions.USE_CONSUMABLE, "args": [0]}
 
    # Or sell consumables:
    # return {"action": Actions.SELL_CONSUMABLE, "args": [0, 1]}
```

This method is called during consumable management phases.

**Available Actions:**

- `Actions.USE_CONSUMABLE` - Use specific consumable cards
- `Actions.SELL_CONSUMABLE` - Sell specific consumable cards

### `rearrange_consumables`

Called when the bot can rearrange the order of consumable cards.

```python
def rearrange_consumables(self, env: dict[str, Any]) -> ActionSchema:
    """Rearrange consumable cards.

    Args:
        env: Current game state with consumable information

    Returns:
        ActionSchema with REARRANGE_CONSUMABLES action
    """
    # Don't rearrange consumables
    return {"action": Actions.REARRANGE_CONSUMABLES, "args": []}

    # Or specify new order:
    # return {"action": Actions.REARRANGE_CONSUMABLES, "args": [1, 0, 2]}
```

This method is called during consumable management phases.

**Available Actions:**

- `Actions.REARRANGE_CONSUMABLES` - Rearrange consumables (provide new order)

### `rearrange_hand`

Called when the bot can rearrange cards in hand.

```python
def rearrange_hand(self, env: dict[str, Any]) -> ActionSchema:
    """Rearrange cards in your hand.

    Args:
        env: Current game state with hand information

    Returns:
        ActionSchema with REARRANGE_HAND action
    """
    # Don't rearrange hand
    return {"action": Actions.REARRANGE_HAND, "args": []}

    # Or specify new order:
    # return {"action": Actions.REARRANGE_HAND, "args": [4, 3, 2, 1, 0]}
```

This method is called during hand management phases.

**Available Actions:**

- `Actions.REARRANGE_HAND` - Rearrange hand cards (provide new order)

## Running Your Bot

Once you've implemented all required methods, you can run your bot:

```python
if __name__ == "__main__":
    # Create bot instance
    bot = MyFirstBot()

    # Set it to running state
    bot.running = True

    # Start the bot
    bot.run()
```

## Best Practices

**1. Start Simple**

Begin with simple logic and gradually add more sophisticated behavior:

```python
def select_cards_from_hand(self, env: dict[str, Any]) -> ActionSchema:
    """Start with simple logic, then improve."""

    # Version 1: Always play first 5 cards
    return {"action": Actions.PLAY_HAND, "args": [1, 2, 3, 4, 5]}

    # Version 2: Add basic hand evaluation
    # hand_cards = env.get('hand', [])
    # if len(hand_cards) >= 5:
    #     return {"action": Actions.PLAY_HAND, "args": [1, 2, 3, 4, 5]}
    # else:
    #     return {"action": Actions.DISCARD_HAND, "args": [1]}
```

**2. Use Type Hints**

Always use proper type hints for better code quality:

```python
from typing import Any
from balatrobot.base import ActionSchema

def select_shop_action(self, env: dict[str, Any]) -> ActionSchema:
    """Type hints help catch errors early."""
    return {"action": Actions.END_SHOP, "args": None}
```

**3. Document Your Logic**

Add clear comments explaining your bot's decision-making:

```python
def select_cards_from_hand(self, env: dict[str, Any]) -> ActionSchema:
    """Select cards using a simple high-card strategy."""
    # TODO: Implement actual hand evaluation
    # For now, just play the first 5 cards
    return {"action": Actions.PLAY_HAND, "args": [1, 2, 3, 4, 5]}
```

**4. Test Incrementally**

Test your bot frequently with simple scenarios:

```python
# Test with a known seed for reproducible results
bot = MyBot(seed="EXAMPLE")
bot.running = True
bot.run()
```

## Common Pitfalls

1. **Index Errors**: Remember that card indices are 1-based, not 0-based
2. **Missing Args**: Always provide the `args` field, even if it's `None` or `[]`
3. **Wrong Action Type**: Make sure you're using the correct `Actions` enum value
4. **Forgetting Type Hints**: Use proper type annotations for better development experience

## Next Steps

Once you have a basic bot working:

1. **Study the Game State**: Learn about the structure of the `env` parameter
2. **Implement Smart Logic**: Add decision-making based on game state
3. **Test Different Scenarios**: Try different decks, stakes, and seeds
4. **Debug and Iterate**: Use the game state cache to analyze decisions

---

*Ready to create more advanced bots? Check out the [API Protocol Reference](api-protocol.md) for detailed about Lua socket API.*
