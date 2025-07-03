# Installation Guide

This guide will walk you through installing and setting up Balatrobot for automated Balatro gameplay.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Install Steamodded](#step-1-install-steamodded)
- [Step 2: Install Balatrobot Mod](#step-2-install-balatrobot-mod)
- [Step 3: Configure Balatrobot](#step-3-configure-balatrobot)
- [Step 4: Set Up Python Environment](#step-4-set-up-python-environment)
- [Step 5: Test Installation](#step-5-test-installation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing Balatrobot, ensure you have:

### Required Software
- **Balatro** (Steam version)
- **Python 3.7+** ([Download Python](https://python.org/downloads/))
- **Git** (for cloning repositories)

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 4GB minimum (8GB recommended for multiple instances)
- **Disk Space**: 100MB for mod files

### Important Notes
- ⚠️ **Steam Version Required**: The Epic Games Store version is not supported
- ⚠️ **Mod Warning**: This mod may not work with other Balatro mods
- ⚠️ **Risk**: Use at your own risk as with any game modification

## Step 1: Install Steamodded

Steamodded is required as the modding framework for Balatro.

### 1.1 Download Steamodded

1. Visit the [Steamodded GitHub repository](https://github.com/Steamopollys/Steamodded)
2. Download the latest release (v0.9.3 or higher recommended)
3. Extract the files to a temporary location

### 1.2 Install Steamodded

#### Windows Installation
```bash
# Navigate to your Balatro installation directory
cd "C:\Program Files (x86)\Steam\steamapps\common\Balatro"

# Copy Steamodded files to the game directory
# (Copy all files from the Steamodded download)
```

#### macOS/Linux Installation
```bash
# Find your Steam installation
# Usually: ~/.steam/steam/steamapps/common/Balatro
cd ~/.steam/steam/steamapps/common/Balatro

# Copy Steamodded files
# (Copy all files from the Steamodded download)
```

### 1.3 Verify Steamodded Installation

1. Launch Balatro through Steam
2. Look for "Mods" option in the main menu
3. If present, Steamodded is installed correctly

## Step 2: Install Balatrobot Mod

### 2.1 Download Balatrobot

```bash
# Clone the Balatrobot repository
git clone https://github.com/besteon/balatrobot.git

# Or download as ZIP from GitHub and extract
```

### 2.2 Install the Mod

#### Find Your Mods Directory

The mods directory is typically located at:
- **Windows**: `%APPDATA%\Balatro\Mods\`
- **macOS**: `~/Library/Application Support/Balatro/Mods/`
- **Linux**: `~/.local/share/Balatro/Mods/`

#### Copy Mod Files

```bash
# Create the mods directory if it doesn't exist
mkdir -p "/path/to/Balatro/Mods/"

# Copy the entire Balatrobot directory to the mods folder
cp -r balatrobot "/path/to/Balatro/Mods/Balatrobot-v0.3"
```

Your directory structure should look like:
```
Balatro/Mods/
└── Balatrobot-v0.3/
    ├── main.lua
    ├── config.lua
    ├── lib/
    ├── src/
    ├── bot.py
    ├── bot_example.py
    └── flush_bot.py
```

## Step 3: Configure Balatrobot

### 3.1 Edit Configuration

Open `config.lua` in your mod directory and configure the settings:

```lua
BALATRO_BOT_CONFIG = {
    enabled = true,              -- Enable/disable the mod
    port = '12345',              -- UDP port for communication
    dt = 8.0/60.0,              -- Game speed multiplier
    uncap_fps = true,           -- Remove FPS cap
    instant_move = true,        -- Disable animations
    disable_vsync = true,       -- Disable VSync
    disable_card_eval_status_text = true,  -- Disable score text
    frame_ratio = 100,          -- Render every 100th frame
}
```

### 3.2 Configuration Options Explained

| Option | Description | Recommended |
|--------|-------------|-------------|
| `enabled` | Master switch for all mod functionality | `true` |
| `port` | UDP port for bot communication | `'12345'` |
| `dt` | Game update speed (smaller = faster) | `8.0/60.0` |
| `uncap_fps` | Remove FPS limitations | `true` |
| `instant_move` | Skip movement animations | `true` |
| `disable_vsync` | Disable vertical sync | `true` |
| `disable_card_eval_status_text` | Hide score popups | `true` |
| `frame_ratio` | Render frequency (higher = faster) | `100` |

### 3.3 Performance vs Visual Quality

For **maximum performance** (fastest bot execution):
```lua
dt = 4.0/60.0,
frame_ratio = 200,
instant_move = true,
```

For **visible gameplay** (debugging/demonstration):
```lua
dt = 16.0/60.0,
frame_ratio = 1,
instant_move = false,
```

## Step 4: Set Up Python Environment

### 4.1 Install Python Dependencies

Balatrobot uses only standard Python libraries, so no additional packages are required:

```bash
# Verify Python installation
python --version  # Should be 3.7+

# Navigate to the mod directory
cd "/path/to/Balatro/Mods/Balatrobot-v0.3"

# Test Python scripts can run
python bot_example.py --help
```

### 4.2 Optional: Create Virtual Environment

```bash
# Create virtual environment (optional but recommended)
python -m venv balatrobot-env

# Activate virtual environment
# Windows:
balatrobot-env\Scripts\activate
# macOS/Linux:
source balatrobot-env/bin/activate
```

### 4.3 Verify Python Setup

Create a simple test script to verify everything works:

```python
# test_setup.py
from bot import Bot, Actions, State

print("Balatrobot Python components loaded successfully!")
print(f"Available states: {len(State)}")
print(f"Available actions: {len(Actions)}")
```

Run the test:
```bash
python test_setup.py
```

## Step 5: Test Installation

### 5.1 Launch Balatro with Mods

1. Start Balatro through Steam
2. In the main menu, click "Mods"
3. Verify "Balatrobot" appears in the mod list
4. Enable the mod if it's not already enabled
5. Restart Balatro

### 5.2 Verify Mod Loading

When Balatro starts with the mod enabled, you should see:
- Debug message: "Balatrobot v0.3 loaded" (if debug is enabled)
- Game runs noticeably faster (if performance settings are enabled)
- Network socket listening on the configured port

### 5.3 Test Bot Communication

#### Quick Test with Example Bot

1. Start Balatro with the mod enabled
2. In a terminal, navigate to the mod directory
3. Run the example bot:

```bash
python bot_example.py
```

#### Expected Behavior

- Balatro should start a new run automatically
- The bot should make decisions (skip small/big blinds, play cards)
- You should see the game progressing automatically

#### Success Indicators

✅ **Working correctly if you see:**
- Game starts automatically
- Cards are played/discarded automatically
- Shop actions occur without user input
- Game progresses through rounds

❌ **Check troubleshooting if:**
- Bot script hangs or shows errors
- Game doesn't start automatically
- No automatic actions occur
- Connection timeout errors

## Troubleshooting

### Common Issues

#### Issue: "ModuleNotFoundError: No module named 'bot'"
**Solution**: Ensure you're running Python from the correct directory
```bash
cd "/path/to/Balatro/Mods/Balatrobot-v0.3"
python bot_example.py
```

#### Issue: "Connection timeout" or "Network error"
**Solutions**:
1. Check if Balatro is running with mods enabled
2. Verify the port in `config.lua` matches the bot port
3. Check firewall settings allow UDP traffic on the port
4. Try a different port number

#### Issue: Game doesn't start automatically
**Solutions**:
1. Verify the mod is enabled in Balatro's mod menu
2. Check `config.lua` has `enabled = true`
3. Restart Balatro after configuration changes
4. Check the bot specifies a valid deck name

#### Issue: Bot actions don't work
**Solutions**:
1. Verify all required bot methods are implemented
2. Check bot returns valid action formats
3. Enable debug logging to see action validation errors

### Debug Mode

Enable debug output by modifying your bot:

```python
class DebugBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add debug prints
        
    def chooseaction(self):
        action = super().chooseaction()
        print(f"Sending action: {action}")
        return action
```

### Port Conflicts

If you encounter port conflicts:

1. **Change the port in config.lua**:
```lua
port = '12346',  -- Use different port
```

2. **Update your bot**:
```python
mybot = Bot(deck="Red Deck", stake=1, bot_port=12346)
```

3. **Check for port usage**:
```bash
# Windows
netstat -an | findstr :12345

# macOS/Linux  
netstat -an | grep :12345
```

### Getting Help

If you continue experiencing issues:

1. **Check the GitHub Issues** for known problems
2. **Enable debug logging** to identify specific errors
3. **Test with the provided examples** before custom bots
4. **Verify all prerequisites** are correctly installed

---

*Once installation is complete, proceed to the [Bot Development Guide](bot-development.md) to create your first bot!* 