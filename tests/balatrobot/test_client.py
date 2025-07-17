"""Tests for the BalatroClient class using real Game API."""

import json
import socket
from unittest.mock import Mock

import pytest

from src.balatrobot.client import BalatroClient
from src.balatrobot.enums import State
from src.balatrobot.exceptions import BalatroError, ConnectionFailedError
from src.balatrobot.models import GameState


@pytest.fixture(scope="function", autouse=True)
def reset_game_to_menu():
    """Reset game to menu state before each test."""
    try:
        with BalatroClient() as client:
            response = client.send_message("go_to_menu", {})
            game_state = GameState.model_validate(response)
            assert game_state.state_enum == State.MENU
    except (ConnectionFailedError, BalatroError):
        # Game not running or other API error, skip setup
        pass


class TestBalatroClient:
    """Test suite for BalatroClient with real Game API."""

    def test_client_initialization_defaults(self):
        """Test client initialization with default class attributes."""
        client = BalatroClient()

        assert client.host == "127.0.0.1"
        assert client.port == 12346
        assert client.timeout == 10.0
        assert client.buffer_size == 65536
        assert client._socket is None
        assert client._connected is False

    def test_client_class_attributes(self):
        """Test client class attributes are set correctly."""
        assert BalatroClient.host == "127.0.0.1"
        assert BalatroClient.port == 12346
        assert BalatroClient.timeout == 10.0
        assert BalatroClient.buffer_size == 65536

    def test_context_manager_with_game_running(self):
        """Test context manager functionality with game running."""
        with BalatroClient() as client:
            assert client._connected is True
            assert client._socket is not None

            # Test that we can get game state
            response = client.send_message("get_game_state", {})
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

    def test_manual_connect_disconnect_with_game_running(self):
        """Test manual connection and disconnection with game running."""
        client = BalatroClient()

        # Test connection
        client.connect()
        assert client._connected is True
        assert client._socket is not None

        # Test that we can get game state
        response = client.send_message("get_game_state", {})
        game_state = GameState.model_validate(response)
        assert isinstance(game_state, GameState)

        # Test disconnection
        client.disconnect()
        assert client._connected is False
        assert client._socket is None

    def test_get_game_state_with_game_running(self):
        """Test getting game state with game running."""
        with BalatroClient() as client:
            response = client.send_message("get_game_state", {})
            game_state = GameState.model_validate(response)

            assert isinstance(game_state, GameState)
            assert hasattr(game_state, "state")

    def test_go_to_menu_with_game_running(self):
        """Test going to menu with game running."""
        with BalatroClient() as client:
            # Test go_to_menu from any state
            response = client.send_message("go_to_menu", {})
            game_state = GameState.model_validate(response)

            assert isinstance(game_state, GameState)
            assert hasattr(game_state, "state")

    def test_double_connect_is_safe(self):
        """Test that calling connect twice is safe."""
        client = BalatroClient()

        client.connect()
        assert client._connected is True

        # Second connect should be safe
        client.connect()
        assert client._connected is True

        client.disconnect()

    def test_disconnect_when_not_connected(self):
        """Test that disconnecting when not connected is safe."""
        client = BalatroClient()

        # Should not raise any exceptions
        client.disconnect()
        assert client._connected is False
        assert client._socket is None

    def test_connection_failure_wrong_port(self):
        """Test connection failure with wrong port."""
        client = BalatroClient()
        # Temporarily change port to invalid one
        original_port = client.port
        client.port = 54321

        with pytest.raises(ConnectionFailedError) as exc_info:
            client.connect()

        # Restore original port
        client.port = original_port
        assert "Failed to connect to 127.0.0.1:54321" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E008"

    def test_send_message_when_not_connected(self):
        """Test sending message when not connected raises error."""
        client = BalatroClient()

        with pytest.raises(ConnectionFailedError) as exc_info:
            client.send_message("get_game_state", {})

        assert "Not connected to the game API" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E008"

    def test_socket_configuration(self):
        """Test socket is configured correctly."""
        client = BalatroClient()
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

    def test_start_run_with_game_running(self):
        """Test start_run method with game running."""
        with BalatroClient() as client:
            # Test with minimal parameters
            response = client.send_message(
                "start_run", {"deck": "Red Deck", "seed": "OOOO155"}
            )
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

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
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

    def test_skip_or_select_blind_with_game_running(self):
        """Test skip_or_select_blind method with game running."""
        with BalatroClient() as client:
            # First start a run to get to blind selection state
            response = client.send_message("start_run", {"deck": "Red Deck"})
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

            # Test skip action
            response = client.send_message("skip_or_select_blind", {"action": "skip"})
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

            # Test select action
            response = client.send_message("skip_or_select_blind", {"action": "select"})
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

    def test_play_hand_or_discard_with_game_running(self):
        """Test play_hand_or_discard method with game running."""
        with BalatroClient() as client:
            # Test play_hand action - may fail if not in correct game state
            try:
                response = client.send_message(
                    "play_hand_or_discard", {"action": "play_hand", "cards": [0, 1, 2]}
                )
                game_state = GameState.model_validate(response)
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

            # Test discard action - may fail if not in correct game state
            try:
                response = client.send_message(
                    "play_hand_or_discard", {"action": "discard", "cards": [0]}
                )
                game_state = GameState.model_validate(response)
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

    def test_cash_out_with_game_running(self):
        """Test cash_out method with game running."""
        with BalatroClient() as client:
            try:
                response = client.send_message("cash_out", {})
                game_state = GameState.model_validate(response)
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in correct state for cash out
                pass

    def test_shop_with_game_running(self):
        """Test shop method with game running."""
        with BalatroClient() as client:
            try:
                response = client.send_message("shop", {"action": "next_round"})
                game_state = GameState.model_validate(response)
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in shop state
                pass

    def test_send_message_api_error_response(self):
        """Test send_message handles API error responses correctly."""
        client = BalatroClient()

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

    def test_send_message_socket_error(self):
        """Test send_message handles socket errors correctly."""
        client = BalatroClient()

        # Mock socket to raise socket error
        mock_socket = Mock()
        mock_socket.send.side_effect = socket.error("Connection broken")

        client._socket = mock_socket
        client._connected = True

        with pytest.raises(ConnectionFailedError) as exc_info:
            client.send_message("test_function", {})

        assert "Socket error during communication" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E008"

    def test_send_message_json_decode_error(self):
        """Test send_message handles JSON decode errors correctly."""
        client = BalatroClient()

        # Mock socket to return invalid JSON
        mock_socket = Mock()
        mock_socket.recv.return_value = b"invalid json response"

        client._socket = mock_socket
        client._connected = True

        with pytest.raises(BalatroError) as exc_info:
            client.send_message("test_function", {})

        assert "Invalid JSON response from game" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E001"

    def test_send_message_successful_response(self):
        """Test send_message with successful responses."""
        client = BalatroClient()

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
        game_state = GameState.model_validate(response)
        assert isinstance(game_state, GameState)

        # Test play_hand_or_discard success
        response = client.send_message(
            "play_hand_or_discard", {"action": "play_hand", "cards": [0, 1]}
        )
        game_state = GameState.model_validate(response)
        assert isinstance(game_state, GameState)

        # Test cash_out success
        response = client.send_message("cash_out", {})
        game_state = GameState.model_validate(response)
        assert isinstance(game_state, GameState)

        # Test shop success
        response = client.send_message("shop", {"action": "next_round"})
        game_state = GameState.model_validate(response)
        assert isinstance(game_state, GameState)


