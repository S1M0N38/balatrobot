# BalatroBot

A powerful botting framework for Balatro that provides both Lua and Python APIs for creating automated gameplay bots.

## Features

- 🎮 **Game State Access** - Full access to Balatro's game state and mechanics
- 🐍 **Python API** - Write bots in Python with a clean, intuitive interface
- 🌙 **Lua Integration** - Direct Lua scripting support for advanced users
- 🔌 **Middleware System** - Extensible middleware for custom bot behaviors
- 📊 **Logging & Debugging** - Comprehensive logging system for bot development
- 🚀 **Easy Setup** - Simple installation and configuration process

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/balatrobot.git
cd balatrobot
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the bot (see [Configuration Guide](docs/configuration.md))

### Basic Usage

**Python Bot Example:**
```python
from bot import BalatroBot

bot = BalatroBot()

@bot.on_turn_start
def handle_turn_start(game_state):
    # Your bot logic here
    pass

bot.run()
```

**Lua Bot Example:**
```lua
local bot = require('src.bot')

bot.on_turn_start(function(game_state)
    -- Your bot logic here
end)
```

## Documentation

- 📖 [Full Documentation](https://your-username.github.io/balatrobot/)
- 🛠️ [Installation Guide](docs/installation.md)
- ⚙️ [Configuration](docs/configuration.md)
- 🏗️ [Architecture Overview](docs/architecture.md)
- 🤖 [Bot Development Guide](docs/bot-development.md)
- 🐍 [Python API Reference](docs/python-api.md)
- 💡 [Examples](docs/examples.md)
- 🔧 [Troubleshooting](docs/troubleshooting.md)

## Project Structure

```
balatrobot/
├── src/           # Lua source code
├── docs/          # Documentation
├── lib/           # External Lua libraries
├── bot.py         # Python API
├── main.lua       # Main entry point
└── config.lua     # Configuration
```

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:

- Check the [Troubleshooting Guide](docs/troubleshooting.md)
- Open an issue on GitHub
- Join our community discussions

