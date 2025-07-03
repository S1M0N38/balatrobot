# Troubleshooting Guide

Comprehensive guide to diagnosing and fixing common issues with Balatrobot.

## Quick Diagnostics

### Pre-Flight Checklist

Before troubleshooting, verify these basics:

**Prerequisites Met**
- [ ] Balatro (Steam version) installed
- [ ] Steamodded v0.9.3+ installed and working
- [ ] Python 3.7+ installed
- [ ] Balatrobot mod copied to correct directory

**Configuration Basics**
- [ ] `config.lua` has `enabled = true`
- [ ] Port numbers match between Lua config and Python bot
- [ ] No firewall blocking the port
- [ ] Balatro launched with mod enabled

**Connection Test**
- [ ] Balatro shows "Balatrobot v0.3 loaded" message
- [ ] Python script runs without import errors
- [ ] Bot sends "HELLO" message on startup

### Quick Fix Commands

```bash
# Test Python environment
python -c "from bot import Bot, Actions; print('Import successful')"

# Check if port is in use
netstat -an | grep :12345  # Linux/macOS
netstat -an | findstr :12345  # Windows

# Test UDP communication
# (Run this in Python while game is running)
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"HELLO", ("localhost", 12345))
sock.settimeout(5)
try:
    data, addr = sock.recvfrom(1024)
    print("Received:", data[:100])
except socket.timeout:
    print("No response - check game is running with mod")
```

## Installation Issues

### Issue: Mod Not Loading

**Symptoms:**
- No "Balatrobot" in mod list
- No loading message
- Game starts normally without bot functionality

**Solutions:**

1. **Check Mod Directory Structure**
   ```
   Balatro/Mods/
   └── Balatrobot-v0.3/
       ├── main.lua
       ├── config.lua
       └── src/
   ```

2. **Verify Steamodded Installation**
   - Launch Balatro
   - Look for "Mods" in main menu
   - If missing, reinstall Steamodded

3. **Check File Permissions**
   ```bash
   # Ensure files are readable
   ls -la /path/to/Balatro/Mods/Balatrobot-v0.3/
   ```

4. **Validate main.lua Syntax**
   - Open `main.lua` in text editor
   - Check for syntax errors or corruption
   - Re-download if necessary

