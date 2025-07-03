# Best Practices

Guidelines and best practices for developing effective Balatrobot bots.

## General Principles

### 1. Keep It Simple
Start with simple logic and gradually add complexity. A working simple bot is better than a broken complex one.

```python
# Good: Simple, clear logic
def skip_or_select_blind(self, G):
    return [Actions.SELECT_BLIND]

# Avoid: Overly complex from the start
def skip_or_select_blind(self, G):
    # 50 lines of complex probability calculations...
```

### 2. Fail Gracefully
Always provide fallback actions to prevent crashes.

```python
def select_cards_from_hand(self, G):
    try:
        # Complex card selection logic
        return self.advanced_card_selection(G)
    except:
        # Fallback: play first card
        return [Actions.PLAY_HAND, [1]]
```

### 3. State Management
Use the bot's persistent state dictionary for tracking information across rounds.

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.state = {
        'rounds_played': 0,
        'money_targets': {},
        'joker_priorities': []
    }
```

## Code Organization

### Method Structure
Organize bot methods with clear separation of concerns:

```python
class MyBot(Bot):
    def skip_or_select_blind(self, G):
        blind_info = self._analyze_blind(G)
        return self._make_blind_decision(blind_info)
    
    def _analyze_blind(self, G):
        # Helper method for analysis
        pass
    
    def _make_blind_decision(self, blind_info):
        # Helper method for decision making
        pass
```

### Configuration
Use class attributes for bot configuration:

```python
class MyBot(Bot):
    # Configuration
    MIN_MONEY_RESERVE = 10
    PREFERRED_JOKERS = ["Joker", "Greedy Joker", "Lusty Joker"]
    DISCARD_THRESHOLD = 3
    
    def select_shop_action(self, G):
        if G["player"]["money"] < self.MIN_MONEY_RESERVE:
            return [Actions.END_SHOP]
```

## Decision Making

### Prioritize Actions
Create clear priority systems for decisions:

```python
def select_shop_action(self, G):
    money = G["player"]["money"]
    
    # Priority 1: Buy essential jokers
    joker_action = self._buy_priority_joker(G)
    if joker_action:
        return joker_action
    
    # Priority 2: Buy vouchers if affordable
    voucher_action = self._buy_affordable_voucher(G)
    if voucher_action:
        return voucher_action
    
    # Priority 3: Reroll if money allows
    if money > 15:
        return [Actions.REROLL_SHOP]
    
    return [Actions.END_SHOP]
```

### Context-Aware Decisions
Consider game context in all decisions:

```python
def select_cards_from_hand(self, G):
    discards_remaining = G["round"]["discards_left"]
    hands_remaining = G["round"]["hands_left"]
    score_needed = G["blind"]["requirement"] - G["round"]["current_score"]
    
    if score_needed <= 0:
        # Already won, play safe
        return [Actions.PLAY_HAND, [1]]
    elif hands_remaining == 1:
        # Last hand, play best possible
        return self._play_best_hand(G)
    elif discards_remaining > 0:
        # Can afford to discard
        return self._discard_weak_cards(G)
```

## Performance

### Efficient Game State Access
Cache frequently accessed data:

```python
def select_cards_from_hand(self, G):
    # Cache commonly used values
    hand = G["hand"]
    money = G["player"]["money"]
    jokers = G["jokers"]
    
    # Use cached values throughout method
    return self._evaluate_hand(hand, jokers, money)
```

### Avoid Unnecessary Calculations
Don't recalculate the same values:

```python
# Good: Calculate once, use multiple times
def analyze_hand(self, hand):
    ranks = [card["rank"] for card in hand]
    suits = [card["suit"] for card in hand]
    
    has_pair = len(set(ranks)) < len(ranks)
    has_flush = len(set(suits)) == 1
    
    return {
        'has_pair': has_pair,
        'has_flush': has_flush,
        'ranks': ranks,
        'suits': suits
    }

# Avoid: Recalculating repeatedly
def bad_analysis(self, hand):
    if len(set([card["rank"] for card in hand])) < len(hand):
        # ... later in same method
        if len(set([card["rank"] for card in hand])) < len(hand):
