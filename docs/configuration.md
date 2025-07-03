# Configuration Guide

Complete guide to configuring Balatrobot for optimal performance and functionality.

## Configuration File Overview

The main configuration is stored in `config.lua` in the mod directory. This file controls all aspects of the Balatrobot mod behavior.

### Default Configuration

```lua
BALATRO_BOT_CONFIG = {
    enabled = true,                           -- Master enable/disable switch
    port = '12345',                          -- UDP port for communication
    dt = 8.0/60.0,                          -- Game update speed multiplier
    uncap_fps = true,                       -- Remove FPS limitations
    instant_move = true,                    -- Disable movement animations
    disable_vsync = true,                   -- Disable vertical sync
    disable_card_eval_status_text = true,   -- Hide card scoring text
    frame_ratio = 100,                      -- Render frequency (1 = every frame)
}
```

## Core Settings

### enabled

**Type:** `boolean`  
**Default:** `true`  
**Description:** Master switch for all mod functionality.

```lua
enabled = true   -- Mod is active
enabled = false  -- Mod is completely disabled
```

**Usage:**
- Set to `false` to temporarily disable the mod without uninstalling
- Useful for playing the game normally without bot interference

### port

**Type:** `string`  
**Default:** `'12345'`  
**Description:** UDP port for bot communication.

```lua
port = '12345'   -- Default port
port = '12346'   -- Alternative port to avoid conflicts
```

**Important Notes:**
- Must match the port in your Python bot configuration
- Change if multiple bot instances are running simultaneously
- Can be overridden by command line argument when launching Balatro

**Port Selection Guidelines:**
- Use ports 12345-12355 for standard single-bot usage
- For multiple instances, increment by 1 for each instance
- Avoid system ports (1-1024) and common application ports

## Performance Optimization

### dt (Delta Time)

**Type:** `number`  
**Default:** `8.0/60.0` (~0.133)  
**Description:** Game update interval in seconds. Lower values = faster game.

```lua
dt = 8.0/60.0    -- Default: ~7.5 FPS equivalent
dt = 4.0/60.0    -- Faster: ~15 FPS equivalent
dt = 16.0/60.0   -- Slower: ~3.75 FPS equivalent
dt = 1.0/60.0    -- Maximum speed: ~60 FPS equivalent
```

**Performance Impact:**
- **Lower values**: Faster game execution, higher CPU usage
- **Higher values**: Slower execution, more visible for debugging
- **Recommended range**: 4.0/60.0 to 16.0/60.0 for stability

**Stability Considerations:**
- Values below 4.0/60.0 may cause game instability
- Very low values can overwhelm the networking stack
- Test thoroughly when using extreme values

### uncap_fps

**Type:** `boolean`  
**Default:** `true`  
**Description:** Remove FPS limitations for maximum speed.

```lua
uncap_fps = true   -- Remove FPS cap (recommended for bots)
uncap_fps = false  -- Keep normal FPS limits
```

**Effects:**
- `true`: Game runs as fast as possible, better for bot performance
- `false`: Game respects normal FPS limits, more stable visually

### frame_ratio

**Type:** `integer`  
**Default:** `100`  
**Description:** Render every Nth frame. Higher values = less rendering.

```lua
frame_ratio = 1    -- Render every frame (full visual)
frame_ratio = 10   -- Render every 10th frame
frame_ratio = 100  -- Render every 100th frame (minimal visual)
frame_ratio = 200  -- Render every 200th frame (fastest)
```

**Performance vs Visual Quality:**

| Value | Rendering | Performance | Use Case |
|-------|-----------|-------------|----------|
| 1 | Full visual | Slowest | Debugging, demonstrations |
| 10 | Reduced visual | Moderate | Development testing |
| 100 | Minimal visual | Fast | Production bots |
| 200+ | Almost no visual | Fastest | Benchmark/batch runs |

## Visual Settings

### instant_move

**Type:** `boolean`  
**Default:** `true`  
**Description:** Skip movement animations for instant card positioning.

