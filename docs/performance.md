# Performance Optimization

Guide to optimizing Balatrobot performance for faster and more efficient bot execution.

## Overview

Performance optimization in Balatrobot involves:

- **Game Speed**: Configuring Balatro's internal speed settings  
- **Bot Logic**: Optimizing decision-making algorithms
- **Network**: Minimizing UDP communication overhead
- **Memory**: Efficient use of game state data

## Game Speed Settings

### Configuration Options
Adjust performance settings in `config.lua`:

```lua
BALATRO_BOT_CONFIG = {
    enabled = true,
    port = '12345',
    dt = 4.0/60.0,                          -- Lower = faster (default: 8.0/60.0)
    uncap_fps = true,                       -- Remove FPS limitations
    instant_move = true,                    -- Skip movement animations  
    disable_vsync = true,                   -- Disable vertical sync
    disable_card_eval_status_text = true,   -- Hide score popups
    frame_ratio = 200,                      -- Higher = less rendering
}
```

**Recommended Settings:**
- **Development**: `dt = 8.0/60.0, frame_ratio = 10` (visible for debugging)
- **Production**: `dt = 4.0/60.0, frame_ratio = 100` (balanced performance)
- **Maximum Speed**: `dt = 2.0/60.0, frame_ratio = 200` (fastest, may be unstable)

## Bot Optimization

### Efficient Decision Making
Minimize computation in bot methods:

```python
class OptimizedBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-calculate constants
        self.SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    
    def select_cards_from_hand(self, G):
        # Fast lookup instead of complex calculations
        hand = G["hand"]
        if len(hand) >= 2:
            return [Actions.PLAY_HAND, [1, 2]]
        return [Actions.PLAY_HAND, [1]]
```

### Caching Strategies
Cache expensive calculations:

```python
class CachedBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hand_cache = {}
    
    def _analyze_hand(self, hand):
        # Create cache key from hand
        hand_key = tuple(sorted([(c["value"], c["suit"]) for c in hand]))
        
        if hand_key not in self._hand_cache:
            self._hand_cache[hand_key] = self._compute_hand_value(hand)
        
        return self._hand_cache[hand_key]
```

### Avoid Redundant Processing
Skip unnecessary work:

```python
def select_shop_action(self, G):
    dollars = G.get("dollars", 0)
    
    # Quick exit for no money
    if dollars < 5:
        return [Actions.END_SHOP]
    
    # Only analyze if we have reasonable money
    if dollars >= 20:
        return self._full_shop_analysis(G)
    
    return [Actions.END_SHOP]
```

## Memory Management

### Efficient Game State Handling
Avoid copying large game state objects:

```python
def select_cards_from_hand(self, G):
    # Access directly instead of copying
    hand_size = len(G["hand"])
    dollars = G.get("dollars", 0)
    
    # Don't do: hand_copy = G["hand"].copy()
    # Work with references when possible
```

### Cleanup Strategies
Clear caches periodically:

```python
def cleanup_caches(self):
    # Clear caches every 100 actions
    if len(self._hand_cache) > 1000:
        self._hand_cache.clear()
```

## Profiling

### Python Profiling
Use cProfile to identify bottlenecks:

```python
import cProfile
import pstats

def profile_bot():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run bot for a few rounds
    bot = MyBot(deck="Red Deck", stake=1)
    for _ in range(100):
        mock_G = {"hand": [], "dollars": 10}
        bot.select_cards_from_hand(mock_G)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(20)
```

### Timing Critical Sections
Measure method performance:

```python
import time

def timed_method(self, G):
    start_time = time.time()
    
    result = self._complex_decision(G)
    
    elapsed = time.time() - start_time
    if elapsed > 0.1:  # Log slow methods
        print(f"Slow method: {elapsed:.3f}s")
    
    return result
```

## Common Performance Issues

### 1. Slow Game State Access
**Problem**: Repeatedly accessing nested values
```python
# Slow
for i in range(100):
    blind = G["ante"]["blinds"]["ondeck"]
```

**Solution**: Cache frequently accessed values
```python
# Fast
blind = G["ante"]["blinds"]["ondeck"]
for i in range(100):
    # Use cached 'blind' value
```

### 2. Inefficient String Operations
**Problem**: Building commands with string concatenation
```python
# Slow
cmd = ""
for card in cards:
    cmd += str(card) + ","
```

**Solution**: Use join()
```python
# Fast
cmd = ",".join(str(card) for card in cards)
```

### 3. Unnecessary Calculations
**Problem**: Recalculating the same values
```python
# Slow
def select_cards_from_hand(self, G):
    if self._calculate_hand_value(G["hand"]) > 100:
        if self._calculate_hand_value(G["hand"]) > 200:
            # ...
```

**Solution**: Calculate once, store result
```python
# Fast
def select_cards_from_hand(self, G):
    hand_value = self._calculate_hand_value(G["hand"])
    if hand_value > 100:
        if hand_value > 200:
            # ...
```

## Benchmarking

### Performance Testing
Create standardized benchmarks:

```python
def benchmark_bot(bot_class, iterations=1000):
    start_time = time.time()
    
    bot = bot_class(deck="Red Deck", stake=1)
    
    # Simulate decisions
    mock_G = {
        "hand": [{"suit": "Hearts", "value": 10, "name": "10 of Hearts"}],
        "dollars": 50,
        "ante": {"blinds": {"ondeck": "Small"}}
    }
    
    for _ in range(iterations):
        bot.select_cards_from_hand(mock_G)
        bot.select_shop_action(mock_G)
    
    elapsed = time.time() - start_time
    print(f"Bot completed {iterations} decisions in {elapsed:.2f}s")
    print(f"Average: {elapsed/iterations*1000:.1f}ms per decision")
```

---

*For more optimization techniques, see [Best Practices](best-practices.md) and [Configuration](configuration.md).* 