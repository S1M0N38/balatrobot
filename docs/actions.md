# Actions Reference

Complete reference for all available actions in Balatrobot.

## Overview

Actions in Balatrobot are represented as lists that tell the game what to do. Each action follows a specific format and is returned from bot methods to control game behavior.

All actions are defined in the `Actions` enum and should be imported:

```python
from bot import Bot, Actions
```

## Action Format

Actions follow this general format:

```python
[Actions.ACTION_TYPE, [parameters], [additional_parameters]]
```

- First element: Action type from `Actions` enum
- Second element: List of parameters (often indices)
- Third element: Additional parameters when needed

## Blind Actions

### SELECT_BLIND
Select the current blind to play.

```python
def skip_or_select_blind(self, G):
    return [Actions.SELECT_BLIND]
```

### SKIP_BLIND
Skip the current blind (forfeit ante).

```python
def skip_or_select_blind(self, G):
    return [Actions.SKIP_BLIND]
```

## Hand Actions

### PLAY_HAND
Play selected cards from hand.

```python
def select_cards_from_hand(self, G):
    # Play cards at indices 1 and 3 (1-based indexing)
    return [Actions.PLAY_HAND, [1, 3]]
```

### DISCARD_HAND
Discard selected cards from hand.

```python
def select_cards_from_hand(self, G):
    # Discard cards at indices 2, 4, 5
    return [Actions.DISCARD_HAND, [2, 4, 5]]
```

## Shop Actions

### BUY_CARD
Purchase a card from the shop.

```python
def select_shop_action(self, G):
    # Buy the first card in shop
    return [Actions.BUY_CARD, [1]]
```

### BUY_VOUCHER
Purchase a voucher from the shop.

```python
def select_shop_action(self, G):
    # Buy the first voucher
    return [Actions.BUY_VOUCHER, [1]]
```

### BUY_BOOSTER
Purchase a booster pack from the shop.

```python
def select_shop_action(self, G):
    # Buy the first booster pack
    return [Actions.BUY_BOOSTER, [1]]
```

### REROLL_SHOP
Reroll the shop contents (costs money).

```python
def select_shop_action(self, G):
    return [Actions.REROLL_SHOP]
```

### END_SHOP
Exit the shop phase.

```python
def select_shop_action(self, G):
    return [Actions.END_SHOP]
```

## Joker Actions

### SELL_JOKER
Sell jokers for money.

```python
def sell_jokers(self, G):
    # Sell jokers at positions 1 and 3
    return [Actions.SELL_JOKER, [1, 3]]
    
    # Sell no jokers
    return [Actions.SELL_JOKER, []]
```

### REARRANGE_JOKERS
Reorder jokers (usually no parameters needed).

```python
def rearrange_jokers(self, G):
    return [Actions.REARRANGE_JOKERS, []]
```

## Consumable Actions

### USE_CONSUMABLE
Use a consumable card (tarot, planet, spectral).

```python
def use_or_sell_consumables(self, G):
    # Use consumable at index 1, targeting cards at indices 2 and 4
    return [Actions.USE_CONSUMABLE, [1], [2, 4]]
    
    # Use consumable without targets
    return [Actions.USE_CONSUMABLE, [1], []]
    
    # Do nothing
    return [Actions.USE_CONSUMABLE, []]
```

### SELL_CONSUMABLE
Sell a consumable card for money.

```python
def use_or_sell_consumables(self, G):
    # Sell consumable at index 1
    return [Actions.SELL_CONSUMABLE, [1]]
```

### REARRANGE_CONSUMABLES
Reorder consumable cards.

```python
def rearrange_consumables(self, G):
    return [Actions.REARRANGE_CONSUMABLES, []]
```

## Booster Actions

### SELECT_BOOSTER_CARD
Select a card from an opened booster pack.

```python
def select_booster_action(self, G):
    # Select card 1 from booster, place at position 2
    return [Actions.SELECT_BOOSTER_CARD, [1], [2]]
```

### SKIP_BOOSTER_PACK
Skip the current booster pack without selecting.

```python
def select_booster_action(self, G):
    return [Actions.SKIP_BOOSTER_PACK]
```

## Arrangement Actions

### REARRANGE_HAND
Reorder cards in hand.

```python
def rearrange_hand(self, G):
    return [Actions.REARRANGE_HAND, []]
```

## Examples

### Conditional Actions Based on Game State

```python
def select_cards_from_hand(self, G):
    hand = G["hand"]
    money = G["player"]["money"]
    
    # Play high-value cards if we need money
    if money < 5:
        high_cards = [i+1 for i, card in enumerate(hand) 
                     if card["rank"] in ["King", "Queen", "Jack"]]
        if high_cards:
            return [Actions.PLAY_HAND, high_cards[:2]]
    
    # Otherwise discard low cards
    low_cards = [i+1 for i, card in enumerate(hand) 
                if card["rank"] in ["2", "3", "4"]]
    return [Actions.DISCARD_HAND, low_cards[:3]]
```

### Smart Shop Decisions

```python
def select_shop_action(self, G):
    money = G["player"]["money"]
    shop_cards = G["shop"]["cards"]
    
    # Buy affordable jokers first
    for i, card in enumerate(shop_cards):
        if card["type"] == "joker" and card["price"] <= money:
            return [Actions.BUY_CARD, [i+1]]
    
    # Reroll if we have extra money
    if money > 10:
        return [Actions.REROLL_SHOP]
    
    return [Actions.END_SHOP]
```

---

*For more examples and patterns, see [Bot Development Guide](bot-development.md) and [Examples](examples.md).* 