```lua
instant_move = true   -- Cards move instantly (faster)
instant_move = false  -- Cards use smooth animations (slower)
```

**Impact:**
- `true`: Significant performance improvement, no smooth movements
- `false`: Normal game animations, slower but more visually appealing

### disable_vsync

**Type:** `boolean`  
**Default:** `true`  
**Description:** Disable vertical synchronization.

```lua
disable_vsync = true   -- Disable VSync (faster, may cause tearing)
disable_vsync = false  -- Enable VSync (smoother, frame-rate limited)
```

**Considerations:**
- `true`: Better performance, possible screen tearing
- `false`: Smoother visuals, frame rate limited to monitor refresh

### disable_card_eval_status_text

**Type:** `boolean`  
**Default:** `true`  
**Description:** Hide floating text when cards are scored ("+10", etc.).

```lua
disable_card_eval_status_text = true   -- Hide score text (faster)
disable_card_eval_status_text = false  -- Show score text (slower)
```

**Performance Impact:**
- Disabling this text provides a small but measurable performance improvement
- Recommended to keep `true` for production bots

## Network Configuration

### Command Line Port Override

The port can be overridden when launching Balatro:

```bash
# Windows
Balatro.exe 12346

# Launch with specific port
steam://rungameid/2379780//12346
```

### Multi-Instance Setup

For running multiple bot instances:

**Instance 1 (config.lua):**
```lua
port = '12345'
```

**Instance 2 (config.lua):**
```lua
port = '12346'
```

**Instance 3 (config.lua):**
```lua
port = '12347'
```

**Python Bot Configuration:**
```python
# Bot 1
bot1 = Bot(deck="Red Deck", stake=1, bot_port=12345)

# Bot 2  
bot2 = Bot(deck="Blue Deck", stake=1, bot_port=12346)

# Bot 3
bot3 = Bot(deck="Yellow Deck", stake=1, bot_port=12347)
```

## Bot-Specific Settings

### Python Bot Constructor Options

```python
Bot(deck, stake=1, seed=None, challenge=None, bot_port=12346)
```

#### deck

**Type:** `str`  
**Required:** Yes  
**Description:** Deck name to use for the run.

**Valid Deck Names:**
- `"Red Deck"` - Standard balanced deck
- `"Blue Deck"` - Extra hand each round
- `"Yellow Deck"` - Start with extra money
- `"Green Deck"` - Interest earned every round
- `"Black Deck"` - Extra joker slot, no interest
- `"Magic Deck"` - Start with Crystal Ball voucher
- `"Nebula Deck"` - Start with Telescope voucher
- `"Ghost Deck"` - Spectral cards can appear in shop
- `"Abandoned Deck"` - No face cards in deck
- `"Checkered Deck"` - Half spades/clubs become hearts/diamonds
- `"Zodiac Deck"` - Start with random tarot cards
- `"Painted Deck"` - +1 hand size, no hearts or diamonds
- `"Anaglyph Deck"` - Double tag rewards
- `"Plasma Deck"` - Chips and mult balance when calculating score
- `"Erratic Deck"` - All ranks and suits random

#### stake

**Type:** `int`  
**Default:** `1`  
**Range:** 1-8  
**Description:** Difficulty level (higher = more challenging).

**Stake Levels:**
1. **White Stake** - Base difficulty
2. **Red Stake** - Small Blind gives no reward money
3. **Green Stake** - Required score scales faster
4. **Black Stake** - Shop can have eternal jokers
5. **Blue Stake** - -1 discard per round
6. **Purple Stake** - Required score scales faster
7. **Orange Stake** - -1 hand per round
8. **Gold Stake** - Shop can have rental jokers

#### seed

**Type:** `str` or `None`  
**Default:** `None`  
**Description:** Game seed for reproducible runs.

```python
# Random seed (different each run)
bot = Bot(deck="Red Deck", seed=None)

# Fixed seed (same sequence each run)
bot = Bot(deck="Red Deck", seed="ABC1234")

# Generate random seed
bot = Bot(deck="Red Deck", seed=bot.random_seed())
```

