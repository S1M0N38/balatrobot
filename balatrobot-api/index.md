# BalatroBot API

This page provides comprehensive API documentation for the BalatroBot Python framework. The API enables you to build automated bots that interact with the Balatro card game through a structured TCP communication protocol.

The API is organized into several key components: the `BalatroClient` for managing game connections and sending commands, enums that define game states and actions, exception classes for robust error handling, and data models that structure requests and responses between your bot and the game.

## Client

The `BalatroClient` is the main interface for communicating with the Balatro game through TCP connections. It handles connection management, message serialization, and error handling.

### `balatrobot.client.BalatroClient`

Client for communicating with the BalatroBot game API.

Attributes:

| Name          | Type     | Description                 |
| ------------- | -------- | --------------------------- |
| `host`        |          | Host address to connect to  |
| `port`        |          | Port number to connect to   |
| `timeout`     |          | Socket timeout in seconds   |
| `buffer_size` |          | Socket buffer size in bytes |
| `_socket`     | \`socket | None\`                      |

Source code in `src/balatrobot/client.py`

```python
class BalatroClient:
    """Client for communicating with the BalatroBot game API.

    Attributes:
        host: Host address to connect to
        port: Port number to connect to
        timeout: Socket timeout in seconds
        buffer_size: Socket buffer size in bytes
        _socket: Socket connection to BalatroBot
    """

    host = "127.0.0.1"
    port = 12346
    timeout = 10.0
    buffer_size = 65536

    def __init__(self):
        """Initialize BalatroBot client"""
        self._socket: socket.socket | None = None
        self._connected = False

    def __enter__(self) -> Self:
        """Enter context manager and connect to the game."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and disconnect from the game."""
        self.disconnect()

    def connect(self) -> None:
        """Connect to Balatro TCP server

        Raises:
            ConnectionFailedError: If not connected to the game
        """
        if self._connected:
            return

        logger.info(f"Connecting to BalatroBot API at {self.host}:{self.port}")
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_RCVBUF, self.buffer_size
            )
            self._socket.connect((self.host, self.port))
            self._connected = True
            logger.info(
                f"Successfully connected to BalatroBot API at {self.host}:{self.port}"
            )
        except (socket.error, OSError) as e:
            logger.error(f"Failed to connect to {self.host}:{self.port}: {e}")
            raise ConnectionFailedError(
                f"Failed to connect to {self.host}:{self.port}",
                error_code="E008",
                context={"host": self.host, "port": self.port, "error": str(e)},
            ) from e

    def disconnect(self) -> None:
        """Disconnect from the BalatroBot game API."""
        if self._socket:
            logger.info(f"Disconnecting from BalatroBot API at {self.host}:{self.port}")
            self._socket.close()
            self._socket = None
        self._connected = False

    def send_message(self, name: str, arguments: dict | None = None) -> dict:
        """Send JSON message to Balatro and receive response

        Args:
            name: Function name to call
            arguments: Function arguments

        Returns:
            Response from the game API

        Raises:
            ConnectionFailedError: If not connected to the game
            BalatroError: If the API returns an error
        """
        if arguments is None:
            arguments = {}

        if not self._connected or not self._socket:
            raise ConnectionFailedError(
                "Not connected to the game API",
                error_code="E008",
                context={
                    "connected": self._connected,
                    "socket": self._socket is not None,
                },
            )

        # Create and validate request
        request = APIRequest(name=name, arguments=arguments)
        logger.debug(f"Sending API request: {name}")

        try:
            # Send request
            message = request.model_dump_json() + "\n"
            self._socket.send(message.encode())

            # Receive response
            data = self._socket.recv(self.buffer_size)
            response_data = json.loads(data.decode().strip())

            # Check for error response
            if "error" in response_data:
                logger.error(f"API request {name} failed: {response_data.get('error')}")
                raise create_exception_from_error_response(response_data)

            logger.debug(f"API request {name} completed successfully")
            return response_data

        except socket.error as e:
            logger.error(f"Socket error during API request {name}: {e}")
            raise ConnectionFailedError(
                f"Socket error during communication: {e}",
                error_code="E008",
                context={"error": str(e)},
            ) from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from API request {name}: {e}")
            raise BalatroError(
                f"Invalid JSON response from game: {e}",
                error_code="E001",
                context={"error": str(e)},
            ) from e

