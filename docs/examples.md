# Examples

Working examples of bots included with Balatrobot.

## Basic Example Bot (`bot_example.py`)

Simple bot demonstrating basic functionality:

- **Blind Strategy**: Skip small/big blinds, play boss blinds
- **Hand Strategy**: Use state tracking to discard first, then play specific cards
- **Shop Strategy**: Buy cards on specific shop visits

Key concepts:
- State persistence with `self.state`
- Progressive decision making
- Basic resource management

## Flush Bot (`flush_bot.py`)

More advanced bot with poker strategy:

- **Strategy**: Build and play flush hands (5+ cards of same suit)
- **Implementation**: Count suits, identify dominant suit, discard off-suit cards
- **Fallback**: Play suboptimal hands when forced by game constraints

Key features:
- Class-based implementation
- Sophisticated card analysis
- Multi-instance benchmarking
def play_flushes(self, G):
    # Count cards by suit
    suit_count = {
        "Hearts": 0,
        "Diamonds": 0,
        "Clubs": 0,
        "Spades": 0,
    }
    for card in G["hand"]:
        suit_count[card["suit"]] += 1

    # Find most common suit
    most_common_suit = max(suit_count, key=suit_count.get)
    most_common_suit_count = suit_count[most_common_suit]
    
    # Play flush if we have 5+ cards of same suit
    if most_common_suit_count >= 5:
        flush_cards = []
        for card in G["hand"]:
            if card["suit"] == most_common_suit:
                flush_cards.append(card)
        
        # Sort by value (highest first) and play best 5
        flush_cards.sort(key=lambda x: x["value"], reverse=True)
        return [
            Actions.PLAY_HAND,
            [G["hand"].index(card) + 1 for card in flush_cards[:5]],
        ]
```

**Key Insights:**
- **Suit Counting**: Efficiently identifies the dominant suit
- **Card Selection**: Plays the highest-value cards within the flush
- **Index Mapping**: Correctly maps card objects back to hand indices

#### Strategic Discarding
```python
# We don't have a flush, so discard cards not of the most common suit
discards = []
for card in G["hand"]:
    if card["suit"] != most_common_suit:
        discards.append(card)

discards.sort(key=lambda x: x["value"], reverse=True)
discards = discards[:5]  # Limit to 5 cards

if len(discards) > 0:
    if G["current_round"]["discards_left"] > 0:
        action = Actions.DISCARD_HAND
    else:
        action = Actions.PLAY_HAND  # Must play if no discards left
    return [action, [G["hand"].index(card) + 1 for card in discards]]
```

**Strategic Elements:**
- **Focused Discarding**: Only removes cards that don't contribute to the primary strategy
- **Resource Management**: Checks available discards before attempting to discard
- **Adaptive Play**: Plays suboptimal hands when forced to by game constraints

#### Performance Monitoring
```python
def benchmark_multi_instance():
    target_t = 50 * bot_count
    start_time = time.time()
    
    while t < target_t:
        for bot in bots:
            bot.run_step()
    
    end_time = time.time()
    t_per_sec = target_t / (end_time - start_time)
    print(f"Bot count: {bot_count}, t/sec: {t_per_sec}")
```

The FlushBot includes benchmarking code to measure performance across multiple instances, demonstrating scalability testing.

### Class-Based Implementation
```python
class FlushBot(Bot):
    def skip_or_select_blind(self, G):
        cache_state("skip_or_select_blind", G)
        return [Actions.SELECT_BLIND]

    def select_cards_from_hand(self, G):
        return self.play_flushes(G)
    
    # ... other methods
```

**Advantages of Class-Based Approach:**
- **Encapsulation**: Strategy logic contained within the class
- **State Management**: Easy access to instance variables
- **Reusability**: Can be extended or modified easily
- **Testing**: Simpler to unit test individual methods

## Strategy Patterns

### Pattern 1: Conservative Early Game

```python
def conservative_early_strategy(self, G):
    """Skip early blinds to build resources"""
    round_num = G.get("round", 1)
    blind_name = G["ante"]["blinds"]["ondeck"]
    
    if round_num <= 3:
        if blind_name in ["Small", "Big"]:
            return [Actions.SKIP_BLIND]
    
    return [Actions.SELECT_BLIND]
```

### Pattern 2: Adaptive Shopping

```python
def adaptive_shop_strategy(self, G):
    """Shop based on current needs and resources"""
    dollars = G.get("dollars", 0)
    joker_count = len(G.get("jokers", []))
    shop = G.get("shop", {})
    
    # Prioritize jokers if we have few
    if joker_count < 2 and dollars >= 50:
        for i, card in enumerate(shop.get("cards", [])):
            if "joker" in card["name"].lower():
                return [Actions.BUY_CARD, [i + 1]]
    
    # Reroll if we have excess money
    if dollars >= 100:
        return [Actions.REROLL_SHOP]
    
    return [Actions.END_SHOP]
```

### Pattern 3: Hand Strength Evaluation

```python
def evaluate_hand_strength(self, hand):
    """Rate the strength of current hand"""
    suits = {}
    values = {}
    
    for card in hand:
        suits.setdefault(card["suit"], 0)
        suits[card["suit"]] += 1
        values.setdefault(card["value"], 0)
        values[card["value"]] += 1
    
    # Scoring system
    score = 0
    
    # Flush potential
    max_suit_count = max(suits.values())
    if max_suit_count >= 5:
        score += 100
    elif max_suit_count >= 3:
        score += 20
    
    # Pair potential
    max_value_count = max(values.values())
    if max_value_count >= 4:
        score += 80
    elif max_value_count >= 3:
        score += 40
    elif max_value_count >= 2:
        score += 20
    
    return score
