# Configuration Guide

Balatrobot configuration is controlled by `config.lua` in the mod directory.

## Configuration File

```lua
BALATRO_BOT_CONFIG = {
    enabled = true,                           -- Enable/disable mod functionality
    port = '12345',                          -- UDP port for bot communication
    dt = 8.0/60.0,                          -- Game update speed (lower = faster)
    uncap_fps = true,                       -- Remove FPS limitations
    instant_move = true,                    -- Disable movement animations
    disable_vsync = true,                   -- Disable vertical sync
    disable_card_eval_status_text = true,   -- Hide card scoring text
    frame_ratio = 100,                      -- Render every Nth frame (higher = faster)
}
```

## Configuration Options

### enabled
**Type:** `boolean` | **Default:** `true`

Master switch for all mod functionality. Set to `false` to disable the mod without uninstalling.

### port
**Type:** `string` | **Default:** `'12345'`

UDP port for bot communication. Must match the port in your Python bot. Can be overridden by command line argument when launching Balatro.

### dt
**Type:** `number` | **Default:** `8.0/60.0`

Game update interval in seconds. Lower values make the game run faster but use more CPU.

### uncap_fps
**Type:** `boolean` | **Default:** `true`

Remove FPS limitations for maximum game speed. Recommended for bot performance.

### instant_move
**Type:** `boolean` | **Default:** `true`

Skip movement animations for instant card positioning. Provides significant performance improvement.

### disable_vsync
**Type:** `boolean` | **Default:** `true`

Disable vertical synchronization for better performance.

### disable_card_eval_status_text
**Type:** `boolean` | **Default:** `true`

Hide floating score text ("+10", etc.) when cards are scored for better performance.

### frame_ratio
**Type:** `integer` | **Default:** `100`

Render every Nth frame. Higher values provide better performance with less visual output.

## Multi-Instance Setup

For multiple bot instances, use different ports:

```lua
-- Instance 1
port = '12345'

-- Instance 2  
port = '12346'
```

Launch Balatro with specific port:
```bash
Balatro.exe 12346
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