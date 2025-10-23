"""Tests for the BalatroClient class using real Game API."""

import json
import socket
from unittest.mock import Mock

import pytest

from balatrobot.client import BalatroClient
from balatrobot.exceptions import BalatroError, ConnectionFailedError
from balatrobot.models import G


class TestBalatroClient:
    """Test suite for BalatroClient with real Game API."""

    def test_client_initialization_defaults(self, port):
        """Test client initialization with default class attributes."""
        client = BalatroClient(port=port)

        assert client.host == "127.0.0.1"
        assert client.port == port
        assert client.timeout == 60.0
        assert client.buffer_size == 65536
        assert client._socket is None
        assert client._connected is False

    def test_client_class_attributes(self):
        """Test client class attributes are set correctly."""
        assert BalatroClient.host == "127.0.0.1"
        assert BalatroClient.timeout == 60.0
        assert BalatroClient.buffer_size == 65536

    def test_context_manager_with_game_running(self, port):
        """Test context manager functionality with game running."""
        with BalatroClient(port=port) as client:
            assert client._connected is True
            assert client._socket is not None

            # Test that we can get game state
            response = client.send_message("get_game_state", {})
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

    def test_manual_connect_disconnect_with_game_running(self, port):
        """Test manual connection and disconnection with game running."""
        client = BalatroClient(port=port)

        # Test connection
        client.connect()
        assert client._connected is True
        assert client._socket is not None

        # Test that we can get game state
        response = client.send_message("get_game_state", {})
        game_state = G.model_validate(response)
        assert isinstance(game_state, G)

        # Test disconnection
        client.disconnect()
        assert client._connected is False
        assert client._socket is None

    def test_get_game_state_with_game_running(self, port):
        """Test getting game state with game running."""
        with BalatroClient(port=port) as client:
            response = client.send_message("get_game_state", {})
            game_state = G.model_validate(response)

            assert isinstance(game_state, G)
            assert hasattr(game_state, "state")

    def test_go_to_menu_with_game_running(self, port):
        """Test going to menu with game running."""
        with BalatroClient(port=port) as client:
            # Test go_to_menu from any state
            response = client.send_message("go_to_menu", {})
            game_state = G.model_validate(response)

            assert isinstance(game_state, G)
            assert hasattr(game_state, "state")

    def test_double_connect_is_safe(self, port):
        """Test that calling connect twice is safe."""
        client = BalatroClient(port=port)

        client.connect()
        assert client._connected is True

        # Second connect should be safe
        client.connect()
        assert client._connected is True

        client.disconnect()

    def test_disconnect_when_not_connected(self, port):
        """Test that disconnecting when not connected is safe."""
        client = BalatroClient(port=port)

        # Should not raise any exceptions
        client.disconnect()
        assert client._connected is False
        assert client._socket is None

    def test_connection_failure_wrong_port(self):
        """Test connection failure with wrong port."""
        client = BalatroClient(port=54321)  # Use invalid port directly

        with pytest.raises(ConnectionFailedError) as exc_info:
            client.connect()

        assert "Failed to connect to 127.0.0.1:54321" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E008"

    def test_send_message_when_not_connected(self, port):
        """Test sending message when not connected raises error."""
        client = BalatroClient(port=port)

        with pytest.raises(ConnectionFailedError) as exc_info:
            client.send_message("get_game_state", {})

        assert "Not connected to the game API" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E008"

    def test_socket_configuration(self, port):
        """Test socket is configured correctly."""
        client = BalatroClient(port=port)
        # Temporarily change timeout and buffer_size
        original_timeout = client.timeout
        original_buffer_size = client.buffer_size
        client.timeout = 5.0
        client.buffer_size = 32768

        with client:
            sock = client._socket

            assert sock is not None
            assert sock.gettimeout() == 5.0
            # Note: OS may adjust buffer size, so we check it's at least the requested size
            assert sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) >= 32768

        # Restore original values
        client.timeout = original_timeout
        client.buffer_size = original_buffer_size

    def test_start_run_with_game_running(self, port):
        """Test start_run method with game running."""
        with BalatroClient(port=port) as client:
            # Test with minimal parameters
            response = client.send_message(
                "start_run", {"deck": "Red Deck", "seed": "OOOO155"}
            )
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

            # Test with all parameters
            response = client.send_message(
                "start_run",
                {
                    "deck": "Blue Deck",
                    "stake": 2,
                    "seed": "OOOO155",
                    "challenge": "test_challenge",
                },
            )
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

    def test_skip_or_select_blind_with_game_running(self, port):
        """Test skip_or_select_blind method with game running."""
        with BalatroClient(port=port) as client:
            # First start a run to get to blind selection state
            response = client.send_message("start_run", {"deck": "Red Deck"})
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

            # Test skip action
            response = client.send_message("skip_or_select_blind", {"action": "skip"})
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

            # Test select action
            response = client.send_message("skip_or_select_blind", {"action": "select"})
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

    def test_play_hand_or_discard_with_game_running(self, port):
        """Test play_hand_or_discard method with game running."""
        with BalatroClient(port=port) as client:
            # Test play_hand action - may fail if not in correct game state
            try:
                response = client.send_message(
                    "play_hand_or_discard", {"action": "play_hand", "cards": [0, 1, 2]}
                )
                game_state = G.model_validate(response)
                assert isinstance(game_state, G)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

            # Test discard action - may fail if not in correct game state
            try:
                response = client.send_message(
                    "play_hand_or_discard", {"action": "discard", "cards": [0]}
                )
                game_state = G.model_validate(response)
                assert isinstance(game_state, G)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

    def test_cash_out_with_game_running(self, port):
        """Test cash_out method with game running."""
        with BalatroClient(port=port) as client:
            try:
                response = client.send_message("cash_out", {})
                game_state = G.model_validate(response)
                assert isinstance(game_state, G)
            except BalatroError:
                # Expected if game is not in correct state for cash out
                pass

    def test_shop_with_game_running(self, port):
        """Test shop method with game running."""
        with BalatroClient(port=port) as client:
            try:
                response = client.send_message("shop", {"action": "next_round"})
                game_state = G.model_validate(response)
                assert isinstance(game_state, G)
            except BalatroError:
                # Expected if game is not in shop state
                pass

    def test_send_message_api_error_response(self, port):
        """Test send_message handles API error responses correctly."""
        client = BalatroClient(port=port)

        # Mock socket to return an error response
        mock_socket = Mock()
        error_response = {
            "error": "Invalid game state",
            "error_code": "E009",
            "state": 1,
            "context": {"expected": "MENU", "actual": "SHOP"},
        }
        mock_socket.recv.return_value = json.dumps(error_response).encode()

        client._socket = mock_socket
        client._connected = True

        with pytest.raises(BalatroError) as exc_info:
            client.send_message("invalid_function", {})

        assert "Invalid game state" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E009"

    def test_send_message_socket_error(self, port):
        """Test send_message handles socket errors correctly."""
        client = BalatroClient(port=port)

        # Mock socket to raise socket error
        mock_socket = Mock()
        mock_socket.send.side_effect = socket.error("Connection broken")

        client._socket = mock_socket
        client._connected = True

        with pytest.raises(ConnectionFailedError) as exc_info:
            client.send_message("test_function", {})

        assert "Socket error during communication" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E008"

    def test_send_message_json_decode_error(self, port):
        """Test send_message handles JSON decode errors correctly."""
        client = BalatroClient(port=port)

        # Mock socket to return invalid JSON
        mock_socket = Mock()
        mock_socket.recv.return_value = b"invalid json response"

        client._socket = mock_socket
        client._connected = True

        with pytest.raises(BalatroError) as exc_info:
            client.send_message("test_function", {})

        assert "Invalid JSON response from game" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E001"

    def test_send_message_successful_response(self, port):
        """Test send_message with successful responses."""
        client = BalatroClient(port=port)

        # Mock successful responses for each API method
        success_response = {
            "state": 1,
            "game": {"chips": 100, "dollars": 4},
            "hand": [],
            "jokers": [],
        }

        mock_socket = Mock()
        mock_socket.recv.return_value = json.dumps(success_response).encode()

        client._socket = mock_socket
        client._connected = True

        # Test skip_or_select_blind success
        response = client.send_message("skip_or_select_blind", {"action": "skip"})
        game_state = G.model_validate(response)
        assert isinstance(game_state, G)

        # Test play_hand_or_discard success
        response = client.send_message(
            "play_hand_or_discard", {"action": "play_hand", "cards": [0, 1]}
        )
        game_state = G.model_validate(response)
        assert isinstance(game_state, G)

        # Test cash_out success
        response = client.send_message("cash_out", {})
        game_state = G.model_validate(response)
        assert isinstance(game_state, G)

        # Test shop success
        response = client.send_message("shop", {"action": "next_round"})
        game_state = G.model_validate(response)
        assert isinstance(game_state, G)


