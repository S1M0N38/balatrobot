"""Main BalatroBot client for communicating with the game."""

import json
import logging
import platform
import re
import shutil
import socket
from pathlib import Path
from typing import Self

from .enums import ErrorCode
from .exceptions import (
    BalatroError,
    ConnectionFailedError,
    create_exception_from_error_response,
)
from .models import APIRequest

logger = logging.getLogger(__name__)


class BalatroClient:
    """Client for communicating with the BalatroBot game API.

    The client provides methods for game control, state management, and development tools
    including a checkpointing system for saving and loading game states.

    Attributes:
        host: Host address to connect to
        port: Port number to connect to
        timeout: Socket timeout in seconds
        buffer_size: Socket buffer size in bytes
        _socket: Socket connection to BalatroBot
    """

    host = "127.0.0.1"
    timeout = 300.0
    buffer_size = 65536

    def __init__(self, port: int = 12346, timeout: float | None = None):
        """Initialize BalatroBot client

        Args:
            port: Port number to connect to (default: 12346)
            timeout: Socket timeout in seconds (default: 300.0)
        """
        self.port = port
        self.timeout = timeout if timeout is not None else self.timeout
        self._socket: socket.socket | None = None
        self._connected = False
        self._message_buffer = b""  # Buffer for incomplete messages

    def _receive_complete_message(self) -> bytes:
        """Receive a complete message from the socket, handling message boundaries properly."""
        if not self._connected or not self._socket:
            raise ConnectionFailedError(
                "Socket not connected",
                error_code="E008",
                context={
                    "connected": self._connected,
                    "socket": self._socket is not None,
                },
            )

        # Check if we already have a complete message in the buffer
        while b"\n" not in self._message_buffer:
            try:
                chunk = self._socket.recv(self.buffer_size)
            except socket.timeout:
                raise ConnectionFailedError(
                    "Socket timeout while receiving data",
                    error_code="E008",
                    context={
                        "timeout": self.timeout,
                        "buffer_size": len(self._message_buffer),
                    },
                )
            except socket.error as e:
                raise ConnectionFailedError(
                    f"Socket error while receiving: {e}",
                    error_code="E008",
                    context={"error": str(e), "buffer_size": len(self._message_buffer)},
                )

            if not chunk:
                raise ConnectionFailedError(
                    "Connection closed by server",
                    error_code="E008",
                    context={"buffer_size": len(self._message_buffer)},
                )
            self._message_buffer += chunk

        # Extract the first complete message
        message_end = self._message_buffer.find(b"\n")
        complete_message = self._message_buffer[:message_end]

        # Update buffer to remove the processed message
        remaining_data = self._message_buffer[message_end + 1 :]
        self._message_buffer = remaining_data

        # Log any remaining data for debugging
        if remaining_data:
            logger.warning(f"Data remaining in buffer: {len(remaining_data)} bytes")
            logger.debug(f"Buffer preview: {remaining_data[:100]}...")

        return complete_message

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
        # Clear message buffer on disconnect
        self._message_buffer = b""

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

            # Receive response using improved message handling
            complete_message = self._receive_complete_message()

            # Decode and validate the message
            message_str = complete_message.decode().strip()
            logger.debug(f"Raw message length: {len(message_str)} characters")
            logger.debug(f"Message preview: {message_str[:100]}...")

            # Ensure the message is properly formatted JSON
            if not message_str:
                raise BalatroError(
                    "Empty response received from game",
                    error_code="E001",
                    context={"raw_data_length": len(complete_message)},
                )

            response_data = json.loads(message_str)

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
            logger.error(f"Problematic message content: {message_str[:200]}...")
            logger.error(
                f"Message buffer state: {len(self._message_buffer)} bytes remaining"
            )

            # Clear the message buffer to prevent cascading errors
            if self._message_buffer:
                logger.warning("Clearing message buffer due to JSON parse error")
                self._message_buffer = b""

            raise BalatroError(
                f"Invalid JSON response from game: {e}",
                error_code="E001",
                context={"error": str(e), "message_preview": message_str[:100]},
            ) from e

    # Checkpoint Management Methods

    def _convert_windows_path_to_linux(self, windows_path: str) -> str:
        """Convert Windows path to Linux Steam Proton path if on Linux.

        Args:
            windows_path: Windows-style path (e.g., "C:/Users/.../Balatro/3/save.jkr")

        Returns:
            Converted path for Linux or original path for other platforms
        """

        if platform.system() == "Linux":
            # Match Windows drive letter and path (e.g., "C:/...", "D:\\...", "E:...")
            match = re.match(r"^([A-Z]):[\\/]*(.*)", windows_path, re.IGNORECASE)
            if match:
                # Replace drive letter with Linux Steam Proton prefix
                linux_prefix = str(
                    Path(
                        "~/.steam/steam/steamapps/compatdata/2379780/pfx/drive_c"
                    ).expanduser()
                )
                # Normalize slashes and join with prefix
                rest_of_path = match.group(2).replace("\\", "/")
                return linux_prefix + "/" + rest_of_path

        return windows_path

    def get_save_info(self) -> dict:
        """Get the current save file location and profile information.

        Development tool for working with save files and checkpoints.

        Returns:
            Dictionary containing:
            - profile_path: Current profile path (e.g., "3")
            - save_directory: Full path to Love2D save directory
            - save_file_path: Full OS-specific path to save.jkr file
            - has_active_run: Whether a run is currently active
            - save_exists: Whether the save file exists

        Raises:
            BalatroError: If request fails

        Note:
            This is primarily for development and testing purposes.
        """
        save_info = self.send_message("get_save_info")

        # Convert Windows paths to Linux Steam Proton paths if needed
        if "save_file_path" in save_info and save_info["save_file_path"]:
            save_info["save_file_path"] = self._convert_windows_path_to_linux(
                save_info["save_file_path"]
            )
        if "save_directory" in save_info and save_info["save_directory"]:
            save_info["save_directory"] = self._convert_windows_path_to_linux(
                save_info["save_directory"]
            )

        return save_info

    def save_checkpoint(self, checkpoint_name: str | Path) -> Path:
        """Save the current save.jkr file as a checkpoint.

        Args:
            checkpoint_name: Either:
                - A checkpoint name (saved to checkpoints dir)
                - A full file path where the checkpoint should be saved
                - A directory path (checkpoint will be saved as 'save.jkr' inside it)

        Returns:
            Path to the saved checkpoint file

        Raises:
            BalatroError: If no save file exists or the destination path is invalid
            IOError: If file operations fail
        """
        # Get current save info
        save_info = self.get_save_info()
        if not save_info.get("save_exists"):
            raise BalatroError(
                "No save file exists to checkpoint", ErrorCode.INVALID_GAME_STATE
            )

        # Get the full save file path from API (already OS-specific)
        save_path = Path(save_info["save_file_path"])
        if not save_path.exists():
            raise BalatroError(
                f"Save file not found: {save_path}", ErrorCode.MISSING_GAME_OBJECT
            )

        # Normalize and interpret destination
        dest = Path(checkpoint_name).expanduser()
        # Treat paths without a .jkr suffix as directories
        if dest.suffix.lower() != ".jkr":
            raise BalatroError(
                f"Invalid checkpoint path provided: {dest}",
                ErrorCode.INVALID_PARAMETER,
                context={"path": str(dest), "reason": "Path does not end with .jkr"},
            )

        # Ensure destination directory exists
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise BalatroError(
                f"Invalid checkpoint path provided: {dest}",
                ErrorCode.INVALID_PARAMETER,
                context={"path": str(dest), "reason": str(e)},
            ) from e

        # Copy save file to checkpoint
        try:
            shutil.copy2(save_path, dest)
        except OSError as e:
            raise BalatroError(
                f"Failed to write checkpoint to: {dest}",
                ErrorCode.INVALID_PARAMETER,
                context={"path": str(dest), "reason": str(e)},
            ) from e

        return dest

    def prepare_save(self, source_path: str | Path) -> str:
        """Prepare a test save file for use with load_save.

        This copies a .jkr file from your test directory into Love2D's save directory
        in a temporary profile so it can be loaded with load_save().

        Args:
            source_path: Path to the .jkr save file to prepare

        Returns:
            The Love2D-relative path to use with load_save()
            (e.g., "checkpoint/save.jkr")

        Raises:
            BalatroError: If source file not found
            IOError: If file operations fail
        """
        source = Path(source_path)
        if not source.exists():
            raise BalatroError(
                f"Source save file not found: {source}", ErrorCode.MISSING_GAME_OBJECT
            )

        # Get save directory info
        save_info = self.get_save_info()
        if not save_info.get("save_directory"):
            raise BalatroError(
                "Cannot determine Love2D save directory", ErrorCode.INVALID_GAME_STATE
            )

        checkpoints_profile = "checkpoint"
        save_dir = Path(save_info["save_directory"])
        checkpoints_dir = save_dir / checkpoints_profile
        checkpoints_dir.mkdir(parents=True, exist_ok=True)

        # Copy the save file to the test profile
        dest_path = checkpoints_dir / "save.jkr"
        shutil.copy2(source, dest_path)

        # Return the Love2D-relative path
        return f"{checkpoints_profile}/save.jkr"

    def load_save(self, save_path: str | Path) -> dict:
        """Load a save file directly without requiring a game restart.

        This method loads a save file (in Love2D's save directory format) and starts
        a run from that save state. Unlike load_checkpoint which copies to the profile's
        save location and requires restart, this directly loads the save into the game.

        This is particularly useful for testing as it allows you to quickly jump to
        specific game states without manual setup.

        Args:
            save_path: Path to the save file relative to Love2D save directory
                      (e.g., "3/save.jkr" for profile 3's save)

        Returns:
            Game state after loading the save

        Raises:
            BalatroError: If save file not found or loading fails

        Note:
            This is a development tool that bypasses normal game flow.
            Use with caution in production bots.

        Example:
            ```python
            # Load a profile's save directly
            game_state = client.load_save("3/save.jkr")

            # Or use with prepare_save for external files
            save_path = client.prepare_save("tests/fixtures/shop_state.jkr")
            game_state = client.load_save(save_path)
            ```
        """
        # Convert to string if Path object
        if isinstance(save_path, Path):
            save_path = str(save_path)

        # Send load_save request to API
        return self.send_message("load_save", {"save_path": save_path})

    def load_absolute_save(self, save_path: str | Path) -> dict:
        """Load a save from an absolute path. Takes a full path from the OS as a .jkr file and loads it into the game.

        Args:
            save_path: Path to the save file relative to Love2D save directory
                      (e.g., "3/save.jkr" for profile 3's save)

        Returns:
            Game state after loading the save
        """
        love_save_path = self.prepare_save(save_path)
        return self.load_save(love_save_path)

    def screenshot(self, path: Path | None = None) -> Path:
        """
        Take a screenshot and save as both PNG and JPEG formats.

        Args:
            path: Optional path for PNG file. If provided, PNG will be moved to this location.

        Returns:
            Path to the PNG screenshot. JPEG is saved alongside with .jpg extension.

        Note:
            The response now includes both 'path' (PNG) and 'jpeg_path' (JPEG) keys.
            This method maintains backward compatibility by returning the PNG path.
        """
        screenshot_response = self.send_message("screenshot", {})

        if path is None:
            return Path(screenshot_response["path"])
        else:
            source_path = Path(screenshot_response["path"])
            dest_path = path
            shutil.move(source_path, dest_path)
            return dest_path
