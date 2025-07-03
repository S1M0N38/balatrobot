# Balatrobot Documentation

Welcome to the comprehensive documentation for **Balatrobot** - A powerful botting API for the game Balatro.

## Overview

Balatrobot is a sophisticated modding framework that provides a complete API for creating automated bots for the card game Balatro. It consists of both Lua components (that run within the game) and Python components (for bot logic implementation).

### Key Features

- **UDP-based Communication**: Real-time communication between the game and bot logic
- **Comprehensive Game State Access**: Full access to hand, jokers, shop, blinds, and more
- **Action System**: Complete control over game actions (play, discard, shop, etc.)
- **Performance Optimizations**: Built-in speed optimizations for faster bot execution
- **Logging & Replay**: Complete action logging and replay functionality
- **Multi-instance Support**: Run multiple bot instances simultaneously

## Quick Start

1. **Install Steamodded** (v0.9.3+ recommended)
2. **Install Balatrobot mod** in your Steamodded mods directory
3. **Configure** the bot settings in `config.lua`
4. **Create your bot** by extending the Python `Bot` class
5. **Run** your bot and watch it play!

```python
from bot import Bot, Actions

class MyBot(Bot):
    def skip_or_select_blind(self, G):
        return [Actions.SELECT_BLIND]
    
    def select_cards_from_hand(self, G):
        return [Actions.PLAY_HAND, [1]]
    
    # ... implement other required methods

# Run the bot
mybot = MyBot(deck="Red Deck", stake=1)
mybot.run()
```

## Documentation Sections

### Core Documentation
- **[Architecture](architecture.md)** - System design and component interaction
- **[Installation](installation.md)** - Complete setup guide
- **[Configuration](configuration.md)** - Configuration options and settings

### Bot Development
- **[Bot Development Guide](bot-development.md)** - How to create your own bots
- **[Game State Reference](game-state.md)** - Understanding the game state object
- **[Actions Reference](actions.md)** - Complete list of available actions

### API Reference
- **[Python API](python-api.md)** - Python classes and methods
- **[Lua API](lua-api.md)** - Lua modules and functions

### Examples & Guides
- **[Examples](examples.md)** - Working bot examples with explanations
- **[Best Practices](best-practices.md)** - Tips for effective bot development
- **[Performance Optimization](performance.md)** - Making your bots run faster

### Advanced Topics
- **[Multi-Instance Setup](multi-instance.md)** - Running multiple bots
- **[Logging & Replay](logging-replay.md)** - Recording and replaying games
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Requirements

- **Balatro** (Steam version)
- **Steamodded** v0.9.3 or higher
- **Python 3.7+**
- **Windows/Linux/macOS** (Windows path in examples)

## Support

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: This comprehensive guide covers all functionality
- **Community**: Join the Steamodded community for general modding support

---

*This documentation covers Balatrobot v0.3. For the latest updates, check the project repository.* 