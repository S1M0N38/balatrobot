"""Main BalatroBot client for communicating with the game."""

import json
import logging
import platform
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

    def _convert_windows_path_to_linux(self, windows_path: str) -> str:
        """Convert Windows path to Linux Steam Proton path if on Linux.

        Args:
            windows_path: Windows-style path (e.g., "C:/Users/.../Balatro/3/save.jkr")

        Returns:
            Converted path for Linux or original path for other platforms
        """

        # Use proton prefix if on linux
        if platform.system() == "Linux" and windows_path.startswith("C:"):
            # Replace C: with Linux Steam Proton prefix
            linux_prefix = str(
                Path(
                    "~/.steam/steam/steamapps/compatdata/2379780/pfx/drive_c"
                ).expanduser()
            )
            # Remove C: or C:/ and replace with Linux prefix
            if windows_path.startswith("C:/"):
                return linux_prefix + "/" + windows_path[3:]
            elif windows_path.startswith("C:\\"):
                # Also handle backslash format
                return linux_prefix + "/" + windows_path[3:].replace("\\", "/")
            else:
                # C: without slash
                return linux_prefix + "/" + windows_path[2:]

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