### Issue: Python Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'bot'
ImportError: cannot import name 'Actions'
```

**Solutions:**

1. **Check Working Directory**
   ```bash
   # Navigate to mod directory first
   cd "/path/to/Balatro/Mods/Balatrobot-v0.3"
   python bot_example.py
   ```

2. **Verify File Integrity**
   ```bash
   # Check all required files exist
   ls -la bot.py gamestates.py
   ```

3. **Python Path Issues**
   ```python
   import sys
   import os
   sys.path.append(os.path.dirname(os.path.abspath(__file__)))
   from bot import Bot, Actions
   ```

### Issue: Steamodded Compatibility

**Symptoms:**
- Other mods stop working
- Lua errors in console
- Game crashes on startup

**Solutions:**

1. **Check Steamodded Version**
   - Ensure v0.9.3 or higher
   - Update if necessary

2. **Test Mod Isolation**
   - Disable other mods temporarily
   - Test if Balatrobot works alone
   - Re-enable mods one by one

3. **Lua Error Debugging**
   - Enable Steamodded debug console
   - Look for specific error messages
   - Check for conflicting function hooks

## Connection Problems

### Issue: Connection Timeout

**Symptoms:**
```
Connection timeout
Unknown network error: timeout
Bot hangs on startup
```

**Solutions:**

1. **Port Conflicts**
   ```bash
   # Check what's using the port
   lsof -i :12345  # Linux/macOS
   netstat -ano | findstr :12345  # Windows
   
   # Try different port
   # In config.lua: port = '12346'
   # In Python: bot_port=12346
   ```

2. **Firewall Issues**
   ```bash
   # Windows: Allow through Windows Firewall
   # Add exception for Balatro.exe and Python
   
   # Linux: Check iptables
   sudo ufw allow 12345/udp
   
   # macOS: Check System Preferences > Security
   ```

3. **Network Interface Issues**
   ```python
   # Test specific interface binding
   import socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.bind(('127.0.0.1', 12345))  # Localhost only
   # or
   sock.bind(('0.0.0.0', 12345))   # All interfaces
   ```

### Issue: Game Doesn't Respond to Bot

**Symptoms:**
- Bot script runs without errors
- Game doesn't start automatically
- No automatic actions occur

**Solutions:**

1. **Check Mod Enabled State**
   - In Balatro, go to Mods menu
   - Ensure Balatrobot is enabled (checkmark)
   - Restart Balatro if needed

2. **Verify Configuration**
   ```lua
   -- In config.lua, ensure:
   BALATRO_BOT_CONFIG = {
       enabled = true,  -- Must be true
       port = '12345',  -- Must match Python bot
   }
   ```

3. **Test Manual Commands**
   ```python
   # Test raw UDP communication
   bot = Bot(deck="Red Deck")
   bot.sendcmd("HELLO")
   # Should receive game state response
   ```

### Issue: Partial Communication

**Symptoms:**
- Bot receives some data but not others
- Intermittent connection drops
- Commands sent but not executed

**Solutions:**

1. **UDP Buffer Size**
   ```python
   # Increase buffer size for large game states
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
   ```

2. **Network Timing Issues**
   ```python
   # Add delays between commands
   import time
   bot.sendcmd("HELLO")
   time.sleep(0.1)  # Small delay
   ```

3. **JSON Parsing Errors**
   ```python
   try:
       data = json.loads(response)
   except json.JSONDecodeError as e:
       print(f"JSON Error: {e}")
       print(f"Raw data: {response[:200]}")
   ```

## Bot Behavior Issues

### Issue: Bot Makes Invalid Actions

**Symptoms:**
```
Error: Incorrect number of params for action PLAY_HAND
Error: Action invalid for action BUY_CARD
```

**Solutions:**

1. **Action Format Validation**
   ```python
   def select_cards_from_hand(self, G):
       hand = G.get("hand", [])
       if not hand:
           return [Actions.PLAY_HAND, []]  # Empty action
       
       # Ensure indices are valid
       indices = [1, 2]  # 1-indexed
       max_index = len(hand)
       valid_indices = [i for i in indices if 1 <= i <= max_index]
       
       return [Actions.PLAY_HAND, valid_indices]
   ```

2. **State Validation**
   ```python
   def select_shop_action(self, G):
       # Check if actually in shop
       if "shop" not in G:
           return [Actions.END_SHOP]
       
       shop_cards = G["shop"].get("cards", [])
       if not shop_cards:
           return [Actions.END_SHOP]
       
       # Validate card index exists
       if len(shop_cards) >= 1:
           return [Actions.BUY_CARD, [1]]
       
       return [Actions.END_SHOP]
   ```

3. **Resource Checking**
   ```python
   def select_shop_action(self, G):
       dollars = G.get("dollars", 0)
       shop = G.get("shop", {})
       cards = shop.get("cards", [])
       
       for i, card in enumerate(cards):
           cost = card.get("cost", 999)
           if dollars >= cost:
               return [Actions.BUY_CARD, [i + 1]]
       
       return [Actions.END_SHOP]
   ```

### Issue: Bot Doesn't Implement All Methods

**Symptoms:**
```
NotImplementedError: Error: Bot.select_cards_from_hand must be implemented.
```

**Solutions:**

1. **Complete Implementation Template**
   ```python
   class MyBot(Bot):
       def skip_or_select_blind(self, G):
           return [Actions.SELECT_BLIND]
       
       def select_cards_from_hand(self, G):
           return [Actions.PLAY_HAND, [1]]
       
       def select_shop_action(self, G):
           return [Actions.END_SHOP]
       
       def select_booster_action(self, G):
           return [Actions.SKIP_BOOSTER_PACK]
       
       def sell_jokers(self, G):
           return [Actions.SELL_JOKER, []]
       
       def rearrange_jokers(self, G):
           return [Actions.REARRANGE_JOKERS, []]
       
       def use_or_sell_consumables(self, G):
           return [Actions.USE_CONSUMABLE, []]
       
       def rearrange_consumables(self, G):
           return [Actions.REARRANGE_CONSUMABLES, []]
       
       def rearrange_hand(self, G):
           return [Actions.REARRANGE_HAND, []]
   ```

2. **Method Assignment Pattern**
   ```python
   # Alternative: assign functions to bot instance
   bot = Bot(deck="Red Deck")
   bot.skip_or_select_blind = lambda G: [Actions.SELECT_BLIND]
   bot.select_cards_from_hand = lambda G: [Actions.PLAY_HAND, [1]]
   # ... assign all other methods
   ```

### Issue: Bot Gets Stuck in Loops

**Symptoms:**
- Bot repeats same action continuously
- Game doesn't progress
- Bot state doesn't update

**Solutions:**

1. **State Progression Checks**
   ```python
   def select_cards_from_hand(self, G):
       # Track previous states to detect loops
       if "last_hand_state" not in self.state:
           self.state["last_hand_state"] = None
       
       current_state = str(G.get("hand", []))
       if current_state == self.state["last_hand_state"]:
           # State hasn't changed, try different action
           return [Actions.DISCARD_HAND, [1]]
       
       self.state["last_hand_state"] = current_state
       return [Actions.PLAY_HAND, [1]]
   ```

2. **Timeout Mechanisms**
   ```python
   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.state["action_count"] = 0
       self.state["max_actions"] = 1000
   
   def chooseaction(self):
       self.state["action_count"] += 1
       if self.state["action_count"] > self.state["max_actions"]:
           print("Max actions reached, stopping bot")
           self.running = False
           return [Actions.PASS]
       
       return super().chooseaction()
   ```

## Performance Problems

### Issue: Bot Runs Too Slowly

**Symptoms:**
- Visible lag between actions
- Slow game progression
- High CPU usage

**Solutions:**

1. **Optimize Configuration**
   ```lua
   -- In config.lua
   BALATRO_BOT_CONFIG = {
       dt = 4.0/60.0,         -- Faster game time
       frame_ratio = 200,     -- Less rendering
       instant_move = true,   -- No animations
   }
   ```

2. **Optimize Bot Logic**
   ```python
   def optimized_hand_analysis(self, hand):
       # Use efficient algorithms
       if not hand:
           return [Actions.PLAY_HAND, []]
       
       # Quick heuristics instead of complex analysis
       high_cards = [i+1 for i, card in enumerate(hand) 
                    if card["value"] >= 10]
       
       if high_cards:
           return [Actions.PLAY_HAND, high_cards[:1]]
       
       return [Actions.PLAY_HAND, [1]]
   ```

3. **Reduce State Caching**
   ```python
   # Avoid expensive state caching in production
   def select_cards_from_hand(self, G):
       # cache_state("hand_selection", G)  # Disable for performance
       return self.choose_cards(G)
   ```

### Issue: Memory Usage Grows Over Time

**Symptoms:**
- Increasing RAM usage
- Bot slows down over time
- Eventually crashes with memory error

**Solutions:**

1. **Clean Up State Data**
   ```python
   def cleanup_state(self):
       # Remove old data periodically
       current_round = self.G.get("round", 1)
       for key in list(self.state.keys()):
           if key.startswith("round_"):
               round_num = int(key.split("_")[1])
               if round_num < current_round - 10:
                   del self.state[key]
   ```

2. **Limit State Caching**
   ```python
   def cache_state(self, G):
       # Only cache last N states
       max_cache = 100
       if len(self.cached_states) > max_cache:
           self.cached_states.pop(0)  # Remove oldest
       self.cached_states.append(G.copy())
   ```

## Game Crashes

### Issue: Balatro Crashes on Startup

**Symptoms:**
- Game closes immediately after launch
- Lua error messages
- Steam shows "running" then stops

**Solutions:**

1. **Check Lua Syntax**
   - Validate all `.lua` files for syntax errors
   - Use online Lua syntax checker
   - Re-download mod if corrupted

2. **Disable Other Mods**
   - Move other mods out of Mods directory
   - Test Balatrobot alone
   - Check for mod conflicts

3. **Steamodded Compatibility**
   - Ensure Steamodded version compatibility
   - Update Steamodded if necessary
   - Check Steamodded documentation

### Issue: Game Crashes During Bot Execution

**Symptoms:**
- Game runs fine until bot starts
- Crashes during specific actions
- Error messages in logs

**Solutions:**

1. **Action Validation**
   ```python
   def safe_action(self, action_func, G):
       try:
           result = action_func(G)
           # Validate result format
           if not isinstance(result, list) or len(result) < 1:
               return [Actions.PASS]
           return result
       except Exception as e:
           print(f"Action error: {e}")
           return [Actions.PASS]
   ```

2. **Network Error Handling**
   ```python
   def sendcmd(self, cmd, **kwargs):
       try:
           msg = bytes(cmd, "utf-8")
           self.sock.sendto(msg, self.addr)
       except Exception as e:
           print(f"Network error: {e}")
           # Attempt reconnection
           self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   ```

## Debug Tools

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugBot(Bot):
    def chooseaction(self):
        action = super().chooseaction()
        logger.debug(f"Action chosen: {action}")
        logger.debug(f"Game state keys: {list(self.G.keys())}")
        return action
```

