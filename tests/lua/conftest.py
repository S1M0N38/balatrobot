"""Lua API test-specific configuration and fixtures."""

import json
import platform
import shutil
import socket
from pathlib import Path
from typing import Any, Generator

import pytest

# Connection settings
HOST = "127.0.0.1"
TIMEOUT: float = 60.0  # timeout for socket operations in seconds
BUFFER_SIZE: int = 65536  # 64KB buffer for TCP messages


@pytest.fixture
def tcp_client(port: int) -> Generator[socket.socket, None, None]:
    """Create and clean up a TCP client socket.

    Yields:
        Configured TCP socket for testing.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        # Set socket receive buffer size
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        sock.connect((HOST, port))
        yield sock


def send_api_message(sock: socket.socket, name: str, arguments: dict) -> None:
    """Send a properly formatted JSON API message.

    Args:
        sock: Socket to send through.
        name: Function name to call.
        arguments: Arguments dictionary for the function.
    """
    message = {"name": name, "arguments": arguments}
    sock.send(json.dumps(message).encode() + b"\n")


def receive_api_message(sock: socket.socket) -> dict[str, Any]:
    """Receive a properly formatted JSON API message from the socket.

    Args:
        sock: Socket to receive from.

    Returns:
        Received message as a dictionary.
    """
    data = sock.recv(BUFFER_SIZE)
    return json.loads(data.decode().strip())


def send_and_receive_api_message(
    sock: socket.socket, name: str, arguments: dict
) -> dict[str, Any]:
    """Send a properly formatted JSON API message and receive the response.

    Args:
        sock: Socket to send through.
        name: Function name to call.
        arguments: Arguments dictionary for the function.

    Returns:
        The game state after the message is sent and received.
    """
    send_api_message(sock, name, arguments)
    game_state = receive_api_message(sock)
    return game_state


def assert_error_response(
    response,
    expected_error_text,
    expected_context_keys=None,
    expected_error_code=None,
):
    """
    Helper function to assert the format and content of an error response.

    Args:
        response (dict): The response dictionary to validate. Must contain at least
            the keys "error", "state", and "error_code".
        expected_error_text (str): The expected error message text to check within
            the "error" field of the response.
        expected_context_keys (list, optional): A list of keys expected to be present
            in the "context" field of the response, if the "context" field exists.
        expected_error_code (str, optional): The expected error code to check within
            the "error_code" field of the response.

    Raises:
        AssertionError: If the response does not match the expected format or content.
    """
    assert isinstance(response, dict)
    assert "error" in response
    assert "state" in response
    assert "error_code" in response
    assert expected_error_text in response["error"]
    if expected_error_code:
        assert response["error_code"] == expected_error_code
    if expected_context_keys:
        assert "context" in response
        for key in expected_context_keys:
            assert key in response["context"]


def prepare_checkpoint(sock: socket.socket, checkpoint_path: Path) -> dict[str, Any]:
    """Prepare a checkpoint file for loading and load it into the game.

    This function copies a checkpoint file to Love2D's save directory and loads it
    directly without requiring a game restart.

    Args:
        sock: Socket connection to the game.
        checkpoint_path: Path to the checkpoint .jkr file to load.

    Returns:
        Game state after loading the checkpoint.

    Raises:
        FileNotFoundError: If checkpoint file doesn't exist.
        RuntimeError: If loading the checkpoint fails.
    """
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    # First, get the save directory from the game
    game_state = send_and_receive_api_message(sock, "get_save_info", {})

    # Determine the Love2D save directory
    # On Linux with Steam, convert Windows paths

    save_dir_str = game_state["save_directory"]
    if platform.system() == "Linux" and save_dir_str.startswith("C:"):
        # Replace C: with Linux Steam Proton prefix
        linux_prefix = (
            Path.home() / ".steam/steam/steamapps/compatdata/2379780/pfx/drive_c"
        )
        save_dir_str = str(linux_prefix) + "/" + save_dir_str[3:]

    save_dir = Path(save_dir_str)

    # Copy checkpoint to a test profile in Love2D save directory
    test_profile = "test_checkpoint"
    test_dir = save_dir / test_profile
    test_dir.mkdir(parents=True, exist_ok=True)

    dest_path = test_dir / "save.jkr"
    shutil.copy2(checkpoint_path, dest_path)

    # Load the save using the new load_save API function
    love2d_path = f"{test_profile}/save.jkr"
    game_state = send_and_receive_api_message(
        sock, "load_save", {"save_path": love2d_path}
    )

    # Check for errors
    if "error" in game_state:
        raise RuntimeError(f"Failed to load checkpoint: {game_state['error']}")

    return game_state
