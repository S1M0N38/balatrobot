"""Shared test configuration and fixtures for BalatroBot API tests."""

import json
import socket
from typing import Any, Generator

import pytest

# Connection settings
HOST = "127.0.0.1"
PORT: int = 12346  # default port for BalatroBot UDP API
TIMEOUT: float = 10.0  # timeout for socket operations in seconds
BUFFER_SIZE: int = 65536  # 64KB buffer for UDP messages


@pytest.fixture
def udp_client() -> Generator[socket.socket, None, None]:
    """Create and clean up a UDP client socket.

    Yields:
        Configured UDP socket for testing.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(TIMEOUT)
        # Set socket receive buffer size
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        yield sock


def send_api_message(sock: socket.socket, name: str, arguments: dict) -> None:
    """Send a properly formatted JSON API message.

    Args:
        sock: Socket to send through.
        name: Function name to call.
        arguments: Arguments dictionary for the function.
    """
    message = {"name": name, "arguments": arguments}
    sock.sendto(json.dumps(message).encode(), (HOST, PORT))


def receive_api_message(sock: socket.socket) -> dict[str, Any]:
    """Receive a properly formatted JSON API message from the socket.

    Args:
        sock: Socket to receive from.

    Returns:
        Received message as a dictionary.
    """
    data, _ = sock.recvfrom(BUFFER_SIZE)
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


def assert_error_response(response, expected_error_text, expected_context_keys=None):
    """Helper function to assert error response format and content."""
    assert isinstance(response, dict)
    assert "error" in response
    assert "state" in response
    assert expected_error_text in response["error"]
    if expected_context_keys:
        assert "context" in response
        for key in expected_context_keys:
            assert key in response["context"]
