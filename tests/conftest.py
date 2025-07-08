"""Shared test configuration and fixtures for BalatroBot API tests."""

import json
import socket
from typing import Any, Generator

import pytest

# Connection settings
HOST = "127.0.0.1"
PORT = 12346
TIMEOUT = 30.0
BUFFER_SIZE = 65536  # 64KB buffer for UDP messages


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


def teardown_test(sock: socket.socket) -> None:
    """Teardown helper to return to menu state after test.

    Args:
        sock: Socket to send teardown message through.
    """
    send_api_message(sock, "go_to_menu", {})
    receive_api_message(sock)