```

#### `connect()`

Connect to Balatro TCP server

Raises:

| Type                    | Description                  |
| ----------------------- | ---------------------------- |
| `ConnectionFailedError` | If not connected to the game |

Source code in `src/balatrobot/client.py`

```python
def connect(self) -> None:
    """Connect to Balatro TCP server

    Raises:
        ConnectionFailedError: If not connected to the game
    """
    if self._connected:
        return

    logger.info(f"Connecting to BalatroBot API at {self.host}:{self.port}")
    try:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self.timeout)
        self._socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, self.buffer_size
        )
        self._socket.connect((self.host, self.port))
        self._connected = True
        logger.info(
            f"Successfully connected to BalatroBot API at {self.host}:{self.port}"
        )
    except (socket.error, OSError) as e:
        logger.error(f"Failed to connect to {self.host}:{self.port}: {e}")
        raise ConnectionFailedError(
            f"Failed to connect to {self.host}:{self.port}",
            error_code="E008",
            context={"host": self.host, "port": self.port, "error": str(e)},
        ) from e

```

#### `disconnect()`

Disconnect from the BalatroBot game API.

Source code in `src/balatrobot/client.py`

```python
def disconnect(self) -> None:
    """Disconnect from the BalatroBot game API."""
    if self._socket:
        logger.info(f"Disconnecting from BalatroBot API at {self.host}:{self.port}")
        self._socket.close()
        self._socket = None
    self._connected = False

```

#### `send_message(name, arguments=None)`

Send JSON message to Balatro and receive response

Parameters:

| Name        | Type   | Description           | Default            |
| ----------- | ------ | --------------------- | ------------------ |
| `name`      | `str`  | Function name to call | *required*         |
| `arguments` | \`dict | None\`                | Function arguments |

Returns:

| Type   | Description                |
| ------ | -------------------------- |
| `dict` | Response from the game API |

Raises:

| Type                    | Description                  |
| ----------------------- | ---------------------------- |
| `ConnectionFailedError` | If not connected to the game |
| `BalatroError`          | If the API returns an error  |

Source code in `src/balatrobot/client.py`

```python
def send_message(self, name: str, arguments: dict | None = None) -> dict:
    """Send JSON message to Balatro and receive response

    Args:
        name: Function name to call
        arguments: Function arguments

    Returns:
        Response from the game API

    Raises:
        ConnectionFailedError: If not connected to the game
        BalatroError: If the API returns an error
    """
    if arguments is None:
        arguments = {}

    if not self._connected or not self._socket:
        raise ConnectionFailedError(
            "Not connected to the game API",
            error_code="E008",
            context={
                "connected": self._connected,
                "socket": self._socket is not None,
            },
        )

    # Create and validate request
    request = APIRequest(name=name, arguments=arguments)
    logger.debug(f"Sending API request: {name}")

    try:
        # Send request
        message = request.model_dump_json() + "\n"
        self._socket.send(message.encode())

        # Receive response
        data = self._socket.recv(self.buffer_size)
        response_data = json.loads(data.decode().strip())

        # Check for error response
        if "error" in response_data:
            logger.error(f"API request {name} failed: {response_data.get('error')}")
            raise create_exception_from_error_response(response_data)

        logger.debug(f"API request {name} completed successfully")
        return response_data

    except socket.error as e:
        logger.error(f"Socket error during API request {name}: {e}")
        raise ConnectionFailedError(
            f"Socket error during communication: {e}",
            error_code="E008",
            context={"error": str(e)},
        ) from e
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from API request {name}: {e}")
        raise BalatroError(
            f"Invalid JSON response from game: {e}",
            error_code="E001",
            context={"error": str(e)},
        ) from e

```

______________________________________________________________________

## Enums

### `balatrobot.enums.State`

Game state values representing different phases of gameplay in Balatro, from menu navigation to active card play and shop interactions.

Source code in `src/balatrobot/enums.py`

```python
@unique
class State(Enum):
    """Game state values representing different phases of gameplay in Balatro,
    from menu navigation to active card play and shop interactions."""

    SELECTING_HAND = 1
    HAND_PLAYED = 2
    DRAW_TO_HAND = 3
    GAME_OVER = 4
    SHOP = 5
    PLAY_TAROT = 6
    BLIND_SELECT = 7
    ROUND_EVAL = 8
    TAROT_PACK = 9
    PLANET_PACK = 10
    MENU = 11
    TUTORIAL = 12
    SPLASH = 13
    SANDBOX = 14
    SPECTRAL_PACK = 15
    DEMO_CTA = 16
    STANDARD_PACK = 17
    BUFFOON_PACK = 18
    NEW_ROUND = 19