```

## Debugging

### Logging Strategy
Use structured logging for debugging:

```python
def select_shop_action(self, G):
    money = G["player"]["money"]
    shop_cards = G["shop"]["cards"]
    
    print(f"Shop Decision - Money: {money}")
    for i, card in enumerate(shop_cards):
        print(f"  Card {i+1}: {card['name']} - ${card['price']}")
    
    action = self._make_shop_decision(G)
    print(f"Decision: {action}")
    return action
```

### State Tracking
Track important bot state changes:

```python
def select_cards_from_hand(self, G):
    self.state['rounds_played'] += 1
    
    if self.state['rounds_played'] % 10 == 0:
        print(f"Rounds played: {self.state['rounds_played']}")
        print(f"Current money: {G['player']['money']}")
```

## Testing

### Test Individual Methods
Create test cases for bot methods:

```python
def test_blind_decision(self):
    # Create mock game state
    test_G = {
        "ante": {"blinds": {"ondeck": "Big Blind"}},
        "player": {"money": 50}
    }
    
    action = self.skip_or_select_blind(test_G)
    assert action == [Actions.SELECT_BLIND]
```

### Gradual Testing
Test with simple scenarios first:

```python
# Start with basic deck, low stakes
test_bot = MyBot(deck="Red Deck", stake=1)

# Gradually increase complexity
production_bot = MyBot(deck="Plasma Deck", stake=5)
```

## Common Patterns

### Safe Indexing
Always check array bounds:

```python
def get_first_card(self, hand):
    if len(hand) > 0:
        return hand[0]
    return None

def play_cards_safely(self, indices, hand_size):
    safe_indices = [i for i in indices if 1 <= i <= hand_size]
    return [Actions.PLAY_HAND, safe_indices]
```

### Conditional Logic Patterns
Use guard clauses for cleaner code:

```python
def select_shop_action(self, G):
    # Guard clauses
    if G["player"]["money"] < 5:
        return [Actions.END_SHOP]
    
    if not G["shop"]["cards"]:
        return [Actions.END_SHOP]
    
    # Main logic here
    return self._evaluate_shop_options(G)
```

### Resource Management
Track and manage game resources:

```python
def should_reroll_shop(self, G):
    money = G["player"]["money"]
    reroll_cost = G["shop"]["reroll_cost"]
    rounds_remaining = self._estimate_rounds_remaining(G)
    
    # Only reroll if we can afford it and have rounds left
    return money > reroll_cost * 2 and rounds_remaining > 3
```

## Pitfalls to Avoid

### 1. Index Errors
Remember 1-based indexing for actions:

```python
# Wrong: 0-based indexing
return [Actions.PLAY_HAND, [0, 1]]

# Correct: 1-based indexing
return [Actions.PLAY_HAND, [1, 2]]
```

### 2. Empty Action Lists
Always provide valid parameters:

```python
# Wrong: Empty when action expects parameters
return [Actions.PLAY_HAND, []]

# Correct: Provide at least one card
return [Actions.PLAY_HAND, [1]]
```

### 3. State Mutation
Don't modify the game state object:

```python
# Wrong: Modifying G
def bad_method(self, G):
    G["player"]["money"] += 100  # Don't do this!

# Correct: Read-only access
def good_method(self, G):
    money = G["player"]["money"]  # Read only
```

### 4. Overcomplication
Avoid premature optimization:

```python
# Good: Start simple
def select_cards_from_hand(self, G):
    return [Actions.PLAY_HAND, [1, 2]]

# Avoid: Overengineering early
def select_cards_from_hand(self, G):
    # 200 lines of machine learning code...
```

### 5. Ignoring Game Context
Consider all relevant game state:

```python
# Wrong: Ignoring context
def select_shop_action(self, G):
    return [Actions.BUY_CARD, [1]]  # Always buy first card

# Right: Context-aware
def select_shop_action(self, G):
    if self._need_money(G):
        return [Actions.END_SHOP]
    if self._good_deal_available(G):
        return [Actions.BUY_CARD, [1]]
    return [Actions.REROLL_SHOP]
```

---

*For more examples and implementation details, see [Examples](examples.md) and [Bot Development Guide](bot-development.md).* 