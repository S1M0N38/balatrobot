"""Tests for BalatroBot TCP API connection and protocol handling."""

import json
import socket

import pytest
from conftest import (
    BUFFER_SIZE,
    HOST,
    PORT,
    assert_error_response,
    send_api_message,
    receive_api_message,
)


def test_basic_connection(tcp_client: socket.socket) -> None:
    """Test basic TCP connection and response."""
    send_api_message(tcp_client, "get_game_state", {})

    game_state = receive_api_message(tcp_client)
    assert isinstance(game_state, dict)


def test_rapid_messages(tcp_client: socket.socket) -> None:
    """Test rapid succession of get_game_state messages."""
    responses = []

    for _ in range(3):
        send_api_message(tcp_client, "get_game_state", {})
        game_state = receive_api_message(tcp_client)
        responses.append(game_state)

    assert all(isinstance(resp, dict) for resp in responses)
    assert len(responses) == 3


def test_connection_timeout() -> None:
    """Test behavior when no server is listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)

        with pytest.raises((socket.timeout, ConnectionRefusedError)):
            sock.connect((HOST, 12345))  # Unused port


def test_invalid_json_message(tcp_client: socket.socket) -> None:
    """Test that invalid JSON messages return error responses."""
    # Send invalid JSON
    tcp_client.send(b"invalid json\n")

    # Should receive error response for invalid JSON
    error_response = receive_api_message(tcp_client)
    assert_error_response(error_response, "Invalid JSON")

    # Verify server is still responsive
    send_api_message(tcp_client, "get_game_state", {})
    game_state = receive_api_message(tcp_client)
    assert isinstance(game_state, dict)


def test_missing_name_field(tcp_client: socket.socket) -> None:
    """Test message without name field returns error response."""
    message = {"arguments": {}}
    tcp_client.send(json.dumps(message).encode() + b"\n")

    # Should receive error response for missing name field
    error_response = receive_api_message(tcp_client)
    assert_error_response(error_response, "Message must contain a name")

    # Verify server is still responsive
    send_api_message(tcp_client, "get_game_state", {})
    game_state = receive_api_message(tcp_client)
    assert isinstance(game_state, dict)


def test_missing_arguments_field(tcp_client: socket.socket) -> None:
    """Test message without arguments field returns error response."""
    message = {"name": "get_game_state"}
    tcp_client.send(json.dumps(message).encode() + b"\n")

    # Should receive error response for missing arguments field
    error_response = receive_api_message(tcp_client)
    assert_error_response(error_response, "Message must contain arguments")

    # Verify server is still responsive
    send_api_message(tcp_client, "get_game_state", {})
    game_state = receive_api_message(tcp_client)
    assert isinstance(game_state, dict)


def test_unknown_message(tcp_client: socket.socket) -> None:
    """Test that unknown messages return error responses."""
    # Send unknown message
    send_api_message(tcp_client, "unknown_function", {})

    # Should receive error response for unknown function
    error_response = receive_api_message(tcp_client)
    assert_error_response(error_response, "Unknown function name", ["name"])

    # Verify server is still responsive
    send_api_message(tcp_client, "get_game_state", {})
    game_state = receive_api_message(tcp_client)
    assert isinstance(game_state, dict)


def test_large_message_handling(tcp_client: socket.socket) -> None:
    """Test handling of large messages within TCP limits."""
    # Create a large but valid message
    large_args = {"data": "x" * 1000}  # 1KB of data
    send_api_message(tcp_client, "get_game_state", large_args)

    # Should still get a response
    game_state = receive_api_message(tcp_client)
    assert isinstance(game_state, dict)


def test_empty_message(tcp_client: socket.socket) -> None:
    """Test sending an empty message."""
    tcp_client.send(b"\n")

    # Verify server is still responsive
    send_api_message(tcp_client, "get_game_state", {})
    game_state = receive_api_message(tcp_client)
    assert isinstance(game_state, dict)