```

### `balatrobot.enums.Actions`

Bot action values corresponding to user interactions available in different game states, from card play to shop purchases and inventory management.

Source code in `src/balatrobot/enums.py`

```python
@unique
class Actions(Enum):
    """Bot action values corresponding to user interactions available in
    different game states, from card play to shop purchases and inventory
    management."""

    SELECT_BLIND = 1
    SKIP_BLIND = 2
    PLAY_HAND = 3
    DISCARD_HAND = 4
    END_SHOP = 5
    REROLL_SHOP = 6
    BUY_CARD = 7
    BUY_VOUCHER = 8
    BUY_BOOSTER = 9
    SELECT_BOOSTER_CARD = 10
    SKIP_BOOSTER_PACK = 11
    SELL_JOKER = 12
    USE_CONSUMABLE = 13
    SELL_CONSUMABLE = 14
    REARRANGE_JOKERS = 15
    REARRANGE_CONSUMABLES = 16
    REARRANGE_HAND = 17
    PASS = 18
    START_RUN = 19
    SEND_GAMESTATE = 20

```

### `balatrobot.enums.Decks`

Starting deck types in Balatro, each providing unique starting conditions, card modifications, or special abilities that affect gameplay throughout the run.

Source code in `src/balatrobot/enums.py`

```python
@unique
class Decks(Enum):
    """Starting deck types in Balatro, each providing unique starting
    conditions, card modifications, or special abilities that affect gameplay
    throughout the run."""

    RED = "Red Deck"
    BLUE = "Blue Deck"
    YELLOW = "Yellow Deck"
    GREEN = "Green Deck"
    BLACK = "Black Deck"
    MAGIC = "Magic Deck"
    NEBULA = "Nebula Deck"
    GHOST = "Ghost Deck"
    ABANDONED = "Abandoned Deck"
    CHECKERED = "Checkered Deck"
    ZODIAC = "Zodiac Deck"
    PAINTED = "Painted Deck"
    ANAGLYPH = "Anaglyph Deck"
    PLASMA = "Plasma Deck"
    ERRATIC = "Erratic Deck"

```

### `balatrobot.enums.Stakes`

Difficulty stake levels in Balatro that increase game difficulty through various modifiers and restrictions, with higher stakes providing greater challenges and rewards.

Source code in `src/balatrobot/enums.py`

```python
@unique
class Stakes(Enum):
    """Difficulty stake levels in Balatro that increase game difficulty through
    various modifiers and restrictions, with higher stakes providing greater
    challenges and rewards."""

    WHITE = 1
    RED = 2
    GREEN = 3
    BLACK = 4
    BLUE = 5
    PURPLE = 6
    ORANGE = 7
    GOLD = 8

```

### `balatrobot.enums.ErrorCode`

Standardized error codes used in BalatroBot API that match those defined in src/lua/api.lua for consistent error handling across the entire system.

Source code in `src/balatrobot/enums.py`

```python
@unique
class ErrorCode(Enum):
    """Standardized error codes used in BalatroBot API that match those defined in src/lua/api.lua for consistent error handling across the entire system."""

    # Protocol errors (E001-E005)
    INVALID_JSON = "E001"
    MISSING_NAME = "E002"
    MISSING_ARGUMENTS = "E003"
    UNKNOWN_FUNCTION = "E004"
    INVALID_ARGUMENTS = "E005"

    # Network errors (E006-E008)
    SOCKET_CREATE_FAILED = "E006"
    SOCKET_BIND_FAILED = "E007"
    CONNECTION_FAILED = "E008"

    # Validation errors (E009-E012)
    INVALID_GAME_STATE = "E009"
    INVALID_PARAMETER = "E010"
    PARAMETER_OUT_OF_RANGE = "E011"
    MISSING_GAME_OBJECT = "E012"

    # Game logic errors (E013-E016)
    DECK_NOT_FOUND = "E013"
    INVALID_CARD_INDEX = "E014"
    NO_DISCARDS_LEFT = "E015"
    INVALID_ACTION = "E016"