**Seed Format:**
- 7 characters long
- Alphanumeric (0-9, A-Z)
- Example: "1OGB5WO"

#### challenge

**Type:** `str` or `None`  
**Default:** `None`  
**Description:** Challenge run identifier.

```python
# Normal run
bot = Bot(deck="Red Deck", challenge=None)

# Challenge run (if supported)
bot = Bot(deck="Red Deck", challenge="challenge_name")
```

#### bot_port

**Type:** `int`  
**Default:** `12346`  
**Description:** UDP port for communication with Lua mod.

```python
# Default port
bot = Bot(deck="Red Deck", bot_port=12346)

# Custom port
bot = Bot(deck="Red Deck", bot_port=12350)
```

## Configuration Examples

### Maximum Performance Configuration

For the fastest possible bot execution:

```lua
BALATRO_BOT_CONFIG = {
    enabled = true,
    port = '12345',
    dt = 4.0/60.0,                          -- Fast game speed
    uncap_fps = true,                       -- No FPS limits
    instant_move = true,                    -- No animations
    disable_vsync = true,                   -- No VSync
    disable_card_eval_status_text = true,   -- No score text
    frame_ratio = 200,                      -- Minimal rendering
}
```

### Debugging Configuration

For visible gameplay and debugging:

```lua
BALATRO_BOT_CONFIG = {
    enabled = true,
    port = '12345',
    dt = 16.0/60.0,                         -- Slower, more visible
    uncap_fps = false,                      -- Normal FPS
    instant_move = false,                   -- Smooth animations
    disable_vsync = false,                  -- VSync enabled
    disable_card_eval_status_text = false,  -- Show score text
    frame_ratio = 1,                        -- Full rendering
}
```

### Balanced Configuration

Good compromise between performance and visibility:

```lua
BALATRO_BOT_CONFIG = {
    enabled = true,
    port = '12345',
    dt = 8.0/60.0,                          -- Moderate speed
    uncap_fps = true,                       -- Remove FPS cap
    instant_move = true,                    -- No animations
    disable_vsync = true,                   -- No VSync
    disable_card_eval_status_text = true,   -- No score text
    frame_ratio = 10,                       -- Some visual feedback
}
```

### Multi-Instance Configuration

For running multiple bots simultaneously:

**Bot Instance 1:**
```lua
-- config.lua for instance 1
BALATRO_BOT_CONFIG = {
    enabled = true,
    port = '12345',
    dt = 6.0/60.0,
    uncap_fps = true,
    instant_move = true,
    disable_vsync = true,
    disable_card_eval_status_text = true,
    frame_ratio = 150,
}
```

**Bot Instance 2:**
```lua
-- config.lua for instance 2  
BALATRO_BOT_CONFIG = {
    enabled = true,
    port = '12346',                         -- Different port
    dt = 6.0/60.0,
    uncap_fps = true,
    instant_move = true,
    disable_vsync = true,
    disable_card_eval_status_text = true,
    frame_ratio = 150,
}
```

### Configuration Validation

To validate your configuration is working correctly:

1. **Check mod loading:** Look for "Balatrobot v0.3 loaded" message
2. **Verify port binding:** Ensure no "port in use" errors
3. **Test bot communication:** Run a simple bot to verify connection
4. **Monitor performance:** Check if game runs at expected speed

### Troubleshooting Configuration Issues

**Game runs too slow:**
- Decrease `dt` value
- Increase `frame_ratio`
- Enable `instant_move`

**Game is unstable:**
- Increase `dt` value (try 8.0/60.0 or higher)
- Decrease `frame_ratio` (try 50 or lower)
- Disable `uncap_fps`

**Visual issues:**
- Set `frame_ratio = 1` for full rendering
- Disable `instant_move` for animations
- Enable `disable_vsync = false`

**Connection problems:**
- Verify `port` matches Python bot configuration
- Check firewall settings
- Try different port numbers

---

*Proper configuration is essential for optimal bot performance. Start with the balanced configuration and adjust based on your specific needs.* 