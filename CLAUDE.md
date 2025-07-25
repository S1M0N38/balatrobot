# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Linting and Type Checking

```bash
# Run ruff linter and formatter
ruff check .
ruff check --select I --fix .
ruff format .

# Run markdown formatter
mdformat --number docs/index.md docs/installation.md docs/developing-bots.md docs/protocol-api.md docs/contributing.md README.md

# Run type checker
basedpyright
```

### Testing

**IMPORTANT**: Tests require Balatro to be running in the background. Always start the game before running tests.

```bash
# Run all tests (requires Balatro to be running) - stops after first failure
pytest -x

# Run specific test file - stops after first failure
pytest -x tests/lua/test_api_functions.py

# Run tests with verbose output - stops after first failure
pytest -vx
```

#### Test Prerequisites and Workflow

1. **Always start Balatro first**:

  ```bash
  # Check if game is running
  ps aux | grep -E "(Balatro\.app|balatro\.sh)" | grep -v grep

  # Start if not running
  ./balatro.sh > balatro.log 2>&1 & sleep 10 && echo 'Balatro started and ready'
  ```

2. **Monitor game startup**:

  ```bash
  # Check logs for successful mod loading
  tail -n 100 balatro.log

  # Look for these success indicators:
  # - "BalatrobotAPI initialized"
  # - "BalatroBot loaded - version X.X.X"
  # - "TCP socket created on port 12346"
  ```

3. **Common startup issues and fixes**:

  - **Game crashes on mod load**: Review full log for Lua stack traces
  - **Steam connection warnings**: Can be ignored - game works without Steam in development
  - **JSON metadata errors**: Normal for development files (.vscode, .luarc.json) - can be ignored

4. **Test execution**:

  - **Test suite**: 102 tests covering API functions and TCP communication
  - **Execution time**: ~210 seconds (includes game state transitions)
  - **Coverage**: API function calls, socket communication, error handling, edge cases

5. **Troubleshooting test failures**:

  - **Connection timeouts**: Ensure TCP port 12346 is available
  - **Game state errors**: Check if game is responsive and not crashed
  - **Invalid responses**: Verify mod loaded correctly by checking logs
  - **If test/s fail for timeout the reasons is that Balatro crash because there was an error in the Balatro mod (i.e. @balatrobot.lua and @src/lua/ ). The error should be logged in the `balatro.log` file.**
  - **Balatro app crashes**: When the Balatro app crashes during testing, **do not run the remaining tests**. The crash usually indicates an issue with the Lua mod code that causes cryptic errors in `balatro.log`. Stop test execution and investigate the crash logs before continuing. Before running the tests again, ALWAYS kill the current Balatro instance running and start it again.

### Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## Architecture Overview

BalatroBot is a Python framework for developing automated bots to play the card game Balatro. The architecture consists of three main layers:

### 1. Communication Layer (TCP Protocol)

- **Lua API** (`src/lua/api.lua`): Game-side mod that handles socket communication
- **TCP Socket Communication**: Real-time bidirectional communication between game and bot
- **Protocol**: Bot sends "HELLO" → Game responds with JSON state → Bot sends action strings

### 2. Python Framework Layer (`src/balatrobot/`)

**NOTE**: This is the old implementation that is being heavily refactored without backwards compatibility.
It will be drastically simplified in the future. For the moment I'm just focusing on the Lua API (`src/lua/api.lua`).
I keep the old code around for reference.

- **Bot Base Class** (`base.py`): Abstract base class defining the bot interface
- **ActionSchema**: TypedDict defining structured action format with `action` (enum) and `args` (list)
- **Enums** (`enums.py`): Game state enums (Actions, Decks, Stakes, State)
- **Socket Management**: Automatic reconnection, timeout handling, JSON parsing

## Development Standards

### Python Code Style (from `.cursor/rules/`)

- Use modern Python 3.13+ syntax with built-in collection types
- Type annotations with pipe operator for unions: `str | int | None`
- Use `type` statement for type aliases
- Google-style docstrings without type information (since type annotations are present)
- Modern generic class syntax: `class Container[T]:`

## Project Structure Context

- **Dual Implementation**: Both Python framework and Lua game mod
- **TCP Communication**: Port 12346 for real-time game interaction
- **MkDocs Documentation**: Comprehensive guides with Material theme
- **Pytest Testing**: TCP socket testing with fixtures
- **Development Tools**: Ruff, basedpyright, modern Python tooling

### Testing Best Practices

- **Always check that Balatro is running before running tests**
- After starting Balatro, check the `balatro.log` to confirm successful startup
