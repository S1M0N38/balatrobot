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

**IMPORTANT**: Tests require Balatro to be running in the background. Use `./balatro.sh --status` to check if the game is running.

```bash
# Run all tests (requires Balatro to be running) - stops after first failure
pytest

# Run specific test file - stops after first failure
pytest tests/lua/test_api_functions.py

# Run tests with verbose output - stops after first failure
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
    pytest -n 4 --port 12346 --port 12347 tests/lua/

    # Four workers (maximum parallelization)
    pytest -n 4 --port 12346 --port 12347 --port 12348 --port 12349 tests/lua/
    ```

**Benefits:**

- **Faster test execution**: ~4x speedup with 4 parallel workers
- **Port isolation**: Each worker uses its dedicated Balatro instance

**Notes:**

- Each Balatro instance must be running on a different port before starting tests
- Tests automatically distribute across available workers
- Monitor logs for each instance: `tail -f logs/balatro_12346.log`
- Logs are automatically created in the `logs/` directory with format `balatro_PORT.log`

#### Test Prerequisites and Workflow

0. **Check existing instances first**:

```bash
# Check if Balatro instances are already running
./balatro.sh --status

# If instances are running on needed ports, you can proceed with testing
# If you need to kill all running instances and start fresh:
./balatro.sh --kill
```

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

- **BalatroClient** (`client.py`): TCP client for communicating with game API via JSON messages
- **Type-Safe Models** (`models.py`): Pydantic models matching Lua game state structure (G, GGame, GHand, etc.)
- **Enums** (`enums.py`): Game state enums (Actions, Decks, Stakes, State, ErrorCode)
- **Exception Hierarchy** (`exceptions.py`): Structured error handling with game-specific exceptions
- **API Communication**: JSON request/response protocol with timeout handling and error recovery

## Development Standards

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
