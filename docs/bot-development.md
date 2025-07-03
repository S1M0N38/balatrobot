# Bot Development Guide

This guide teaches you how to create custom bots for Balatro using the Balatrobot framework.

## Bot Development Basics

### Bot Architecture

Every bot in Balatrobot extends the base `Bot` class and implements specific decision-making methods:

```python
from bot import Bot, Actions

class MyBot(Bot):
    def __init__(self, deck, stake=1, seed=None, challenge=None, bot_port=12346):
        super().__init__(deck, stake, seed, challenge, bot_port)
        # Initialize bot-specific state
        self.strategy = "aggressive"
        
    # Required: Implement all decision methods
    def skip_or_select_blind(self, G):
        # Decision: Skip or play the current blind
        
    def select_cards_from_hand(self, G):
        # Decision: Play or discard cards from hand
        
    # ... implement other required methods
```

### Required Methods

Every bot must implement these methods:

| Method | Purpose | Return Value |
|--------|---------|--------------|
| `skip_or_select_blind(self, G)` | Choose whether to skip or play blind | `[Actions.SELECT_BLIND]` or `[Actions.SKIP_BLIND]` |
| `select_cards_from_hand(self, G)` | Select cards to play or discard | `[Actions.PLAY_HAND, [indices]]` |
| `select_shop_action(self, G)` | Choose shop action | `[Actions.BUY_CARD, [index]]` etc. |
| `select_booster_action(self, G)` | Handle booster pack choices | `[Actions.SELECT_BOOSTER_CARD, ...]` |
| `sell_jokers(self, G)` | Decide which jokers to sell | `[Actions.SELL_JOKER, [index]]` |
| `rearrange_jokers(self, G)` | Reorder jokers | `[Actions.REARRANGE_JOKERS, []]` |
| `use_or_sell_consumables(self, G)` | Use tarot/planet cards | `[Actions.USE_CONSUMABLE, []]` |
| `rearrange_consumables(self, G)` | Reorder consumables | `[Actions.REARRANGE_CONSUMABLES, []]` |
| `rearrange_hand(self, G)` | Reorder hand cards | `[Actions.REARRANGE_HAND, []]` |

## Creating Your First Bot

### Step 1: Basic Bot Structure

Create a new Python file for your bot:

```python
# my_first_bot.py
from bot import Bot, Actions

class MyFirstBot(Bot):
    def __init__(self, deck="Red Deck", stake=1):
        super().__init__(deck, stake)
        self.round_count = 0
        
    def skip_or_select_blind(self, G):
        """Always select blinds to play them"""
        return [Actions.SELECT_BLIND]
    
    def select_cards_from_hand(self, G):
        """Simple strategy: play the first card"""
        return [Actions.PLAY_HAND, [1]]
    
    def select_shop_action(self, G):
        """Always leave the shop immediately"""
        return [Actions.END_SHOP]
    
    def select_booster_action(self, G):
        """Skip all booster packs"""
        return [Actions.SKIP_BOOSTER_PACK]
    
    def sell_jokers(self, G):
        """Don't sell any jokers"""
        return [Actions.SELL_JOKER, []]
    
    def rearrange_jokers(self, G):
        """Don't rearrange jokers"""
        return [Actions.REARRANGE_JOKERS, []]
    
    def use_or_sell_consumables(self, G):
        """Don't use consumables"""
        return [Actions.USE_CONSUMABLE, []]
    
    def rearrange_consumables(self, G):
        """Don't rearrange consumables"""
        return [Actions.REARRANGE_CONSUMABLES, []]
    
    def rearrange_hand(self, G):
        """Don't rearrange hand"""
        return [Actions.REARRANGE_HAND, []]

# Run the bot
if __name__ == "__main__":
    bot = MyFirstBot()
    bot.run()
```

### Step 2: Run Your Bot

```bash
# Make sure Balatro is running with the mod enabled
python my_first_bot.py
```

## Understanding Game States

The `G` parameter passed to each method contains the complete game state:

### Game State Structure

```python
def analyze_game_state(self, G):
    # Basic game information
    current_state = G["state"]  # Current game state enum
    waiting_for = G["waitingFor"]  # What decision is needed
    
    # Hand information
    hand_cards = G["hand"]  # List of cards in hand
    for card in hand_cards:
        print(f"Card: {card['name']} ({card['suit']} {card['value']})")
    
    # Jokers
    jokers = G["jokers"]  # Active jokers
    
    # Shop (when in shop)
    if "shop" in G:
        shop_cards = G["shop"]["cards"]
        shop_cost = G["shop"]["reroll_cost"]
    
    # Round information
    round_info = G["current_round"]
    discards_left = round_info["discards_left"]
    
    # Ante information
    blind_name = G["ante"]["blinds"]["ondeck"]  # "Small", "Big", or boss name
```

