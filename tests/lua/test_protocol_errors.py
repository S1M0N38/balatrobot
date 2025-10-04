"""Tests for BalatroBot TCP API protocol-level error handling."""

import json
import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode

from .conftest import assert_error_response, receive_api_message, send_api_message


class TestProtocolErrors:
    """Tests for protocol-level error handling in the TCP API."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        yield
        # Clean up by going to menu
        try:
            send_api_message(tcp_client, "go_to_menu", {})
            receive_api_message(tcp_client)
        except Exception:
            pass  # Ignore cleanup errors

    def test_invalid_json_error(self, tcp_client: socket.socket) -> None:
        """Test E001: Invalid JSON message handling."""
        # Send malformed JSON
        tcp_client.send(b"{ invalid json }\n")

        response = receive_api_message(tcp_client)
        assert_error_response(
            response,
            "Invalid JSON",
            expected_error_code=ErrorCode.INVALID_JSON.value,
        )

    def test_missing_name_field_error(self, tcp_client: socket.socket) -> None:
        """Test E002: Missing name field in message."""
        # Send message without name field
        message = {"arguments": {}}
        tcp_client.send(json.dumps(message).encode() + b"\n")

        response = receive_api_message(tcp_client)
        assert_error_response(
            response,
            "Message must contain a name",
            expected_error_code=ErrorCode.MISSING_NAME.value,
        )

    def test_missing_arguments_field_error(self, tcp_client: socket.socket) -> None:
        """Test E003: Missing arguments field in message."""
        # Send message without arguments field
        message = {"name": "get_game_state"}
        tcp_client.send(json.dumps(message).encode() + b"\n")

        response = receive_api_message(tcp_client)
        assert_error_response(
            response,
            "Message must contain arguments",
            expected_error_code=ErrorCode.MISSING_ARGUMENTS.value,
        )

    def test_unknown_function_error(self, tcp_client: socket.socket) -> None:
        """Test E004: Unknown function name."""
        # Send message with non-existent function name
        message = {"name": "nonexistent_function", "arguments": {}}
        tcp_client.send(json.dumps(message).encode() + b"\n")

        response = receive_api_message(tcp_client)
        assert_error_response(
            response,
            "Unknown function name",
            expected_error_code=ErrorCode.UNKNOWN_FUNCTION.value,
            expected_context_keys=["name"],
        )
        assert response["context"]["name"] == "nonexistent_function"

    def test_invalid_arguments_type_error(self, tcp_client: socket.socket) -> None:
        """Test E005: Arguments must be a table/dict."""
        # Send message with non-dict arguments
        message = {"name": "get_game_state", "arguments": "not_a_dict"}
        tcp_client.send(json.dumps(message).encode() + b"\n")

        response = receive_api_message(tcp_client)
        assert_error_response(
            response,
            "Arguments must be a table",
            expected_error_code=ErrorCode.INVALID_ARGUMENTS.value,
            expected_context_keys=["received_type"],
        )
        assert response["context"]["received_type"] == "string"

    def test_invalid_arguments_number_error(self, tcp_client: socket.socket) -> None:
        """Test E005: Arguments as number instead of dict."""
        # Send message with number arguments
        message = {"name": "get_game_state", "arguments": 123}
        tcp_client.send(json.dumps(message).encode() + b"\n")

        response = receive_api_message(tcp_client)
        assert_error_response(
            response,
            "Arguments must be a table",
            expected_error_code=ErrorCode.INVALID_ARGUMENTS.value,
            expected_context_keys=["received_type"],
        )
        assert response["context"]["received_type"] == "number"

    def test_invalid_arguments_null_error(self, tcp_client: socket.socket) -> None:
        """Test E003: Arguments as null (None) is treated as missing arguments."""
        # Send message with null arguments - Lua treats null as missing field
        message = {"name": "get_game_state", "arguments": None}
        tcp_client.send(json.dumps(message).encode() + b"\n")

        response = receive_api_message(tcp_client)
        assert_error_response(
            response,
            "Message must contain arguments",
            expected_error_code=ErrorCode.MISSING_ARGUMENTS.value,
        )

    def test_protocol_error_response_structure(self, tcp_client: socket.socket) -> None:
        """Test that all protocol errors have consistent response structure."""
        # Send invalid JSON to trigger protocol error
        tcp_client.send(b"{ malformed json }\n")

        response = receive_api_message(tcp_client)

        # Verify response has all required fields
        assert isinstance(response, dict)
        required_fields = {"error", "error_code", "state"}
        assert required_fields.issubset(response.keys())

        # Verify error code format
        assert response["error_code"].startswith("E")
        assert len(response["error_code"]) == 4  # Format: E001, E002, etc.

        # Verify state is an integer
        assert isinstance(response["state"], int)

    def test_multiple_protocol_errors_sequence(self, tcp_client: socket.socket) -> None:
        """Test that multiple protocol errors in sequence are handled correctly."""
        # Test sequence: invalid JSON -> missing name -> unknown function

        # 1. Invalid JSON
        tcp_client.send(b"{ invalid }\n")
        response1 = receive_api_message(tcp_client)
        assert_error_response(
            response1,
            "Invalid JSON",
            expected_error_code=ErrorCode.INVALID_JSON.value,
        )

        # 2. Missing name
        message2 = {"arguments": {}}
        tcp_client.send(json.dumps(message2).encode() + b"\n")
        response2 = receive_api_message(tcp_client)
        assert_error_response(
            response2,
            "Message must contain a name",
            expected_error_code=ErrorCode.MISSING_NAME.value,
        )

        # 3. Unknown function
        message3 = {"name": "fake_function", "arguments": {}}
        tcp_client.send(json.dumps(message3).encode() + b"\n")
        response3 = receive_api_message(tcp_client)
        assert_error_response(
            response3,
            "Unknown function name",
            expected_error_code=ErrorCode.UNKNOWN_FUNCTION.value,
        )

        # 4. Valid call should still work
        send_api_message(tcp_client, "get_game_state", {})
        valid_response = receive_api_message(tcp_client)
        assert "error" not in valid_response
        assert "state" in valid_response
