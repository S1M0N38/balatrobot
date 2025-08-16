"""Main BalatroBot client for communicating with the game."""

import json
import logging
import socket
from typing import Self

from .exceptions import (
    BalatroError,
    ConnectionFailedError,
    create_exception_from_error_response,
)
from .models import APIRequest

logger = logging.getLogger(__name__)


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
    timeout = 30.0
    buffer_size = 65536

    def __init__(self, port: int = 12346):
        """Initialize BalatroBot client

        Args:
            port: Port number to connect to (default: 12346)
        """
        self.port = port
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

    # Checkpoint Management Methods

    def save_checkpoint(self, checkpoint_name: str | None = None) -> dict:
        """Save current game state as a checkpoint.

        Args:
            checkpoint_name: Optional name for the checkpoint.
                           If not provided, timestamp will be used.

        Returns:
            Dictionary containing checkpoint details including name and metadata

        Raises:
            BalatroError: If no active game or save fails
        """
        args = {}
        if checkpoint_name:
            args["checkpoint_name"] = checkpoint_name

        response = self.send_message("save_checkpoint", args)
        logger.info(f"Checkpoint saved: {response.get('checkpoint_name')}")
        return response

    def load_checkpoint(self, checkpoint_name: str, mode: str = "restart") -> dict:
        """Load game state from a checkpoint.

        Args:
            checkpoint_name: Name of the checkpoint to load
            mode: Load mode - "restart" (full game restart),
                            "overwrite" (just update save file),
                            "resume" (experimental partial restore)

        Returns:
            Dictionary containing success status and loaded game info

        Raises:
            BalatroError: If checkpoint not found or load fails
        """
        response = self.send_message(
            "load_checkpoint", {"checkpoint_name": checkpoint_name, "mode": mode}
        )
        logger.info(f"Checkpoint loaded: {checkpoint_name} (mode: {mode})")
        return response

    def list_checkpoints(self) -> list[dict]:
        """List all available checkpoints.

        Returns:
            List of checkpoint metadata dictionaries sorted by creation time

        Raises:
            BalatroError: If listing fails
        """
        response = self.send_message("list_checkpoints")
        return response.get("checkpoints", [])

    def delete_checkpoint(self, checkpoint_name: str) -> dict:
        """Delete a checkpoint.

        Args:
            checkpoint_name: Name of the checkpoint to delete

        Returns:
            Dictionary with success status and deleted checkpoint name

        Raises:
            BalatroError: If checkpoint not found or deletion fails
        """
        response = self.send_message(
            "delete_checkpoint", {"checkpoint_name": checkpoint_name}
        )
        logger.info(f"Checkpoint deleted: {checkpoint_name}")
        return response

    def export_checkpoint(self, checkpoint_name: str) -> dict:
        """Export checkpoint data as base64 for external storage.

        Args:
            checkpoint_name: Name of the checkpoint to export

        Returns:
            Dictionary with checkpoint_name, base64 data, and metadata

        Raises:
            BalatroError: If checkpoint not found or export fails
        """
        response = self.send_message(
            "export_checkpoint", {"checkpoint_name": checkpoint_name}
        )
        logger.info(f"Checkpoint exported: {checkpoint_name}")
        return response

    def import_checkpoint(
        self, checkpoint_name: str, data: str, metadata: dict | None = None
    ) -> dict:
        """Import checkpoint data from base64.

        Args:
            checkpoint_name: Name for the imported checkpoint
            data: Base64 encoded checkpoint data
            metadata: Optional metadata dictionary

        Returns:
            Dictionary with success status

        Raises:
            BalatroError: If import fails
        """
        args = {"checkpoint_name": checkpoint_name, "data": data}
        if metadata:
            args["metadata"] = metadata

        response = self.send_message("import_checkpoint", args)
        logger.info(f"Checkpoint imported: {checkpoint_name}")
        return response

    def set_profile_save(
        self, checkpoint_name: str, profile: str | None = None
    ) -> dict:
        """Set the profile's save file to a checkpoint without restarting.

        This overwrites the save file so the checkpoint will be loaded
        on next game start or continue.

        Args:
            checkpoint_name: Name of the checkpoint to use
            profile: Target profile (default: current profile)

        Returns:
            Dictionary with success status and message

        Raises:
            BalatroError: If checkpoint not found or operation fails
        """
        args = {"checkpoint_name": checkpoint_name}
        if profile:
            args["profile"] = profile

        response = self.send_message("set_profile_save", args)
        logger.info(
            f"Profile save set to checkpoint: {checkpoint_name} "
            f"(profile: {profile or 'current'})"
        )
        return response
