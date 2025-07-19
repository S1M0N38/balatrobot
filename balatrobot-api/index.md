# BalatroBot API

This page provides comprehensive API documentation for the BalatroBot Python framework. The API enables you to build automated bots that interact with the Balatro card game through a structured TCP communication protocol.

The API is organized into several key components: the `BalatroClient` for managing game connections and sending commands, enums that define game states and actions, exception classes for robust error handling, and data models that structure requests and responses between your bot and the game.

## Client

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
 18class BalatroClient:
 19    """Client for communicating with the BalatroBot game API.
 20
 21    Attributes:
 22        host: Host address to connect to
 23        port: Port number to connect to
 24        timeout: Socket timeout in seconds
 25        buffer_size: Socket buffer size in bytes
 26        _socket: Socket connection to BalatroBot
 27    """
 28
 29    host = "127.0.0.1"
 30    port = 12346
 31    timeout = 10.0
 32    buffer_size = 65536
 33
 34    def __init__(self):
 35        """Initialize BalatroBot client"""
 36        self._socket: socket.socket | None = None
 37        self._connected = False
 38
 39    def __enter__(self) -> Self:
 40        """Enter context manager and connect to the game."""
 41        self.connect()
 42        return self
 43
 44    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
 45        """Exit context manager and disconnect from the game."""
 46        self.disconnect()
 47
 48    def connect(self) -> None:
 49        """Connect to Balatro TCP server
 50
 51        Raises:
 52            ConnectionFailedError: If not connected to the game
 53        """
 54        if self._connected:
 55            return
 56
 57        logger.info(f"Connecting to BalatroBot API at {self.host}:{self.port}")
 58        try:
 59            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 60            self._socket.settimeout(self.timeout)
 61            self._socket.setsockopt(
 62                socket.SOL_SOCKET, socket.SO_RCVBUF, self.buffer_size
 63            )
 64            self._socket.connect((self.host, self.port))
 65            self._connected = True
 66            logger.info(
 67                f"Successfully connected to BalatroBot API at {self.host}:{self.port}"
 68            )
 69        except (socket.error, OSError) as e:
 70            logger.error(f"Failed to connect to {self.host}:{self.port}: {e}")
 71            raise ConnectionFailedError(
 72                f"Failed to connect to {self.host}:{self.port}",
 73                error_code="E008",
 74                context={"host": self.host, "port": self.port, "error": str(e)},
 75            ) from e
 76
 77    def disconnect(self) -> None:
 78        """Disconnect from the BalatroBot game API."""
 79        if self._socket:
 80            logger.info(f"Disconnecting from BalatroBot API at {self.host}:{self.port}")
 81            self._socket.close()
 82            self._socket = None
 83        self._connected = False
 84
 85    def send_message(self, name: str, arguments: dict | None = None) -> dict:
 86        """Send JSON message to Balatro and receive response
 87
 88        Args:
 89            name: Function name to call
 90            arguments: Function arguments
 91
 92        Returns:
 93            Response from the game API
 94
 95        Raises:
 96            ConnectionFailedError: If not connected to the game
 97            BalatroError: If the API returns an error
 98        """
 99        if arguments is None:
100            arguments = {}
101
102        if not self._connected or not self._socket:
103            raise ConnectionFailedError(
104                "Not connected to the game API",
105                error_code="E008",
106                context={
107                    "connected": self._connected,
108                    "socket": self._socket is not None,
109                },
110            )
111
112        # Create and validate request
113        request = APIRequest(name=name, arguments=arguments)
114        logger.debug(f"Sending API request: {name}")
115
116        try:
117            # Send request
118            message = request.model_dump_json() + "\n"
119            self._socket.send(message.encode())
120
121            # Receive response
122            data = self._socket.recv(self.buffer_size)
123            response_data = json.loads(data.decode().strip())
124
125            # Check for error response
126            if "error" in response_data:
127                logger.error(f"API request {name} failed: {response_data.get('error')}")
128                raise create_exception_from_error_response(response_data)
129
130            logger.debug(f"API request {name} completed successfully")
131            return response_data
132
133        except socket.error as e:
134            logger.error(f"Socket error during API request {name}: {e}")
135            raise ConnectionFailedError(
136                f"Socket error during communication: {e}",
137                error_code="E008",
138                context={"error": str(e)},
139            ) from e
140        except json.JSONDecodeError as e:
141            logger.error(f"Invalid JSON response from API request {name}: {e}")
142            raise BalatroError(
143                f"Invalid JSON response from game: {e}",
144                error_code="E001",
145                context={"error": str(e)},
146            ) from e