```

## Custom Bot Examples

### High-Card Bot

Focus on playing high-value single cards:

```python
class HighCardBot(Bot):
    def select_cards_from_hand(self, G):
        hand = G.get("hand", [])
        if not hand:
            return [Actions.PLAY_HAND, []]
        
        # Find highest value card
        best_card_idx = 0
        best_value = 0
        
        for i, card in enumerate(hand):
            if card["value"] > best_value:
                best_value = card["value"]
                best_card_idx = i
        
        return [Actions.PLAY_HAND, [best_card_idx + 1]]
    
    def skip_or_select_blind(self, G):
        # Only play if we have high cards
        hand = G.get("hand", [])
        high_cards = [card for card in hand if card["value"] >= 10]
        
        if len(high_cards) >= 3:
            return [Actions.SELECT_BLIND]
        else:
            return [Actions.SKIP_BLIND]
```

### Pair-Hunting Bot

Specialized in finding and playing pairs:

```python
class PairBot(Bot):
    def find_pairs(self, hand):
        """Find all pairs in hand"""
        value_indices = {}
        for i, card in enumerate(hand):
            value = card["value"]
            if value not in value_indices:
                value_indices[value] = []
            value_indices[value].append(i + 1)
        
        pairs = []
        for value, indices in value_indices.items():
            if len(indices) >= 2:
                pairs.append((value, indices[:2]))
        
        return pairs
    
    def select_cards_from_hand(self, G):
        hand = G.get("hand", [])
        pairs = self.find_pairs(hand)
        
        if pairs:
            # Play highest value pair
            highest_pair = max(pairs, key=lambda x: x[0])
            return [Actions.PLAY_HAND, highest_pair[1]]
        
        # No pairs, discard lowest cards
        if G["current_round"]["discards_left"] > 0:
            sorted_cards = sorted(enumerate(hand), key=lambda x: x[1]["value"])
            discard_indices = [i + 1 for i, _ in sorted_cards[:3]]
            return [Actions.DISCARD_HAND, discard_indices]
        
        # Must play something
        return [Actions.PLAY_HAND, [1]]
```

### Economic Bot

Focus on shop optimization and resource management:

```python
class EconomicBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state["spending_strategy"] = "conservative"
        self.state["target_jokers"] = 3
    
    def select_shop_action(self, G):
        dollars = G.get("dollars", 0)
        jokers = G.get("jokers", [])
        shop = G.get("shop", {})
        
        # Calculate value of purchases
        best_purchase = None
        best_value = 0
        
        for i, card in enumerate(shop.get("cards", [])):
            cost = card.get("cost", 999)
            if cost <= dollars:
                value = self.evaluate_card_value(card, jokers)
                if value > best_value:
                    best_value = value
                    best_purchase = i + 1
        
        # Buy if value exceeds threshold
        if best_purchase and best_value >= 50:
            return [Actions.BUY_CARD, [best_purchase]]
        
        # Reroll if we have excess money and poor options
        reroll_cost = shop.get("reroll_cost", 5)
        if dollars >= reroll_cost * 3 and best_value < 25:
            return [Actions.REROLL_SHOP]
        
        return [Actions.END_SHOP]
    
    def evaluate_card_value(self, card, current_jokers):
        """Evaluate the value of a potential purchase"""
        base_value = 30  # Base joker value
        
        # Bonus for first jokers
        if len(current_jokers) < 2:
            base_value += 20
        
        # Penalty for too many jokers
        if len(current_jokers) >= 4:
            base_value -= 10
        
        return base_value
```

## Performance Considerations

### Efficient Decision Making

```python
def optimized_hand_analysis(self, hand):
    """Fast hand analysis with minimal iterations"""
    if not hand:
        return {"type": "empty", "cards": []}
    
    # Single pass analysis
    suits = [0, 0, 0, 0]  # Hearts, Diamonds, Clubs, Spades
    values = [0] * 14     # Index 0 unused, 1-13 for card values
    suit_map = {"Hearts": 0, "Diamonds": 1, "Clubs": 2, "Spades": 3}
    
    for card in hand:
        suits[suit_map[card["suit"]]] += 1
        values[card["value"]] += 1
    
    # Quick checks
    max_suit = max(suits)
    max_value = max(values)
    
    if max_suit >= 5:
        return {"type": "flush", "strength": max_suit}
    elif max_value >= 4:
        return {"type": "four_kind", "strength": max_value}
    elif max_value >= 2:
        return {"type": "pair", "strength": max_value}
    else:
        return {"type": "high_card", "strength": max(card["value"] for card in hand)}
```

### Memory Management

```python
def cleanup_old_state(self):
    """Remove old state data to prevent memory leaks"""
    current_round = self.G.get("round", 1)
    
    # Remove state data older than 5 rounds
    keys_to_remove = []
    for key in self.state:
        if key.startswith("round_") and int(key.split("_")[1]) < current_round - 5:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del self.state[key]
```

### Batch Operations

```python
def analyze_multiple_hands(self, possible_plays):
    """Analyze multiple potential plays efficiently"""
    results = []
    
    for play in possible_plays:
        # Quick evaluation without deep analysis
        score = sum(card["value"] for card in play["cards"])
        results.append({"play": play, "score": score})
    
    # Sort and return best options
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:3]  # Top 3 options
```

---

*These examples demonstrate various approaches to bot development. Experiment with different strategies to find what works best for your goals!* 