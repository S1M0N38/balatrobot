# Contributing to BalatroBot

Welcome to BalatroBot! We're excited that you're interested in contributing to this Python framework and Lua mod for creating automated bots to play Balatro.

BalatroBot uses a unique dual-architecture approach with a Python framework that communicates with a Lua mod running inside Balatro via TCP sockets. This allows for real-time bot automation and game state analysis.

## Project Status & Priorities

We track all development work using the [BalatroBot GitHub Project](https://github.com/users/S1M0N38/projects/7). This is the best place to see current priorities, ongoing work, and opportunities for contribution.

**Current Focus**: We're heavily refactoring the Python framework while focusing development efforts on the Lua API (`src/lua/api.lua`). The existing Python code serves as reference but will be drastically simplified in future versions.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Balatro**: Version 1.0.1o-FULL
- **SMODS (Steamodded)**: Version 1.0.0-beta-0711a or newer
- **Python**: 3.13+ (managed via uv)
- **uv**: Python package manager ([Installation Guide](https://docs.astral.sh/uv/))

### Recommended Tools

- **[DebugPlus](https://github.com/WilsontheWolf/DebugPlus)**: Essential for Lua API development and debugging

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

3. **Set Up Balatro with Mods**

    **macOS** (currently supported):

    ```bash
    ./balatro.sh > balatro.log 2>&1 & sleep 10 && echo 'Balatro started and ready'
    ```

    - **Linux**: We need a robust cross-platform script! Feel free to [open an issue](https://github.com/S1M0N38/balatrobot/issues/new) and contribute a Linux-compatible version.

    - **Windows**: Development on Windows is not currently supported.

!!! Tip

    Right now I'm using this [`balatro.sh`](https://gist.github.com/S1M0N38/4653c532bf048474100df3a270822bb4) script to start balatro with mods.

4. **Verify Game Setup**

    ```bash
    # Check if Balatro is running
    ps aux | grep -E "(Balatro\.app|balatro\.sh)" | grep -v grep

    # Monitor startup logs
    tail -n 100 balatro.log
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
    # or
    git checkout -b fix/issue-description
    ```

3. **Make Changes**

    - Follow our code style guidelines (see below)
    - Add tests for new functionality
    - Update documentation as needed

4. **Create Pull Request**

    - **Important**: Enable "Allow edits from maintainers" when creating your PR
    - Link to related issues
    - Provide clear description of changes
    - Include testing instructions

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
    All tests require Balatro to be running in the background.

```bash
# Start Balatro first
./balatro.sh > balatro.log 2>&1 & sleep 10

# Run all tests (stops on first failure)
pytest -x

# Run specific test file
pytest -x tests/lua/test_api_functions.py

# Run with verbose output
pytest -vx
```

**Test Suite Overview**:

- 102 tests covering API functions and TCP communication
- ~210 seconds execution time
- Tests game state transitions, socket communication, error handling

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

## Communication & Community

### Preferred Channels

- **GitHub Issues**: Primary communication for bugs, features, and project coordination
- **Discord**: Join us at the [Balatro Discord](https://discord.com/channels/1116389027176787968/1391371948629426316) for real-time discussions


---

## Questions?

- Check the [GitHub Project](https://github.com/users/S1M0N38/projects/7) for current priorities
- [Open an issue](https://github.com/S1M0N38/balatrobot/issues/new) for bugs or questions
- Join the [Discord discussion](https://discord.com/channels/1116389027176787968/1391371948629426316)

Happy contributing!

