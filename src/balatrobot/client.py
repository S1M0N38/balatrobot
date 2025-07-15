"""Main BalatroBot client for communicating with the game."""

import json
import logging
import socket
from typing import Any, Literal, Self

from .exceptions import (
    BalatroError,
    ConnectionFailedError,
    create_exception_from_error_response,
)
from .models import (
    APIRequest,
    BlindActionRequest,
    GameState,
    HandActionRequest,
    ShopActionRequest,
    StartRunRequest,
)

logger = logging.getLogger(__name__)


class BalatroClient:
    """Client for communicating with the BalatroBot game API."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 12346,
        timeout: float = 10.0,
        buffer_size: int = 65536,
    ) -> None:
        """Initialize the BalatroBot client.

        Args:
            host: Host address to connect to
            port: Port number to connect to
            timeout: Socket timeout in seconds
            buffer_size: Socket buffer size in bytes
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.buffer_size = buffer_size
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
        """Connect to the BalatroBot game API."""
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

    def _send_request(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Send a request to the game API and return the response.

        Args:
            name: Function name to call
            arguments: Function arguments

        Returns:
            Response from the game API

        Raises:
            ConnectionFailedError: If not connected to the game
            BalatroError: If the API returns an error
        """
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

    def get_game_state(self) -> GameState:
        """Get the current game state.

        Returns:
            Current game state
        """
        response = self._send_request("get_game_state", {})
        return GameState.model_validate(response)

    def go_to_menu(self) -> GameState:
        """Navigate to the main menu.

        Returns:
            Game state after navigation
        """
        response = self._send_request("go_to_menu", {})
        return GameState.model_validate(response)

    def start_run(
        self,
        deck: str,
        stake: int = 1,
        seed: str | None = None,
        challenge: str | None = None,
    ) -> GameState:
        """Start a new game run.

        Args:
            deck: Name of the deck to use
            stake: Stake level (1-8)
            seed: Optional seed for the run
            challenge: Optional challenge name

        Returns:
            Game state after starting the run
        """
        request = StartRunRequest(
            deck=deck,
            stake=stake,
            seed=seed,
            challenge=challenge,
        )
        if request.seed is None:
            logger.warning(
                "Seed not provided, using random seed. This run cannot be replayed."
            )
        response = self._send_request("start_run", request.model_dump())
        return GameState.model_validate(response)

    def skip_or_select_blind(self, action: Literal["skip", "select"]) -> GameState:
        """Skip or select the current blind.

        Args:
            action: Either "skip" or "select"

        Returns:
            Game state after the action
        """
        request = BlindActionRequest(action=action)
        response = self._send_request("skip_or_select_blind", request.model_dump())
        return GameState.model_validate(response)

    def play_hand_or_discard(
        self, action: Literal["play_hand", "discard"], cards: list[int]
    ) -> GameState:
        """Play selected cards or discard them.

        Args:
            action: Either "play_hand" or "discard"
            cards: List of card indices (0-indexed)

        Returns:
            Game state after the action
        """
        request = HandActionRequest(action=action, cards=cards)
        response = self._send_request("play_hand_or_discard", request.model_dump())
        return GameState.model_validate(response)

    def cash_out(self) -> GameState:
        """Cash out from the current round to enter the shop.

        Returns:
            Game state after cashing out
        """
        response = self._send_request("cash_out", {})
        return GameState.model_validate(response)

    def shop(self, action: Literal["next_round"]) -> GameState:
        """Perform a shop action.

        Args:
            action: Shop action to perform (currently only "next_round")

        Returns:
            Game state after the action
        """
        request = ShopActionRequest(action=action)
        response = self._send_request("shop", request.model_dump())
        return GameState.model_validate(response)