### Card Properties

Each card in the game state has these properties:

```python
card = {
    "label": "base_card",      # Card type identifier
    "name": "3 of Hearts",     # Display name
    "suit": "Hearts",          # Hearts, Diamonds, Clubs, Spades
    "value": 3,                # Card value (1-13)
    "card_key": "H_3"          # Unique identifier
}
```

## Implementing Bot Methods

### Skip or Select Blind

Decide whether to play or skip the current blind:

```python
def skip_or_select_blind(self, G):
    blind_name = G["ante"]["blinds"]["ondeck"]
    
    # Skip small and big blinds, play boss blinds
    if blind_name in ["Small", "Big"]:
        return [Actions.SKIP_BLIND]
    else:
        return [Actions.SELECT_BLIND]
```

### Select Cards from Hand

Choose which cards to play or discard:

```python
def select_cards_from_hand(self, G):
    hand = G["hand"]
    round_info = G["current_round"]
    
    # Strategy: Look for pairs
    card_values = {}
    for i, card in enumerate(hand):
        value = card["value"]
        if value not in card_values:
            card_values[value] = []
        card_values[value].append(i + 1)  # 1-indexed
    
    # Find pairs
    for value, indices in card_values.items():
        if len(indices) >= 2:
            return [Actions.PLAY_HAND, indices[:2]]
    
    # No pairs found, discard lowest cards
    if round_info["discards_left"] > 0:
        # Sort by value and discard lowest
        sorted_cards = sorted(enumerate(hand), key=lambda x: x[1]["value"])
        discard_indices = [i + 1 for i, _ in sorted_cards[:3]]
        return [Actions.DISCARD_HAND, discard_indices]
    
    # No discards left, play first card
    return [Actions.PLAY_HAND, [1]]
```

### Shop Actions

Make decisions in the shop:

```python
def select_shop_action(self, G):
    shop = G.get("shop", {})
    dollars = G.get("dollars", 0)
    
    if not shop:
        return [Actions.END_SHOP]
    
    # Look for useful jokers
    for i, card in enumerate(shop.get("cards", [])):
        if card["name"] == "Joker" and dollars >= card.get("cost", 0):
            return [Actions.BUY_CARD, [i + 1]]
    
    # Reroll if we have money and nothing good
    reroll_cost = shop.get("reroll_cost", 5)
    if dollars >= reroll_cost * 2:  # Keep some money in reserve
        return [Actions.REROLL_SHOP]
    
    return [Actions.END_SHOP]
```

### Advanced Card Selection

Implement poker hand detection:

```python
def find_best_hand(self, hand):
    """Find the best poker hand from available cards"""
    
    # Group by suit and value
    suits = {}
    values = {}
    
    for i, card in enumerate(hand):
        suit = card["suit"]
        value = card["value"]
        
        if suit not in suits:
            suits[suit] = []
        suits[suit].append((i + 1, value))
        
        if value not in values:
            values[value] = []
        values[value].append(i + 1)
    
    # Check for flush (5+ cards of same suit)
    for suit, cards in suits.items():
        if len(cards) >= 5:
            # Sort by value and take best 5
            cards.sort(key=lambda x: x[1], reverse=True)
            return [Actions.PLAY_HAND, [idx for idx, _ in cards[:5]]]
    
    # Check for four of a kind
    for value, indices in values.items():
        if len(indices) >= 4:
            return [Actions.PLAY_HAND, indices[:4]]
    
    # Check for full house
    three_kind = None
    pair = None
    for value, indices in values.items():
        if len(indices) >= 3 and three_kind is None:
            three_kind = indices[:3]
        elif len(indices) >= 2 and pair is None:
            pair = indices[:2]
    
    if three_kind and pair:
        return [Actions.PLAY_HAND, three_kind + pair]
    
    # Check for straight
    sorted_values = sorted(set(card["value"] for card in hand))
    for i in range(len(sorted_values) - 4):
        if sorted_values[i+4] - sorted_values[i] == 4:
            # Found straight
            straight_cards = []
            for val in sorted_values[i:i+5]:
                for j, card in enumerate(hand):
                    if card["value"] == val and j + 1 not in straight_cards:
                        straight_cards.append(j + 1)
                        break
            return [Actions.PLAY_HAND, straight_cards]
    
    # Check for three of a kind
    if three_kind:
        return [Actions.PLAY_HAND, three_kind]
    
    # Check for pairs
    for value, indices in values.items():
        if len(indices) >= 2:
            return [Actions.PLAY_HAND, indices[:2]]
    
    # High card
    best_card = max(enumerate(hand), key=lambda x: x[1]["value"])
    return [Actions.PLAY_HAND, [best_card[0] + 1]]
```

## Action Reference

### Action Format