### Network Debugging

```python
def debug_network(self):
    """Test UDP communication manually"""
    import socket
    import json
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    
    # Send HELLO
    sock.sendto(b"HELLO", ("localhost", 12345))
    
    try:
        data, addr = sock.recvfrom(4096)
        print(f"Received {len(data)} bytes from {addr}")
        
        # Try to parse as JSON
        try:
            parsed = json.loads(data)
            print(f"JSON keys: {list(parsed.keys())}")
        except:
            print(f"Raw data: {data[:200]}")
            
    except socket.timeout:
        print("No response received")
    except Exception as e:
        print(f"Error: {e}")
```

### State Inspection

```python
def inspect_game_state(self, G):
    """Print detailed game state information"""
    print("=== GAME STATE DEBUG ===")
    print(f"Waiting for: {G.get('waitingFor')}")
    print(f"State: {G.get('state')}")
    
    if "hand" in G:
        print(f"Hand size: {len(G['hand'])}")
        for i, card in enumerate(G["hand"]):
            print(f"  {i+1}: {card.get('name', 'Unknown')}")
    
    if "shop" in G:
        shop = G["shop"]
        print(f"Shop cards: {len(shop.get('cards', []))}")
        print(f"Reroll cost: {shop.get('reroll_cost', 'Unknown')}")
    
    if "jokers" in G:
        print(f"Jokers: {len(G['jokers'])}")
    
    print("========================")
```

### Performance Monitoring

```python
import time

class BenchmarkBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_times = []
        self.start_time = time.time()
    
    def chooseaction(self):
        start = time.time()
        action = super().chooseaction()
        end = time.time()
        
        self.action_times.append(end - start)
        
        # Print stats every 100 actions
        if len(self.action_times) % 100 == 0:
            avg_time = sum(self.action_times) / len(self.action_times)
            total_time = end - self.start_time
            actions_per_sec = len(self.action_times) / total_time
            
            print(f"Actions: {len(self.action_times)}")
            print(f"Avg time: {avg_time:.4f}s")
            print(f"Actions/sec: {actions_per_sec:.2f}")
        
        return action
```

---

*Still having issues? Check the GitHub repository for the latest known issues and solutions, or create a new issue with your specific problem details.* 