```

#### `connect()`

Connect to Balatro TCP server

Raises:

| Type                    | Description                  |
| ----------------------- | ---------------------------- |
| `ConnectionFailedError` | If not connected to the game |

Source code in `src/balatrobot/client.py`

```python
48def connect(self) -> None:
49    """Connect to Balatro TCP server
50
51    Raises:
52        ConnectionFailedError: If not connected to the game
53    """
54    if self._connected:
55        return
56
57    logger.info(f"Connecting to BalatroBot API at {self.host}:{self.port}")
58    try:
59        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
60        self._socket.settimeout(self.timeout)
61        self._socket.setsockopt(
62            socket.SOL_SOCKET, socket.SO_RCVBUF, self.buffer_size
63        )
64        self._socket.connect((self.host, self.port))
65        self._connected = True
66        logger.info(
67            f"Successfully connected to BalatroBot API at {self.host}:{self.port}"
68        )
69    except (socket.error, OSError) as e:
70        logger.error(f"Failed to connect to {self.host}:{self.port}: {e}")
71        raise ConnectionFailedError(
72            f"Failed to connect to {self.host}:{self.port}",
73            error_code="E008",
74            context={"host": self.host, "port": self.port, "error": str(e)},
75        ) from e

```

#### `disconnect()`

Disconnect from the BalatroBot game API.

Source code in `src/balatrobot/client.py`

```python
77def disconnect(self) -> None:
78    """Disconnect from the BalatroBot game API."""
79    if self._socket:
80        logger.info(f"Disconnecting from BalatroBot API at {self.host}:{self.port}")
81        self._socket.close()
82        self._socket = None
83    self._connected = False

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
 85def send_message(self, name: str, arguments: dict | None = None) -> dict:
 86    """Send JSON message to Balatro and receive response
 87
 88    Args:
 89        name: Function name to call
 90        arguments: Function arguments
 91
 92    Returns:
 93        Response from the game API
 94
 95    Raises:
 96        ConnectionFailedError: If not connected to the game
 97        BalatroError: If the API returns an error
 98    """
 99    if arguments is None:
100        arguments = {}
101
102    if not self._connected or not self._socket:
103        raise ConnectionFailedError(
104            "Not connected to the game API",
105            error_code="E008",
106            context={
107                "connected": self._connected,
108                "socket": self._socket is not None,
109            },
110        )
111
112    # Create and validate request
113    request = APIRequest(name=name, arguments=arguments)
114    logger.debug(f"Sending API request: {name}")
115
116    try:
117        # Send request
118        message = request.model_dump_json() + "\n"
119        self._socket.send(message.encode())
120
121        # Receive response
122        data = self._socket.recv(self.buffer_size)
123        response_data = json.loads(data.decode().strip())
124
125        # Check for error response
126        if "error" in response_data:
127            logger.error(f"API request {name} failed: {response_data.get('error')}")
128            raise create_exception_from_error_response(response_data)
129
130        logger.debug(f"API request {name} completed successfully")
131        return response_data
132
133    except socket.error as e:
134        logger.error(f"Socket error during API request {name}: {e}")
135        raise ConnectionFailedError(
136            f"Socket error during communication: {e}",
137            error_code="E008",
138            context={"error": str(e)},
139        ) from e
140    except json.JSONDecodeError as e:
141        logger.error(f"Invalid JSON response from API request {name}: {e}")
142        raise BalatroError(
143            f"Invalid JSON response from game: {e}",
144            error_code="E001",
145            context={"error": str(e)},
146        ) from e

```

______________________________________________________________________

## Enums

### `balatrobot.enums.State`

Game state values representing different phases of gameplay in Balatro, from menu navigation to active card play and shop interactions.

Source code in `src/balatrobot/enums.py`

```python
 4@unique
 5class State(Enum):
 6    """Game state values representing different phases of gameplay in Balatro,
 7    from menu navigation to active card play and shop interactions."""
 8
 9    SELECTING_HAND = 1
10    HAND_PLAYED = 2
11    DRAW_TO_HAND = 3
12    GAME_OVER = 4
13    SHOP = 5
14    PLAY_TAROT = 6
15    BLIND_SELECT = 7
16    ROUND_EVAL = 8
17    TAROT_PACK = 9
18    PLANET_PACK = 10
19    MENU = 11
20    TUTORIAL = 12
21    SPLASH = 13
22    SANDBOX = 14
23    SPECTRAL_PACK = 15
24    DEMO_CTA = 16
25    STANDARD_PACK = 17
26    BUFFOON_PACK = 18
27    NEW_ROUND = 19