All actions follow the format: `[Action, parameters...]`

### Common Actions

```python
# Blind selection
[Actions.SELECT_BLIND]  # Play the blind
[Actions.SKIP_BLIND]    # Skip the blind

# Hand actions
[Actions.PLAY_HAND, [1, 2, 3]]     # Play cards at indices 1, 2, 3
[Actions.DISCARD_HAND, [4, 5]]     # Discard cards at indices 4, 5

# Shop actions
[Actions.BUY_CARD, [1]]           # Buy first shop card
[Actions.BUY_VOUCHER, [1]]        # Buy first voucher
[Actions.BUY_BOOSTER, [1]]        # Buy first booster pack
[Actions.REROLL_SHOP]             # Reroll shop contents
[Actions.END_SHOP]                # Leave shop

# Booster actions
[Actions.SELECT_BOOSTER_CARD, [1], [2, 3]]  # Use card 1 on targets 2, 3
[Actions.SKIP_BOOSTER_PACK]                  # Skip booster pack

# Joker management
[Actions.SELL_JOKER, [2]]         # Sell joker at index 2
[Actions.SELL_JOKER, []]          # Don't sell any jokers

# Card management
[Actions.USE_CONSUMABLE, [1], [2, 3]]  # Use consumable 1 on targets 2, 3
[Actions.SELL_CONSUMABLE, [1]]         # Sell consumable at index 1

# Rearrangement (typically return empty lists)
[Actions.REARRANGE_JOKERS, []]
[Actions.REARRANGE_CONSUMABLES, []]
[Actions.REARRANGE_HAND, []]
```

## Advanced Techniques

### State Persistence

Use the bot's `self.state` dictionary to remember information:

```python
def select_cards_from_hand(self, G):
    # Initialize state tracking
    if "hands_played" not in self.state:
        self.state["hands_played"] = 0
        self.state["strategy"] = "conservative"
    
    self.state["hands_played"] += 1
    
    # Change strategy based on progress
    if self.state["hands_played"] > 10:
        self.state["strategy"] = "aggressive"
    
    # Use strategy in decision making
    if self.state["strategy"] == "aggressive":
        return self.play_aggressively(G)
    else:
        return self.play_conservatively(G)
```

### Multi-Round Planning

```python
def skip_or_select_blind(self, G):
    blind_name = G["ante"]["blinds"]["ondeck"]
    round_num = G.get("round", 1)
    
    # Skip early small blinds to save discards
    if round_num <= 2 and blind_name == "Small":
        return [Actions.SKIP_BLIND]
    
    # Always play boss blinds for rewards
    if blind_name not in ["Small", "Big"]:
        return [Actions.SELECT_BLIND]
    
    # Adaptive strategy based on current strength
    joker_count = len(G.get("jokers", []))
    if joker_count >= 3:  # Strong position
        return [Actions.SELECT_BLIND]
    else:
        return [Actions.SKIP_BLIND]
```

### Error Handling

```python
def select_cards_from_hand(self, G):
    try:
        hand = G.get("hand", [])
        if not hand:
            return [Actions.PLAY_HAND, []]
        
        # Your strategy logic here
        return self.find_best_hand(hand)
        
    except Exception as e:
        print(f"Error in card selection: {e}")
        # Fallback: play first card
        return [Actions.PLAY_HAND, [1]] if G.get("hand") else [Actions.PLAY_HAND, []]
```

## Testing and Debugging

### Debug Output

Add logging to understand bot behavior:

```python
class DebugBot(Bot):
    def select_cards_from_hand(self, G):
        hand = G.get("hand", [])
        print(f"Hand: {[card['name'] for card in hand]}")
        
        action = self.choose_hand_action(G)
        print(f"Chosen action: {action}")
        
        return action
```

### State Caching

Use the provided state caching for analysis:

```python
from gamestates import cache_state

def select_cards_from_hand(self, G):
    # Cache state for later analysis
    cache_state("hand_selection", G)
    
    # Your decision logic
    return [Actions.PLAY_HAND, [1]]
```

### Testing Framework

Create test cases for your bot:

```python
# test_bot.py
def test_blind_selection():
    bot = MyBot("Red Deck")
    
    # Test case: Small blind
    test_state = {"ante": {"blinds": {"ondeck": "Small"}}}
    action = bot.skip_or_select_blind(test_state)
    assert action == [Actions.SKIP_BLIND]
    
    # Test case: Boss blind
    test_state = {"ante": {"blinds": {"ondeck": "The Hook"}}}
    action = bot.skip_or_select_blind(test_state)
    assert action == [Actions.SELECT_BLIND]

if __name__ == "__main__":
    test_blind_selection()
    print("All tests passed!")
```

---

*Ready to create more sophisticated bots? Check out the [Examples](examples.md) for advanced implementations!* 