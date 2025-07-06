# Bot Development Guide

This guide teaches you how to create custom bots for Balatro using the Balatrobot framework.

## Overview

Balatrobot allows you to create automated players (bots) that can play Balatro by implementing decision-making logic in Python. Your bot communicates with the game through a socket connection, receiving game state information and sending back actions to perform.

A bot is essentially a Python class that inherits from the `Bot` base class and implements specific methods that get called at different points during gameplay. The framework uses a modern **ActionSchema** API that returns structured dictionaries instead of plain lists, making the code more readable and type-safe.

## Key Concepts

- **ActionSchema**: A structured dictionary format for bot actions with `action` and `args` fields
- **Game State (`env`)**: Complete information about the current game situation
- **Actions Enum**: Predefined action types your bot can perform
- **Type Safety**: Modern Python type hints ensure your bot is robust and maintainable

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

The new API uses a consistent format for all actions:

```python
# ActionSchema structure
{
    "action": Actions.SOME_ACTION,  # An Actions enum value
    "args": None | [] | [1, 2, 3]   # Arguments for the action (optional)
}
```

**Key Benefits:**
- **Type Safety**: Clear structure with defined types
- **Readability**: Explicit action and arguments
- **Consistency**: Same format across all methods
- **Extensibility**: Easy to add new action types

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

- `Decks.RED`, `Decks.BLUE`, `Decks.YELLOW`, `Decks.GREEN`, `Decks.BLACK`
- `Decks.MAGIC`, `Decks.NEBULA`, `Decks.GHOST`, `Decks.ABANDONED`
- `Decks.CHECKERED`, `Decks.ZODIAC`, `Decks.PAINTED`, `Decks.ANAGLYPH`
- `Decks.PLASMA`, `Decks.ERRATIC`

**Available Stakes:**

- `Stakes.WHITE` (1), `Stakes.RED` (2), `Stakes.GREEN` (3), `Stakes.BLACK` (4)
- `Stakes.BLUE` (5), `Stakes.PURPLE` (6), `Stakes.ORANGE` (7), `Stakes.GOLD` (8)

## Required Methods

All bot methods receive an `env` parameter containing the current game state. The game state contains all information about the current situation, including cards in hand, jokers, consumables, blind information, and more.

!!! note
    For detailed information about the game state structure, see the [Game State Reference](game-state.md) page.

**skip_or_select_blind(env)**

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

**When called:** At the start of each blind selection phase

**Available Actions:**
- `Actions.SELECT_BLIND` - Choose to play the blind
- `Actions.SKIP_BLIND` - Skip the blind (costs money)

**select_cards_from_hand(env)**

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

**When called:** During the playing phase when you need to make a hand

**Available Actions:**
- `Actions.PLAY_HAND` - Play specified cards as a poker hand
- `Actions.DISCARD_HAND` - Discard specified cards to draw new ones

!!! tip
    Card indices are 1-based (first card is 1, not 0). You can access hand information through `env['hand']` to make intelligent decisions.

**select_shop_action(env)**

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

**When called:** During the shop phase between rounds

**Available Actions:**
- `Actions.END_SHOP` - Leave the shop
- `Actions.REROLL_SHOP` - Reroll shop items (costs money)
- `Actions.BUY_CARD` - Buy a joker card (provide index)
- `Actions.BUY_VOUCHER` - Buy a voucher (provide index)
- `Actions.BUY_BOOSTER` - Buy a booster pack (provide index)

**select_booster_action(env)**

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

**When called:** When opening booster packs

**Available Actions:**
- `Actions.SKIP_BOOSTER_PACK` - Skip the pack without taking cards
- `Actions.SELECT_BOOSTER_CARD` - Select specific cards from the pack

**sell_jokers(env)**

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

**When called:** During joker management phases

**Available Actions:**
- `Actions.SELL_JOKER` - Sell specific jokers (provide indices list)

**rearrange_jokers(env)**

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

**When called:** During joker management phases

**Available Actions:**
- `Actions.REARRANGE_JOKERS` - Rearrange jokers (provide new order)

**use_or_sell_consumables(env)**

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

**When called:** During consumable management phases

**Available Actions:**
- `Actions.USE_CONSUMABLE` - Use specific consumable cards
- `Actions.SELL_CONSUMABLE` - Sell specific consumable cards

**rearrange_consumables(env)**

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

**When called:** During consumable management phases

**Available Actions:**
- `Actions.REARRANGE_CONSUMABLES` - Rearrange consumables (provide new order)

**rearrange_hand(env)**

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

**When called:** During hand management phases

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

## Bot Configuration Examples

```python
# Basic bot with default settings
bot = MyFirstBot()

# Bot with custom deck and stake
bot = MyFirstBot(deck=Decks.BLUE, stake=Stakes.RED)

# Bot with random seed
bot = MyFirstBot(seed=Bot.random_seed())

# Bot with specific seed for testing
bot = MyFirstBot(seed="EXAMPLE")
```

## Basic Bot Template

Here's a minimal bot template you can use as a starting point:

```python
from typing import Any
from balatrobot import Actions, Bot, Decks, Stakes
from balatrobot.base import ActionSchema


class MyBot(Bot):
    """A simple bot template for getting started."""

    def __init__(
        self,
        deck: Decks = Decks.RED,
        stake: Stakes = Stakes.WHITE,
        seed: str = "",
    ) -> None:
        super().__init__(deck=deck, stake=stake, seed=seed)

    def skip_or_select_blind(self, env: dict[str, Any]) -> ActionSchema:
        """Always select blinds to play them."""
        return {"action": Actions.SELECT_BLIND, "args": None}

    def select_cards_from_hand(self, env: dict[str, Any]) -> ActionSchema:
        """Always play the first 5 cards."""
        return {"action": Actions.PLAY_HAND, "args": [1, 2, 3, 4, 5]}

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
    bot = MyBot()
    bot.running = True
    bot.run()
```

## Best Practices

**1. Start Simple**

Begin with the basic template above and gradually add more sophisticated logic:

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

!!! tip
    The best way to learn is by experimenting! Start with the basic template and gradually add features as you understand the game better.

---

*Ready to create more advanced bots? Check out the [API Protocol Reference](api-protocol.md) for detailed about Lua socket API.*