```

### `balatrobot.enums.Actions`

Bot action values corresponding to user interactions available in different game states, from card play to shop purchases and inventory management.

Source code in `src/balatrobot/enums.py`

```python
30@unique
31class Actions(Enum):
32    """Bot action values corresponding to user interactions available in
33    different game states, from card play to shop purchases and inventory
34    management."""
35
36    SELECT_BLIND = 1
37    SKIP_BLIND = 2
38    PLAY_HAND = 3
39    DISCARD_HAND = 4
40    END_SHOP = 5
41    REROLL_SHOP = 6
42    BUY_CARD = 7
43    BUY_VOUCHER = 8
44    BUY_BOOSTER = 9
45    SELECT_BOOSTER_CARD = 10
46    SKIP_BOOSTER_PACK = 11
47    SELL_JOKER = 12
48    USE_CONSUMABLE = 13
49    SELL_CONSUMABLE = 14
50    REARRANGE_JOKERS = 15
51    REARRANGE_CONSUMABLES = 16
52    REARRANGE_HAND = 17
53    PASS = 18
54    START_RUN = 19
55    SEND_GAMESTATE = 20

```

### `balatrobot.enums.Decks`

Starting deck types in Balatro, each providing unique starting conditions, card modifications, or special abilities that affect gameplay throughout the run.

Source code in `src/balatrobot/enums.py`

```python
58@unique
59class Decks(Enum):
60    """Starting deck types in Balatro, each providing unique starting
61    conditions, card modifications, or special abilities that affect gameplay
62    throughout the run."""
63
64    RED = "Red Deck"
65    BLUE = "Blue Deck"
66    YELLOW = "Yellow Deck"
67    GREEN = "Green Deck"
68    BLACK = "Black Deck"
69    MAGIC = "Magic Deck"
70    NEBULA = "Nebula Deck"
71    GHOST = "Ghost Deck"
72    ABANDONED = "Abandoned Deck"
73    CHECKERED = "Checkered Deck"
74    ZODIAC = "Zodiac Deck"
75    PAINTED = "Painted Deck"
76    ANAGLYPH = "Anaglyph Deck"
77    PLASMA = "Plasma Deck"
78    ERRATIC = "Erratic Deck"

```

### `balatrobot.enums.Stakes`

Difficulty stake levels in Balatro that increase game difficulty through various modifiers and restrictions, with higher stakes providing greater challenges and rewards.

Source code in `src/balatrobot/enums.py`

```python
81@unique
82class Stakes(Enum):
83    """Difficulty stake levels in Balatro that increase game difficulty through
84    various modifiers and restrictions, with higher stakes providing greater
85    challenges and rewards."""
86
87    WHITE = 1
88    RED = 2
89    GREEN = 3
90    BLACK = 4
91    BLUE = 5
92    PURPLE = 6
93    ORANGE = 7
94    GOLD = 8

```

### `balatrobot.enums.ErrorCode`

Standardized error codes used in BalatroBot API that match those defined in src/lua/api.lua for consistent error handling across the entire system.

Source code in `src/balatrobot/enums.py`

```python
 97@unique
 98class ErrorCode(Enum):
 99    """Standardized error codes used in BalatroBot API that match those defined in src/lua/api.lua for consistent error handling across the entire system."""
100
101    # Protocol errors (E001-E005)
102    INVALID_JSON = "E001"
103    MISSING_NAME = "E002"
104    MISSING_ARGUMENTS = "E003"
105    UNKNOWN_FUNCTION = "E004"
106    INVALID_ARGUMENTS = "E005"
107
108    # Network errors (E006-E008)
109    SOCKET_CREATE_FAILED = "E006"
110    SOCKET_BIND_FAILED = "E007"
111    CONNECTION_FAILED = "E008"
112
113    # Validation errors (E009-E012)
114    INVALID_GAME_STATE = "E009"
115    INVALID_PARAMETER = "E010"
116    PARAMETER_OUT_OF_RANGE = "E011"
117    MISSING_GAME_OBJECT = "E012"
118
119    # Game logic errors (E013-E016)
120    DECK_NOT_FOUND = "E013"
121    INVALID_CARD_INDEX = "E014"
122    NO_DISCARDS_LEFT = "E015"
123    INVALID_ACTION = "E016"

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

### Request Models

#### `balatrobot.models.StartRunRequest`

Request model for starting a new run.

#### `balatrobot.models.BlindActionRequest`

Request model for skip or select blind actions.

#### `balatrobot.models.HandActionRequest`

Request model for playing hand or discarding cards.

#### `balatrobot.models.ShopActionRequest`

Request model for shop actions.

### Game State Models

#### `balatrobot.models.Card`

Model for a playing card.

#### `balatrobot.models.Game`

Model for game information.

#### `balatrobot.models.GameState`

Model for the complete game state.

##### `state_enum` `property`

Get the state as an enum value.

### Communication Models

#### `balatrobot.models.ErrorResponse`

Model for API error responses.

#### `balatrobot.models.APIRequest`

Model for API requests sent to the game.

#### `balatrobot.models.APIResponse`

Model for API responses from the game.

## Usage Examples

For practical implementation examples:

- Follow the [Developing Bots](../developing-bots/) guide for complete bot setup
- Understand the underlying [Protocol API](../protocol-api/) for advanced usage
- Reference the [Installation](../installation/) guide for environment setup