```

______________________________________________________________________

## Exceptions

### Connection and Socket Errors

#### `balatrobot.exceptions.SocketCreateFailedError`

Socket creation failed (E006).

#### `balatrobot.exceptions.SocketBindFailedError`

Socket bind failed (E007).

#### `balatrobot.exceptions.ConnectionFailedError`

Connection failed (E008).

### Game State and Logic Errors

#### `balatrobot.exceptions.InvalidGameStateError`

Invalid game state for requested action (E009).

#### `balatrobot.exceptions.InvalidActionError`

Invalid action for current context (E016).

#### `balatrobot.exceptions.DeckNotFoundError`

Deck not found (E013).

#### `balatrobot.exceptions.InvalidCardIndexError`

Invalid card index (E014).

#### `balatrobot.exceptions.NoDiscardsLeftError`

No discards remaining (E015).

### API and Parameter Errors

#### `balatrobot.exceptions.InvalidJSONError`

Invalid JSON in request (E001).

#### `balatrobot.exceptions.MissingNameError`

Message missing required 'name' field (E002).

#### `balatrobot.exceptions.MissingArgumentsError`

Message missing required 'arguments' field (E003).

#### `balatrobot.exceptions.UnknownFunctionError`

Unknown function name (E004).

#### `balatrobot.exceptions.InvalidArgumentsError`

Invalid arguments provided (E005).

#### `balatrobot.exceptions.InvalidParameterError`

Invalid or missing required parameter (E010).

#### `balatrobot.exceptions.ParameterOutOfRangeError`

Parameter value out of valid range (E011).

#### `balatrobot.exceptions.MissingGameObjectError`

Required game object missing (E012).

______________________________________________________________________

## Models

The BalatroBot API uses Pydantic models to provide type-safe data structures that exactly match the game's internal state representation. All models inherit from `BalatroBaseModel` which provides consistent validation and serialization.

#### Base Model

#### `balatrobot.models.BalatroBaseModel`

Base model for all BalatroBot API models.

### Request Models

These models define the structure for specific API requests:

#### `balatrobot.models.StartRunRequest`

Request model for starting a new run.

#### `balatrobot.models.BlindActionRequest`

Request model for skip or select blind actions.

#### `balatrobot.models.HandActionRequest`

Request model for playing hand or discarding cards.

#### `balatrobot.models.ShopActionRequest`

Request model for shop actions.

### Game State Models

The game state models provide comprehensive access to all Balatro game information, structured hierarchically to match the Lua API:

#### Root Game State

#### `balatrobot.models.G`

Root game state response matching G in Lua types.

##### `state_enum`

Get the state as an enum value.

##### `convert_empty_list_to_none_for_hand(v)`

Convert empty list to None for hand field.

#### Game Information

#### `balatrobot.models.GGame`

Game state matching GGame in Lua types.

##### `convert_empty_list_to_dict(v)`

Convert empty list to empty dict.

##### `convert_empty_list_to_none(v)`

Convert empty list to None for optional nested objects.

#### `balatrobot.models.GGameCurrentRound`

Current round info matching GGameCurrentRound in Lua types.

##### `convert_empty_list_to_dict(v)`

Convert empty list to empty dict.

#### `balatrobot.models.GGameLastBlind`

Last blind info matching GGameLastBlind in Lua types.

#### `balatrobot.models.GGamePreviousRound`

Previous round info matching GGamePreviousRound in Lua types.

#### `balatrobot.models.GGameProbabilities`

Game probabilities matching GGameProbabilities in Lua types.

#### `balatrobot.models.GGamePseudorandom`

Pseudorandom data matching GGamePseudorandom in Lua types.

#### `balatrobot.models.GGameRoundBonus`

Round bonus matching GGameRoundBonus in Lua types.

#### `balatrobot.models.GGameRoundScores`

Round scores matching GGameRoundScores in Lua types.

#### `balatrobot.models.GGameSelectedBack`

Selected deck info matching GGameSelectedBack in Lua types.

#### `balatrobot.models.GGameShop`

Shop configuration matching GGameShop in Lua types.

#### `balatrobot.models.GGameStartingParams`

Starting parameters matching GGameStartingParams in Lua types.

#### `balatrobot.models.GGameTags`

Game tags model matching GGameTags in Lua types.

#### Hand Management

#### `balatrobot.models.GHand`

Hand structure matching GHand in Lua types.

#### `balatrobot.models.GHandCards`

Hand card matching GHandCards in Lua types.

#### `balatrobot.models.GHandCardsBase`

Hand card base properties matching GHandCardsBase in Lua types.

##### `convert_int_to_string(v)`

Convert integer values to strings.

#### `balatrobot.models.GHandCardsConfig`

Hand card configuration matching GHandCardsConfig in Lua types.

#### `balatrobot.models.GHandCardsConfigCard`

Hand card config card data matching GHandCardsConfigCard in Lua types.

#### `balatrobot.models.GHandConfig`

Hand configuration matching GHandConfig in Lua types.

#### Joker Information

#### `balatrobot.models.GJokersCards`

Joker card matching GJokersCards in Lua types.

#### `balatrobot.models.GJokersCardsConfig`

Joker card configuration matching GJokersCardsConfig in Lua types.

### Communication Models

These models handle the communication protocol between your bot and the game:

#### `balatrobot.models.APIRequest`

Model for API requests sent to the game.

#### `balatrobot.models.APIResponse`

Model for API responses from the game.

#### `balatrobot.models.ErrorResponse`

Model for API error responses matching Lua ErrorResponse.

#### `balatrobot.models.JSONLLogEntry`

Model for JSONL log entries that record game actions.

## Usage Examples

For practical implementation examples:

- Follow the [Developing Bots](../developing-bots/) guide for complete bot setup
- Understand the underlying [Protocol API](../protocol-api/) for advanced usage
- Reference the [Installation](../installation/) guide for environment setup
