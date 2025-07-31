# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Quick Start with Makefile

The project includes a comprehensive Makefile with all development workflows. Run `make help` to see all available commands:

```bash
# Show all available commands with descriptions
make help

# Quick development workflow (format + lint + typecheck)
make dev

# Complete workflow including tests
make all

# Install development dependencies
make install-dev
```

### Code Quality and Linting

```bash
make lint              # Check code with ruff linter
make lint-fix          # Auto-fix linting issues
make format            # Format code with ruff
make format-md         # Format markdown files
make typecheck         # Run type checker
make quality           # Run all quality checks
```

### Testing

```bash
make test              # Run tests with single instance (auto-starts if needed)
make test-parallel     # Run tests on 4 instances (auto-starts if needed)
make test-teardown     # Kill all Balatro instances
make test-verbose      # Run tests with verbose output
make coverage          # Generate coverage reports
```

**Testing Features:**

- **Auto-start**: Both `test` and `test-parallel` automatically start Balatro instances if not running
- **Parallel speedup**: `test-parallel` provides ~4x speedup with 4 workers
- **Instance management**: Tests keep instances running after completion
- **Port isolation**: Each worker uses its dedicated Balatro instance (ports 12346-12349)

**Usage:**

- `make test` - Simple single-instance testing (auto-handles everything)
- `make test-parallel` - Fast parallel testing (auto-handles everything)
- `make test-teardown` - Clean up when done testing

**Notes:**

- Monitor logs for each instance: `tail -f logs/balatro_12346.log`
- Logs are automatically created in the `logs/` directory with format `balatro_PORT.log`

### Documentation

```bash
make docs-serve        # Serve documentation locally
make docs-build        # Build documentation
make docs-clean        # Clean documentation build
```

### Build and Maintenance

```bash
make install           # Install package dependencies
make install-dev       # Install with development dependencies
make build             # Build package for distribution
make clean             # Clean all build artifacts and caches
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
