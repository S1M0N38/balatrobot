# Game State Reference

Reference for the game state object provided to bot methods.

## Overview

The game state object (`G`) contains all information about the current Balatro game state. This object is passed to all bot methods and provides access to:

- Current hand cards
- Available jokers  
- Shop contents and prices
- Blind information
- Player stats (money, score, etc.)
- Consumable cards (tarot, planet, spectral)

## Game State Structure

The `G` object contains these main sections:

```python
G = {
    "hand": [...],           # Cards in hand
    "jokers": [...],         # Joker cards
    "shop": {...},           # Shop contents  
    "ante": {...},           # Blind information
    "consumables": [...],    # Tarot/planet/spectral cards
    "current_round": {...},  # Round information
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
        print(f"Card {i+1}: {card['name']} - {card['suit']} {card['value']}")
```

**Card Properties:**
- `card["label"]` - Card label (e.g. "base_card")
- `card["name"]` - Full card name (e.g. "3 of Hearts")  
- `card["suit"]` - Card suit ("Hearts", "Diamonds", "Clubs", "Spades")
- `card["value"]` - Card value (number)
- `card["card_key"]` - Card key (e.g. "H_3")

## Jokers

Information about jokers in play:

```python
def sell_jokers(self, G):
    jokers = G["jokers"]
    # Access joker properties (same structure as cards)
    for i, joker in enumerate(jokers):
        print(f"Joker {i+1}: {joker['name']}")
```

## Shop

Shop contents and pricing:

```python
def select_shop_action(self, G):
    shop = G["shop"]
    cards = shop.get("cards", [])
    vouchers = shop.get("vouchers", [])
    boosters = shop.get("boosters", [])
    reroll_cost = shop.get("reroll_cost", 5)
```

## Blinds

Current blind information:

```python
def skip_or_select_blind(self, G):
    blind_type = G["ante"]["blinds"]["ondeck"]  # "Small", "Big", or "Boss"
    if blind_type == "Small" or blind_type == "Big":
        return [Actions.SKIP_BLIND]
    else:
        return [Actions.SELECT_BLIND]
```

## Round Information

Current round state:

```python
def select_cards_from_hand(self, G):
    discards_left = G["current_round"]["discards_left"]
    if discards_left > 0:
        return [Actions.DISCARD_HAND, [1, 2]]
    else:
        return [Actions.PLAY_HAND, [1]]
```

## Examples

### Finding Cards by Suit

```python
def find_flush(self, G):
    suit_count = {"Hearts": 0, "Diamonds": 0, "Clubs": 0, "Spades": 0}
    for card in G["hand"]:
        suit_count[card["suit"]] += 1
    
    most_common_suit = max(suit_count, key=suit_count.get)
    if suit_count[most_common_suit] >= 5:
        # We have a flush!
        flush_cards = [card for card in G["hand"] if card["suit"] == most_common_suit]
        return flush_cards[:5]
    return []
```

### Checking Available Actions

```python
def can_discard(self, G):
    return G["current_round"]["discards_left"] > 0

def has_jokers_to_sell(self, G):
    return len(G["jokers"]) > 0
```

---

*For more detailed examples, see [Examples](examples.md) and [Python API](python-api.md).* 