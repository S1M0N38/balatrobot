# Performance Optimization

Guide to optimizing Balatrobot performance for faster and more efficient bot execution.

## 📋 Table of Contents

- [Overview](#overview)
- [Game Speed Settings](#game-speed-settings)
- [Bot Optimization](#bot-optimization)
- [Network Performance](#network-performance)
- [Memory Management](#memory-management)
- [Profiling](#profiling)
- [Common Performance Issues](#common-performance-issues)
- [Benchmarking](#benchmarking)

## Overview

Performance optimization in Balatrobot involves several components:

- **Game Speed**: Configuring Balatro's internal speed settings
- **Bot Logic**: Optimizing decision-making algorithms
- **Network**: Minimizing UDP communication overhead
- **Memory**: Efficient use of game state data

## Game Speed Settings

### Speed Factor Configuration
Adjust the speed multiplier in `config.lua`:

```lua
return {
    speed_factor = 10,  -- 10x faster than normal
    -- Other settings...
}
```

**Recommended Settings:**
- **Development**: `speed_factor = 3-5` (easier to debug)
- **Production**: `speed_factor = 10-20` (maximum speed)
- **Very Fast**: `speed_factor = 50+` (use with caution)

### Animation Skipping
Disable unnecessary animations:

```lua
-- In Lua configuration
return {
    skip_animations = true,
    fast_mode = true,
    auto_skip_non_essential = true
}
```

### Frame Rate Optimization
Configure optimal frame rates:

```lua
-- Target 60 FPS for smooth operation
G.SETTINGS.GRAPHICS.fps_target = 60

-- Reduce for maximum speed (may cause instability)
G.SETTINGS.GRAPHICS.fps_target = 120
```

## Bot Optimization

### Efficient Decision Making
Minimize computation in bot methods:

```python
class OptimizedBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-calculate constants
        self.CARD_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.RANK_VALUES = {rank: i for i, rank in enumerate(self.CARD_RANKS)}
    
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
        self._shop_cache = {}
    
    def _analyze_hand(self, hand):
        # Create cache key from hand
        hand_key = tuple(sorted([(c["rank"], c["suit"]) for c in hand]))
        
        if hand_key not in self._hand_cache:
            # Expensive analysis only when needed
            self._hand_cache[hand_key] = self._compute_hand_value(hand)
        
        return self._hand_cache[hand_key]
```

### Avoid Redundant Processing
Skip unnecessary work:

```python
def select_shop_action(self, G):
    money = G["player"]["money"]
    
    # Quick exit for no money
    if money < 5:
        return [Actions.END_SHOP]
    
    # Only analyze if we have reasonable money
    if money >= 20:
        return self._full_shop_analysis(G)
    
    # Simple logic for medium money
    return self._simple_shop_logic(G)
```

## Network Performance

### UDP Optimization
Minimize network overhead:

```python
class NetworkOptimizedBot(Bot):
    def sendcmd(self, cmd, **kwargs):
        # Compress commands when possible
        if len(cmd) > 100:
            cmd = self._compress_command(cmd)
        super().sendcmd(cmd, **kwargs)
    
    def _compress_command(self, cmd):
        # Simple compression for repeated commands
        return cmd.replace("play_hand", "ph").replace("buy_card", "bc")
```

### Batching Commands
Send multiple commands together when possible:

```python
def batch_actions(self, actions):
    # Combine multiple actions into single network call
    batch_cmd = ";".join(actions)
    self.sendcmd(batch_cmd)
```

### Connection Pooling
Reuse network connections:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Keep socket alive
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

## Memory Management

### Efficient Game State Handling
Avoid copying large game state objects:

```python
def select_cards_from_hand(self, G):
    # Access directly instead of copying
    hand_size = len(G["hand"])
    player_money = G["player"]["money"]
    
    # Don't do: hand_copy = G["hand"].copy()
    # Do: work with references when possible
```

### Cleanup Strategies
Clear caches periodically:

```python
def cleanup_caches(self):
    # Clear caches every 100 rounds
    if self.state.get('rounds_played', 0) % 100 == 0:
        self._hand_cache.clear()
        self._shop_cache.clear()
```

### Memory Monitoring
Track memory usage:

```python
import psutil
import os

def monitor_memory(self):
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    if memory_mb > 500:  # 500MB threshold
        print(f"High memory usage: {memory_mb:.1f}MB")
        self.cleanup_caches()
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
    bot.run()
    
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
    
    # Your bot logic here
    result = self._complex_decision(G)
    
    elapsed = time.time() - start_time
    if elapsed > 0.1:  # Log slow methods
        print(f"Slow method: {elapsed:.3f}s")
    
    return result
```

### Memory Profiling
Track memory usage patterns:

```python
from memory_profiler import profile

@profile
def memory_intensive_method(self, G):
    # This will show line-by-line memory usage
    large_calculation = self._analyze_all_possibilities(G)
    return large_calculation
```

## Common Performance Issues

### 1. Slow Game State Access
**Problem**: Repeatedly accessing nested dictionary values
```python
# Slow
for i in range(100):
    money = G["player"]["stats"]["current"]["money"]
```

**Solution**: Cache frequently accessed values
```python
# Fast
money = G["player"]["stats"]["current"]["money"]
for i in range(100):
    # Use cached 'money' value
```

### 2. Inefficient String Operations
**Problem**: Building commands with string concatenation
```python
# Slow
cmd = ""
for card in cards:
    cmd += str(card) + ","
```

**Solution**: Use join() or f-strings
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
        # ... later in same method
        if self._calculate_hand_value(G["hand"]) > 200:
```

**Solution**: Calculate once, store result
```python
# Fast
def select_cards_from_hand(self, G):
    hand_value = self._calculate_hand_value(G["hand"])
    if hand_value > 100:
        # ... later in same method
        if hand_value > 200:
```

### 4. Large Object Creation
**Problem**: Creating large temporary objects
```python
# Memory intensive
all_possibilities = self._generate_all_combinations(G)
best = max(all_possibilities, key=lambda x: x.score)
```

**Solution**: Use generators or iterative approaches
```python
# Memory efficient
best_score = 0
best_action = None
for possibility in self._generate_combinations_iter(G):
    if possibility.score > best_score:
        best_score = possibility.score
        best_action = possibility
```

## Benchmarking

### Performance Testing
Create standardized benchmarks:

```python
def benchmark_bot(bot_class, rounds=100):
    start_time = time.time()
    
    bot = bot_class(deck="Red Deck", stake=1)
    
    # Simulate game rounds
    for _ in range(rounds):
        mock_G = create_mock_game_state()
        bot.select_cards_from_hand(mock_G)
        bot.select_shop_action(mock_G)
    
    elapsed = time.time() - start_time
    print(f"Bot completed {rounds} rounds in {elapsed:.2f}s")
    print(f"Average: {elapsed/rounds*1000:.1f}ms per round")
```

### Speed Comparisons
Compare different optimization approaches:

```python
def compare_implementations():
    bots = [
        ("Basic Bot", BasicBot),
        ("Optimized Bot", OptimizedBot),
        ("Cached Bot", CachedBot)
    ]
    
    for name, bot_class in bots:
        print(f"Testing {name}:")
        benchmark_bot(bot_class, rounds=1000)
        print()
```

### Real-World Testing
Test with actual game instances:

```python
def real_world_benchmark():
    bot = OptimizedBot(deck="Red Deck", stake=1)
    
    start_time = time.time()
    bot.run()  # Play complete game
    
    total_time = time.time() - start_time
    print(f"Complete game: {total_time:.1f}s")
```

---

*For more optimization techniques, see [Best Practices](best-practices.md) and [Configuration](configuration.md).* 