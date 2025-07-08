"""Tests for BalatroBot UDP API connection and protocol handling."""

import json
import socket

import pytest
from conftest import BUFFER_SIZE, HOST, PORT, TIMEOUT, send_api_message


def test_basic_connection(udp_client: socket.socket) -> None:
    """Test basic UDP connection and response."""
    send_api_message(udp_client, "get_game_state", {})

    data, addr = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()

    game_state = json.loads(response)
    assert isinstance(game_state, dict)
    assert addr[0] == HOST


def test_rapid_messages(udp_client: socket.socket) -> None:
    """Test rapid succession of get_game_state messages."""
    responses = []

    for _ in range(3):
        send_api_message(udp_client, "get_game_state", {})
        data, _ = udp_client.recvfrom(BUFFER_SIZE)
        response = data.decode().strip()
        game_state = json.loads(response)
        responses.append(game_state)

    assert all(isinstance(resp, dict) for resp in responses)
    assert len(responses) == 3


def test_connection_timeout() -> None:
    """Test behavior when no server is listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0.2)
        message = {"name": "get_game_state", "arguments": json.dumps({})}
        sock.sendto(json.dumps(message).encode(), (HOST, 12345))  # Unused port

        with pytest.raises(socket.timeout):
            sock.recvfrom(1024)


def test_invalid_json_message(udp_client: socket.socket) -> None:
    """Test that invalid JSON messages return error responses."""
    # Send invalid JSON
    udp_client.sendto(b"invalid json", (HOST, PORT))

    # Should receive error response for invalid JSON
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()
    error_response = json.loads(response)
    assert isinstance(error_response, dict)
    assert "error" in error_response
    assert "Invalid JSON" in error_response["error"]

    # Verify server is still responsive
    send_api_message(udp_client, "get_game_state", {})
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()

    # Should still get valid JSON response
    game_state = json.loads(response)
    assert isinstance(game_state, dict)


def test_missing_name_field(udp_client: socket.socket) -> None:
    """Test message without name field returns error response."""
    message = {"arguments": json.dumps({})}
    udp_client.sendto(json.dumps(message).encode(), (HOST, PORT))

    # Should receive error response for missing name field
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()
    error_response = json.loads(response)
    assert isinstance(error_response, dict)
    assert "error" in error_response
    assert "Message must contain a name" in error_response["error"]

    # Verify server is still responsive
    send_api_message(udp_client, "get_game_state", {})
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()

    # Should still get valid JSON response
    game_state = json.loads(response)
    assert isinstance(game_state, dict)


def test_missing_arguments_field(udp_client: socket.socket) -> None:
    """Test message without arguments field returns error response."""
    message = {"name": "get_game_state"}
    udp_client.sendto(json.dumps(message).encode(), (HOST, PORT))

    # Should receive error response for missing arguments field
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()
    error_response = json.loads(response)
    assert isinstance(error_response, dict)
    assert "error" in error_response
    assert "Message must contain arguments" in error_response["error"]

    # Verify server is still responsive
    send_api_message(udp_client, "get_game_state", {})
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()

    # Should still get valid JSON response
    game_state = json.loads(response)
    assert isinstance(game_state, dict)


def test_unknown_message(udp_client: socket.socket) -> None:
    """Test that unknown messages return error responses."""
    # Send unknown message
    send_api_message(udp_client, "unknown_function", {})

    # Should receive error response for unknown function
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()
    error_response = json.loads(response)
    assert isinstance(error_response, dict)
    assert "error" in error_response
    assert "Unknown function name" in error_response["error"]

    # Verify server is still responsive
    send_api_message(udp_client, "get_game_state", {})
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()

    # Should still get valid JSON response
    game_state = json.loads(response)
    assert isinstance(game_state, dict)


def test_large_message_handling(udp_client: socket.socket) -> None:
    """Test handling of large messages within UDP limits."""
    # Create a large but valid message
    large_args = {"data": "x" * 1000}  # 1KB of data
    send_api_message(udp_client, "get_game_state", large_args)

    # Should still get a response
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()
    game_state = json.loads(response)
    assert isinstance(game_state, dict)


def test_empty_message(udp_client: socket.socket) -> None:
    """Test sending an empty message."""
    udp_client.sendto(b"", (HOST, PORT))

    # Verify server is still responsive
    send_api_message(udp_client, "get_game_state", {})
    data, _ = udp_client.recvfrom(BUFFER_SIZE)
    response = data.decode().strip()

    # Should still get valid JSON response
    game_state = json.loads(response)
    assert isinstance(game_state, dict)
