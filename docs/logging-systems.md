# Logging Systems

BalatroBot implements three distinct logging systems to support different aspects of development, debugging, and analysis:

1. [**JSONL Run Logging**](#jsonl-run-logging) - Records complete game runs for replay and analysis
2. [**Python SDK Logging**](#python-sdk-logging) - Future logging capabilities for the Python framework
3. [**Mod Logging**](#mod-logging) - Traditional streamodded logging for mod development and debugging

## JSONL Run Logging

The run logging system records complete game runs as JSONL (JSON Lines) files. Each line represents a single game action with its parameters, timestamp, and game state **before** the action.

The system hooks into these game functions:

- `start_run`: begins a new game run
- `skip_or_select_blind`: blind selection actions
- `play_hand_or_discard`: card play actions
- `cash_out`: end blind and collect rewards
- `shop`: shop interactions
- `go_to_menu`: return to main menu

The JSONL files are automatically created when:

- **Playing manually**: Starting a new run through the game interface
- **Using the API**: Interacting with the game through the TCP API

Files are saved as: `{mod_path}/runs/YYYYMMDDTHHMMSS.jsonl`

!!! tip "Replay runs"

    The JSONL logs enable complete run replay for testing and analysis.

    ```python
    state = load_jsonl_run("20250714T145700.jsonl")
    for step in state:
        send_and_receive_api_message(
            tcp_client,
            step["function"]["name"],
            step["function"]["arguments"]
        )
    ```

Examples for runs can be found in the [test suite](https://github.com/S1M0N38/balatrobot/tree/main/tests/runs).

### Format Specification

Each log entry follows this structure:

```json
{
  "timestamp_ms": int,
  "function": {
    "name": "...",
    "arguments": {...}
  },
  "game_state": { ... }
}
```

- **`timestamp_ms`**: Unix timestamp in milliseconds when the action occurred
- **`function`**: The game function that was called
    - `name`: Function name (e.g., "start_run", "play_hand_or_discard", "cash_out")
    - `arguments`: Arguments passed to the function
- **`game_state`**: Complete game state **before** the function execution

## Python SDK Logging

The Python SDK (`src/balatrobot/`) implements structured logging for bot development and debugging. The logging system provides visibility into client operations, API communications, and error handling.

### What Gets Logged

The `BalatroClient` logs the following operations:

- **Connection events**: When connecting to and disconnecting from the game API
- **API requests**: Function names being called and their completion status
- **Errors**: Connection failures, socket errors, and invalid API responses

### Configuration Example

The SDK uses Python's built-in `logging` module. Configure it in your bot code before using the client:

```python
import logging
from balatrobot import BalatroClient

# Configure logging
log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler('balatrobot.log')
file_handler.setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[console_handler, file_handler]
)

# Use the client
with BalatroClient() as client:
    state = client.get_game_state()
    client.start_run(deck="Red Deck", stake=1)
```

## Mod Logging

BalatroBot uses Steamodded's built-in logging system for mod development and debugging.

- **Traditional logging**: Standard log levels (DEBUG, INFO, WARNING, ERROR)
- **Development focus**: Primarily for debugging mod functionality
- **Console output**: Displays in game console and log files

```lua
-- Available through Steamodded
sendDebugMessage("This is a debug message")
sendInfoMessage("This is an info message")
sendWarningMessage("This is a warning message")
sendErrorMessage("This is an error message")
```
