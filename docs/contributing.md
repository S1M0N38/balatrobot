# Contributing to BalatroBot

Welcome to BalatroBot! We're excited that you're interested in contributing to this Python framework and Lua mod for creating automated bots to play Balatro.

BalatroBot uses a dual-architecture approach with a Python framework that communicates with a Lua mod running inside Balatro via TCP sockets. This allows for real-time bot automation and game state analysis.

## Project Status & Priorities

We track all development work using the [BalatroBot GitHub Project](https://github.com/users/S1M0N38/projects/7). This is the best place to see current priorities, ongoing work, and opportunities for contribution.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Balatro**: Version 1.0.1o-FULL
- **SMODS (Steamodded)**: Version 1.0.0-beta-0711a or newer
- **Python**: 3.13+ (managed via uv)
- **uv**: Python package manager ([Installation Guide](https://docs.astral.sh/uv/))
- **OS**: macOS, Linux. Windows is not currently supported
- **[DebugPlus](https://github.com/WilsontheWolf/DebugPlus) (optional)**: useful for Lua API development and debugging

### Development Environment Setup

1. **Fork and Clone**

    ```bash
    git clone https://github.com/YOUR_USERNAME/balatrobot.git
    cd balatrobot
    ```

2. **Install Dependencies**

    ```bash
    uv sync --all-extras
    ```

3. **Stars Balatro with Mods**

    ```bash
    ./balatro.sh -p 12346
    ```

4. **Verify Balatro is Running**

    ```bash
    # Check if Balatro is running
    ./balatro.sh --status

    # Monitor startup logs
    tail -n 100 logs/balatro_12346.log
    ```

    Look for these success indicators:

    - "BalatrobotAPI initialized"
    - "BalatroBot loaded - version X.X.X"
    - "TCP socket created on port 12346"

## How to Contribute

### Types of Contributions Welcome

- **Bug Fixes**: Issues tracked in our GitHub project
- **Feature Development**: New bot strategies, API enhancements
- **Performance Improvements**: Optimization of TCP communication or game interaction
- **Documentation**: Improvements to guides, API documentation, or examples
- **Testing**: Additional test coverage, edge case handling

### Contribution Workflow

1. **Check Issues First** (Highly Encouraged)

    - Browse the [BalatroBot GitHub Project](https://github.com/users/S1M0N38/projects/7)
    - Comment on issues you'd like to work on
    - Create new issues for bugs or feature requests

2. **Fork & Branch**

    ```bash
    git checkout -b feature/your-feature-name
    ```

3. **Make Changes**

    - Follow our code style guidelines (see below)
    - Add tests for new functionality
    - Update documentation as needed

4. **Create Pull Request**

    - **Important**: Enable "Allow edits from maintainers" when creating your PR
    - Link to related issues
    - Provide clear description of changes
    - Include test for new functionality

### Commit Messages

We highly encourage following [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat(api): add new game state detection
fix(tcp): resolve connection timeout issues
docs(readme): update setup instructions
test(api): add shop booster validation tests
```

## Development & Testing

### Code Quality Tools

```bash
# Python linting and formatting
ruff check .
ruff check --select I --fix .
ruff format .

# Markdown formatting (docs and specific files)
mdformat --number docs/index.md docs/installation.md docs/developing-bots.md docs/protocol-api.md docs/contributing.md README.md

# Type checking
basedpyright
```

### Testing Requirements

!!! warning

    All tests require Balatro to be running in the background. Use `./balatro.sh --status` to check if the game is running.

#### Single Instance Testing

```bash
# Start Balatro with default port (12346)
./balatro.sh -p 12346

# Run all tests
pytest

# Run specific test file
pytest tests/lua/test_api_functions.py

# Run with verbose output and stop on first failure
pytest -vx

# Run tests on specific port
pytest --port 12347 tests/lua/endpoints/test_cash_out.py
```

#### Parallel Testing with Multiple Balatro Instances

The test suite supports running tests in parallel across multiple Balatro instances. This dramatically reduces test execution time by distributing tests across multiple game instances.

**Setup for Parallel Testing:**

1. **Check existing instances and start multiple Balatro instances on different ports**:

    ```bash
    # First, check if any instances are already running
    ./balatro.sh --status

    # If you need to kill all existing instances first:
    ./balatro.sh --kill
    ```

    ```bash
    # Start two instances with a single command
    ./balatro.sh -p 12346 -p 12347

    # With performance optimizations for faster testing
    ./balatro.sh --fast -p 12346

    # Headless mode for server environments
    ./balatro.sh --headless -p 12346

    # Fast Headless mode on 4 instances (recommended configuration)
    ./balatro.sh --headless --fast -p 12346 -p 12347 -p 12348 -p 12349
    ```

2. **Run tests in parallel**:

    ```bash
    # Two workers (faster than single instance)
    pytest -n 2 --port 12346 --port 12347

    # Four workers (recommended configuration)
    pytest -n 4 --port 12346 --port 12347 --port 12348 --port 12349
    ```

**Benefits:**

- **Faster test execution**: ~4x speedup with 4 parallel workers
- **Port isolation**: Each worker uses its dedicated Balatro instance

**Notes:**

- Each Balatro instance must be running on a different port before starting tests
- Tests automatically distribute across available workers
- Monitor logs for each instance: `tail -f logs/balatro_12346.log`
- Logs are automatically created in the `logs/` directory with format `balatro_PORT.log`

**balatro.sh Command Options:**

```bash
# Usage examples
./balatro.sh -p 12347                   # Start single instance on port 12347
./balatro.sh -p 12346 -p 12347          # Start two instances on ports 12346 and 12347
./balatro.sh --headless --fast -p 12346 # Start with headless and fast mode
./balatro.sh --kill                     # Kill all running Balatro instances
./balatro.sh --status                   # Show running instances
```

**balatro.sh Modes:**

- **`--headless`**: Enable headless mode (sets `BALATROBOT_HEADLESS=1`)

    - Minimizes and hides game window
    - Completely disables Love2D graphics operations
    - Minimal CPU/GPU usage for pure game logic execution
    - Ideal for server environments and cloud-based bot training

- **`--fast`**: Enable fast mode (sets `BALATROBOT_FAST=1`)

    - Unlimited FPS, 10x game speed, 6x faster animations
    - Disabled shadows, bloom, CRT effects, VSync
    - Complete audio muting
    - Optimized for maximum execution speed during bot training

**Test Prerequisites and Workflow:**

```bash
# 1. Check if Balatro instances are already running
./balatro.sh --status

# 2. If instances are running on needed ports, you can proceed with testing
# If you need to kill all running instances and start fresh:
./balatro.sh --kill

# 3. Start the required instances
./balatro.sh --headless --fast -p 12346 -p 12347 -p 12348 -p 12349

# 4. Run parallel tests
pytest -n 4 --port 12346 --port 12347 --port 12348 --port 12349 tests/lua/
```

**Troubleshooting Test Failures**:

- **Connection timeouts**: Ensure TCP port 12346 is available
- **Game state errors**: Verify game is responsive and hasn't crashed
- **Invalid responses**: Check mod loaded correctly in `balatro.log`
- **Balatro crashes**: Stop testing immediately, investigate crash logs, restart game before retrying

### Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## Technical Guidelines

### Python Development

- **Style**: Follow modern Python 3.13+ patterns
- **Type Hints**: Use pipe operator for unions (`str | int | None`)
- **Type Aliases**: Use `type` statement
- **Docstrings**: Google-style without type information (types in annotations)
- **Generics**: Modern syntax (`class Container[T]:`)

### Lua Development

- **Focus Area**: Primary development is on `src/lua/api.lua`
- **Communication**: TCP protocol on port 12346
- **Protocol**: Bot sends "HELLO" → Game responds with JSON state → Bot sends actions
- **Debugging**: Use DebugPlus mod for enhanced debugging capabilities

### Architecture Context

The project consists of:

- **Lua API** (`src/lua/api.lua`): Game-side mod handling socket communication
- **Python Framework** (`src/balatrobot/`): Bot development framework (being refactored)
- **TCP Communication**: Real-time bidirectional communication
- **Testing Suite**: Comprehensive API and integration tests

### Configuration System

The BalatroBot mod includes a sophisticated configuration system that optimizes Balatro for bot automation:

#### Environment Variables

Configure BalatroBot behavior using these environment variables:

- **`BALATROBOT_HEADLESS`**: Set to `"1"` to enable headless mode (no graphics rendering)
- **`BALATROBOT_FAST`**: Set to `"1"` to enable fast mode (10x game speed, disabled visuals)
- **`BALATROBOT_PORT`**: TCP port for communication (default: "12346")

#### Fast Mode Configuration

Fast mode (`BALATROBOT_FAST=1`) applies aggressive optimizations for bot training:

- **Performance**: Unlimited FPS, 10x game speed, 6x faster animations
- **Graphics**: Disabled shadows, bloom, CRT effects, VSync, texture scaling set to nearest neighbor
- **Audio**: Complete audio muting (volume, music, game sounds)
- **Visual Effects**: Disabled motion blur, screen shake, rumble effects
- **Resource Usage**: Optimized for maximum execution speed

#### Normal Mode Configuration

Normal mode preserves standard game experience while maintaining bot compatibility:

- **Performance**: 60 FPS cap, normal game speed, standard animations
- **Graphics**: Full visual quality with shadows, bloom, and CRT effects enabled
- **Audio**: Standard audio levels (50% main volume, 100% music/sounds)
- **Visual Effects**: Normal motion and screen effects enabled

#### Headless Mode Configuration

Headless mode (`BALATROBOT_HEADLESS=1`) disables all graphics for server environments:

- **Window Management**: Minimizes and hides game window
- **Rendering**: Completely disables Love2D graphics operations
- **Resource Usage**: Minimal CPU/GPU usage for pure game logic execution
- **Server Deployment**: Ideal for cloud-based bot training

#### Implementation Details

The configuration system is implemented in `src/lua/settings.lua` and provides:

- **Environment Detection**: Reads environment variables on mod initialization
- **Love2D Patches**: Modifies game engine behavior for performance optimization
- **Balatro Integration**: Configures game-specific settings through global variables
- **Fallback Handling**: Graceful degradation when graphics context is unavailable

This configuration system enables BalatroBot to run efficiently in diverse environments, from local development with full graphics to high-performance server deployments with headless operation.

## Communication & Community

### Preferred Channels

- **GitHub Issues**: Primary communication for bugs, features, and project coordination
- **Discord**: Join us at the [Balatro Discord](https://discord.com/channels/1116389027176787968/1391371948629426316) for real-time discussions

Happy contributing!
