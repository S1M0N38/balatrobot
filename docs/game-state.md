# Game State Reference

Complete reference for understanding the game state object provided to bot methods.

## Overview

The game state object (`G`) is a comprehensive dictionary containing all information about the current state of the Balatro game. This object is passed to all bot methods and provides access to:

- Current hand cards
- Available jokers and their effects
- Shop contents and prices
- Blind information and requirements
- Player stats (money, score, etc.)
- Consumable cards (tarot, planet, spectral)

## Game State Structure

The `G` object contains the following main sections:

```python
G = {
    "hand": {...},           # Cards in hand
    "jokers": {...},         # Joker cards
    "shop": {...},           # Shop contents
    "ante": {...},           # Blind information
    "consumables": {...},    # Tarot/planet/spectral cards
    "deck": {...},           # Deck information
    "player": {...},         # Player stats
    # ... additional game state data
}
```

## Hand Information

Access cards currently in your hand:

```python
def select_cards_from_hand(self, G):
    hand_cards = G["hand"]
    # hand_cards contains list of card objects
    for i, card in enumerate(hand_cards):
        print(f"Card {i+1}: {card['rank']} of {card['suit']}")
```

## Jokers

Information about jokers in play:

```python
def sell_jokers(self, G):
    jokers = G["jokers"]
    # Access joker properties
    for i, joker in enumerate(jokers):
        print(f"Joker {i+1}: {joker['name']} - {joker['effect']}")
```

## Shop

Shop contents and pricing:

```python
def select_shop_action(self, G):
    shop = G["shop"]
    cards = shop.get("cards", [])
    vouchers = shop.get("vouchers", [])
    boosters = shop.get("boosters", [])
```

## Blinds

Current blind information:

```python
def skip_or_select_blind(self, G):
    blind_info = G["ante"]["blinds"]
    current_blind = blind_info.get("ondeck")
    blind_requirement = blind_info.get("requirement")
```

## Consumables

Tarot, planet, and spectral cards:

```python
def use_or_sell_consumables(self, G):
    consumables = G["consumables"]
    for i, card in enumerate(consumables):
        card_type = card.get("type")  # "tarot", "planet", "spectral"
        card_name = card.get("name")
```

## Examples

### Checking Hand for Specific Cards

```python
def has_pair(self, G):
    hand = G["hand"]
    ranks = [card["rank"] for card in hand]
    return len(set(ranks)) < len(ranks)
```

### Finding Affordable Shop Items

```python
def find_affordable_items(self, G):
    money = G["player"]["money"]
    shop_cards = G["shop"]["cards"]
    affordable = [i for i, card in enumerate(shop_cards) 
                  if card["price"] <= money]
    return affordable
```

---

*For more detailed examples, see [Examples](examples.md) and [Python API](python-api.md).* 