class TestSendMessageAPIFunctions:
    """Test suite for all API functions using send_message method."""

    def test_send_message_get_game_state(self, port):
        """Test send_message with get_game_state function."""
        with BalatroClient(port=port) as client:
            response = client.send_message("get_game_state", {})

            # Response should be a dict that can be validated as G
            assert isinstance(response, dict)
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)
            assert hasattr(game_state, "state")

    def test_send_message_go_to_menu(self, port):
        """Test send_message with go_to_menu function."""
        with BalatroClient(port=port) as client:
            response = client.send_message("go_to_menu", {})

            assert isinstance(response, dict)
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)
            assert hasattr(game_state, "state")

    def test_send_message_start_run_minimal(self, port):
        """Test send_message with start_run function (minimal parameters)."""
        with BalatroClient(port=port) as client:
            response = client.send_message("start_run", {"deck": "Red Deck"})

            assert isinstance(response, dict)
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

    def test_send_message_start_run_with_all_params(self, port):
        """Test send_message with start_run function (all parameters)."""
        with BalatroClient(port=port) as client:
            response = client.send_message(
                "start_run",
                {
                    "deck": "Blue Deck",
                    "stake": 2,
                    "seed": "OOOO155",
                    "challenge": "test_challenge",
                },
            )

            assert isinstance(response, dict)
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

    def test_send_message_skip_or_select_blind_skip(self, port):
        """Test send_message with skip_or_select_blind function (skip action)."""
        with BalatroClient(port=port) as client:
            # First start a run to get to blind selection state
            client.send_message("start_run", {"deck": "Red Deck"})

            response = client.send_message("skip_or_select_blind", {"action": "skip"})

            assert isinstance(response, dict)
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

    def test_send_message_skip_or_select_blind_select(self, port):
        """Test send_message with skip_or_select_blind function (select action)."""
        with BalatroClient(port=port) as client:
            # First start a run to get to blind selection state
            client.send_message("start_run", {"deck": "Red Deck"})

            response = client.send_message("skip_or_select_blind", {"action": "select"})

            assert isinstance(response, dict)
            game_state = G.model_validate(response)
            assert isinstance(game_state, G)

    def test_send_message_play_hand_or_discard_play_hand(self, port):
        """Test send_message with play_hand_or_discard function (play_hand action)."""
        with BalatroClient(port=port) as client:
            # This may fail if not in correct game state - expected behavior
            try:
                response = client.send_message(
                    "play_hand_or_discard", {"action": "play_hand", "cards": [0, 1, 2]}
                )

                assert isinstance(response, dict)
                game_state = G.model_validate(response)
                assert isinstance(game_state, G)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

    def test_send_message_play_hand_or_discard_discard(self, port):
        """Test send_message with play_hand_or_discard function (discard action)."""
        with BalatroClient(port=port) as client:
            # This may fail if not in correct game state - expected behavior
            try:
                response = client.send_message(
                    "play_hand_or_discard", {"action": "discard", "cards": [0]}
                )

                assert isinstance(response, dict)
                game_state = G.model_validate(response)
                assert isinstance(game_state, G)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

    def test_send_message_cash_out(self, port):
        """Test send_message with cash_out function."""
        with BalatroClient(port=port) as client:
            try:
                response = client.send_message("cash_out", {})

                assert isinstance(response, dict)
                game_state = G.model_validate(response)
                assert isinstance(game_state, G)
            except BalatroError:
                # Expected if game is not in correct state for cash out
                pass

    def test_send_message_shop_next_round(self, port):
        """Test send_message with shop function."""
        with BalatroClient(port=port) as client:
            try:
                response = client.send_message("shop", {"action": "next_round"})

                assert isinstance(response, dict)
                game_state = G.model_validate(response)
                assert isinstance(game_state, G)
            except BalatroError:
                # Expected if game is not in shop state
                pass

    def test_send_message_invalid_function_name(self, port):
        """Test send_message with invalid function name raises error."""
        with BalatroClient(port=port) as client:
            with pytest.raises(BalatroError):
                client.send_message("invalid_function", {})

    def test_send_message_missing_required_arguments(self, port):
        """Test send_message with missing required arguments raises error."""
        with BalatroClient(port=port) as client:
            # start_run requires deck parameter
            with pytest.raises(BalatroError):
                client.send_message("start_run", {})

    def test_send_message_invalid_arguments(self, port):
        """Test send_message with invalid arguments raises error."""
        with BalatroClient(port=port) as client:
            # Invalid action for skip_or_select_blind
            with pytest.raises(BalatroError):
                client.send_message(
                    "skip_or_select_blind", {"action": "invalid_action"}
                )
