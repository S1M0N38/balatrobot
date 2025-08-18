"""Main BalatroBot client for communicating with the game."""

import json
import logging
import platform
import shutil
import socket
from datetime import datetime
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

        Returns:
            Dictionary containing:
            - profile_path: Current profile path (e.g., "3")
            - save_directory: Full path to Love2D save directory
            - save_file_path: Full OS-specific path to save.jkr file
            - has_active_run: Whether a run is currently active
            - save_exists: Whether the save file exists

        Raises:
            BalatroError: If request fails
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

    def checkpoint_dir(self) -> Path:
        """Get the directory where checkpoints are stored.

        Returns:
            Path to the checkpoints directory
        """
        return Path.home() / "dev" / "striby-balatrobot" / "dump" / "checkpoints"

    def save_checkpoint(self, checkpoint_name: str | None = None) -> Path:
        """Save the current save.jkr file as a checkpoint.

        Args:
            checkpoint_name: Optional name for the checkpoint.
                           If not provided, timestamp will be used.

        Returns:
            Path to the saved checkpoint file

        Raises:
            BalatroError: If no save file exists
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

        # Create checkpoints directory
        # TODO: make not hardcoded
        checkpoints_dir = self.checkpoint_dir()
        checkpoints_dir.mkdir(parents=True, exist_ok=True)

        # Generate checkpoint name if not provided
        if not checkpoint_name:
            checkpoint_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create checkpoint file path
        checkpoint_path = checkpoints_dir / f"{checkpoint_name}.jkr"

        # Copy save file to checkpoint
        shutil.copy2(save_path, checkpoint_path)
        logger.info(f"Checkpoint saved: {checkpoint_path}")

        return checkpoint_path

    def load_checkpoint(self, checkpoint: str | Path) -> None:
        """Overwrite the current save.jkr file with a checkpoint.

        Args:
            checkpoint: Either a checkpoint name (looks in checkpoints dir)
                       or a full path to a .jkr file

        Raises:
            BalatroError: If checkpoint not found or no profile active
            IOError: If file operations fail
        """
        # Get current save info
        save_info = self.get_save_info()
        if not save_info.get("profile_path"):
            raise BalatroError("No active profile", ErrorCode.INVALID_GAME_STATE)

        # Get the full save file path from API (already OS-specific)
        save_path = Path(save_info["save_file_path"])

        # Determine checkpoint path
        checkpoint_path = Path(checkpoint)
        if not checkpoint_path.is_absolute():
            # Look in checkpoints directory
            checkpoints_dir = self.checkpoint_dir()
            checkpoint_path = checkpoints_dir / checkpoint
            if not checkpoint_path.suffix:
                checkpoint_path = checkpoint_path.with_suffix(".jkr")

        # Verify checkpoint exists
        if not checkpoint_path.exists():
            raise BalatroError(
                f"Checkpoint not found: {checkpoint_path}",
                ErrorCode.MISSING_GAME_OBJECT,
            )

        # Backup current save (optional)
        if save_path.exists():
            backup_path = save_path.with_suffix(".jkr.backup")
            shutil.copy2(save_path, backup_path)

        # Overwrite save with checkpoint
        shutil.copy2(checkpoint_path, save_path)
        logger.info(f"Loaded checkpoint: {checkpoint_path} -> {save_path}")

    def list_checkpoints(self) -> list[dict]:
        """List all available checkpoints in the checkpoints directory.

        Returns:
            List of checkpoint info dictionaries with name, path, size, and modified time
        """
        checkpoints_dir = self.checkpoint_dir()
        if not checkpoints_dir.exists():
            return []

        checkpoints = []
        for checkpoint_file in checkpoints_dir.glob("*.jkr"):
            stat = checkpoint_file.stat()
            checkpoints.append(
                {
                    "name": checkpoint_file.stem,
                    "path": str(checkpoint_file),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        # Sort by modified time (newest first)
        checkpoints.sort(key=lambda x: x["modified"], reverse=True)
        return checkpoints

    def delete_checkpoint(self, checkpoint_name: str) -> None:
        """Delete a checkpoint file.

        Args:
            checkpoint_name: Name of the checkpoint to delete

        Raises:
            BalatroError: If checkpoint not found
            IOError: If deletion fails
        """
        checkpoints_dir = self.checkpoint_dir()
        checkpoint_path = checkpoints_dir / f"{checkpoint_name}.jkr"

        if not checkpoint_path.exists():
            raise BalatroError(
                f"Checkpoint not found: {checkpoint_name}",
                ErrorCode.MISSING_GAME_OBJECT,
            )

        checkpoint_path.unlink()
        logger.info(f"Checkpoint deleted: {checkpoint_path}")