class TestSendMessageAPIFunctions:
    """Test suite for all API functions using send_message method."""

    def test_send_message_get_game_state(self):
        """Test send_message with get_game_state function."""
        with BalatroClient() as client:
            response = client.send_message("get_game_state", {})

            # Response should be a dict that can be validated as GameState
            assert isinstance(response, dict)
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)
            assert hasattr(game_state, "state")

    def test_send_message_go_to_menu(self):
        """Test send_message with go_to_menu function."""
        with BalatroClient() as client:
            response = client.send_message("go_to_menu", {})

            assert isinstance(response, dict)
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)
            assert hasattr(game_state, "state")

    def test_send_message_start_run_minimal(self):
        """Test send_message with start_run function (minimal parameters)."""
        with BalatroClient() as client:
            response = client.send_message("start_run", {"deck": "Red Deck"})

            assert isinstance(response, dict)
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

    def test_send_message_start_run_with_all_params(self):
        """Test send_message with start_run function (all parameters)."""
        with BalatroClient() as client:
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
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

    def test_send_message_skip_or_select_blind_skip(self):
        """Test send_message with skip_or_select_blind function (skip action)."""
        with BalatroClient() as client:
            # First start a run to get to blind selection state
            client.send_message("start_run", {"deck": "Red Deck"})

            response = client.send_message("skip_or_select_blind", {"action": "skip"})

            assert isinstance(response, dict)
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

    def test_send_message_skip_or_select_blind_select(self):
        """Test send_message with skip_or_select_blind function (select action)."""
        with BalatroClient() as client:
            # First start a run to get to blind selection state
            client.send_message("start_run", {"deck": "Red Deck"})

            response = client.send_message("skip_or_select_blind", {"action": "select"})

            assert isinstance(response, dict)
            game_state = GameState.model_validate(response)
            assert isinstance(game_state, GameState)

    def test_send_message_play_hand_or_discard_play_hand(self):
        """Test send_message with play_hand_or_discard function (play_hand action)."""
        with BalatroClient() as client:
            # This may fail if not in correct game state - expected behavior
            try:
                response = client.send_message(
                    "play_hand_or_discard", {"action": "play_hand", "cards": [0, 1, 2]}
                )

                assert isinstance(response, dict)
                game_state = GameState.model_validate(response)
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

    def test_send_message_play_hand_or_discard_discard(self):
        """Test send_message with play_hand_or_discard function (discard action)."""
        with BalatroClient() as client:
            # This may fail if not in correct game state - expected behavior
            try:
                response = client.send_message(
                    "play_hand_or_discard", {"action": "discard", "cards": [0]}
                )

                assert isinstance(response, dict)
                game_state = GameState.model_validate(response)
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

    def test_send_message_cash_out(self):
        """Test send_message with cash_out function."""
        with BalatroClient() as client:
            try:
                response = client.send_message("cash_out", {})

                assert isinstance(response, dict)
                game_state = GameState.model_validate(response)
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in correct state for cash out
                pass

    def test_send_message_shop_next_round(self):
        """Test send_message with shop function."""
        with BalatroClient() as client:
            try:
                response = client.send_message("shop", {"action": "next_round"})

                assert isinstance(response, dict)
                game_state = GameState.model_validate(response)
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in shop state
                pass

    def test_send_message_invalid_function_name(self):
        """Test send_message with invalid function name raises error."""
        with BalatroClient() as client:
            with pytest.raises(BalatroError):
                client.send_message("invalid_function", {})

    def test_send_message_missing_required_arguments(self):
        """Test send_message with missing required arguments raises error."""
        with BalatroClient() as client:
            # start_run requires deck parameter
            with pytest.raises(BalatroError):
                client.send_message("start_run", {})

    def test_send_message_invalid_arguments(self):
        """Test send_message with invalid arguments raises error."""
        with BalatroClient() as client:
            # Invalid action for skip_or_select_blind
            with pytest.raises(BalatroError):
                client.send_message(
                    "skip_or_select_blind", {"action": "invalid_action"}
                )
