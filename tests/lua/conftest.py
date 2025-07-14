"""Shared test configuration and fixtures for BalatroBot API tests."""

import json
import socket
from typing import Any, Generator

import pytest

# Connection settings
HOST = "127.0.0.1"
PORT: int = 12346  # default port for BalatroBot TCP API
TIMEOUT: float = 10.0  # timeout for socket operations in seconds
BUFFER_SIZE: int = 65536  # 64KB buffer for TCP messages


@pytest.fixture
def tcp_client() -> Generator[socket.socket, None, None]:
    """Create and clean up a TCP client socket.

    Yields:
        Configured TCP socket for testing.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        # Set socket receive buffer size
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        sock.connect((HOST, PORT))
        yield sock


@pytest.fixture
def udp_client() -> Generator[socket.socket, None, None]:
    """Create and clean up a TCP client socket (legacy support).

    Yields:
        Configured TCP socket for testing.
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
    if sock.type == socket.SOCK_STREAM:
        sock.send(json.dumps(message).encode() + b"\n")
    else:
        sock.sendto(json.dumps(message).encode(), (HOST, PORT))


def receive_api_message(sock: socket.socket) -> dict[str, Any]:
    """Receive a properly formatted JSON API message from the socket.

    Args:
        sock: Socket to receive from.

    Returns:
        Received message as a dictionary.
    """
    if sock.type == socket.SOCK_STREAM:
        data = sock.recv(BUFFER_SIZE)
        return json.loads(data.decode().strip())
    else:
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


def assert_error_response(
    response, expected_error_text, expected_context_keys=None, expected_error_code=None
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
