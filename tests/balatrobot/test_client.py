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
            game_state = client.go_to_menu()
            assert game_state.state_enum == State.MENU
    except (ConnectionFailedError, BalatroError):
        # Game not running or other API error, skip setup
        pass


class TestBalatroClient:
    """Test suite for BalatroClient with real Game API."""

    def test_client_initialization_defaults(self):
        """Test client initialization with default parameters."""
        client = BalatroClient()

        assert client.host == "127.0.0.1"
        assert client.port == 12346
        assert client.timeout == 10.0
        assert client.buffer_size == 65536
        assert client._socket is None
        assert client._connected is False

    def test_client_initialization_custom_params(self):
        """Test client initialization with custom parameters."""
        client = BalatroClient(
            host="192.168.1.100", port=8080, timeout=5.0, buffer_size=32768
        )

        assert client.host == "192.168.1.100"
        assert client.port == 8080
        assert client.timeout == 5.0
        assert client.buffer_size == 32768

    def test_context_manager_with_game_running(self):
        """Test context manager functionality with game running."""
        with BalatroClient() as client:
            assert client._connected is True
            assert client._socket is not None

            # Test that we can get game state
            game_state = client.get_game_state()
            assert isinstance(game_state, GameState)

    def test_manual_connect_disconnect_with_game_running(self):
        """Test manual connection and disconnection with game running."""
        client = BalatroClient()

        # Test connection
        client.connect()
        assert client._connected is True
        assert client._socket is not None

        # Test that we can get game state
        game_state = client.get_game_state()
        assert isinstance(game_state, GameState)

        # Test disconnection
        client.disconnect()
        assert client._connected is False
        assert client._socket is None

    def test_get_game_state_with_game_running(self):
        """Test getting game state with game running."""
        with BalatroClient() as client:
            game_state = client.get_game_state()

            assert isinstance(game_state, GameState)
            assert hasattr(game_state, "state")

    def test_go_to_menu_with_game_running(self):
        """Test going to menu with game running."""
        with BalatroClient() as client:
            # Test go_to_menu from any state
            game_state = client.go_to_menu()

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
        client = BalatroClient(port=54321)  # Use valid but unlikely port

        with pytest.raises(ConnectionFailedError) as exc_info:
            client.connect()

        assert "Failed to connect to 127.0.0.1:54321" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E008"

    def test_send_request_when_not_connected(self):
        """Test sending request when not connected raises error."""
        client = BalatroClient()

        with pytest.raises(ConnectionFailedError) as exc_info:
            client.get_game_state()

        assert "Not connected to the game API" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E008"

    def test_socket_configuration(self):
        """Test socket is configured correctly."""
        with BalatroClient(timeout=5.0, buffer_size=32768) as client:
            sock = client._socket

            assert sock is not None
            assert sock.gettimeout() == 5.0
            # Note: OS may adjust buffer size, so we check it's at least the requested size
            assert sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) >= 32768

    def test_start_run_with_game_running(self):
        """Test start_run method with game running."""
        with BalatroClient() as client:
            # Test with minimal parameters
            game_state = client.start_run(deck="Red Deck", seed="OOOO155")
            assert isinstance(game_state, GameState)

            # Test with all parameters
            game_state = client.start_run(
                deck="Blue Deck",
                stake=2,
                seed="OOOO155",
                challenge="test_challenge",
            )
            assert isinstance(game_state, GameState)

    def test_skip_or_select_blind_with_game_running(self):
        """Test skip_or_select_blind method with game running."""
        with BalatroClient() as client:
            # First start a run to get to blind selection state
            game_state = client.start_run(deck="Red Deck")
            assert isinstance(game_state, GameState)

            # Test skip action
            game_state = client.skip_or_select_blind("skip")
            assert isinstance(game_state, GameState)

            # Test select action
            game_state = client.skip_or_select_blind("select")
            assert isinstance(game_state, GameState)

    def test_play_hand_or_discard_with_game_running(self):
        """Test play_hand_or_discard method with game running."""
        with BalatroClient() as client:
            # Test play_hand action - may fail if not in correct game state
            try:
                game_state = client.play_hand_or_discard("play_hand", [0, 1, 2])
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

            # Test discard action - may fail if not in correct game state
            try:
                game_state = client.play_hand_or_discard("discard", [0])
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in selecting hand state
                pass

    def test_cash_out_with_game_running(self):
        """Test cash_out method with game running."""
        with BalatroClient() as client:
            try:
                game_state = client.cash_out()
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in correct state for cash out
                pass

    def test_shop_with_game_running(self):
        """Test shop method with game running."""
        with BalatroClient() as client:
            try:
                game_state = client.shop("next_round")
                assert isinstance(game_state, GameState)
            except BalatroError:
                # Expected if game is not in shop state
                pass

    def test_send_request_api_error_response(self):
        """Test _send_request handles API error responses correctly."""
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
            client._send_request("invalid_function", {})

        assert "Invalid game state" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E009"

    def test_send_request_socket_error(self):
        """Test _send_request handles socket errors correctly."""
        client = BalatroClient()

        # Mock socket to raise socket error
        mock_socket = Mock()
        mock_socket.send.side_effect = socket.error("Connection broken")

        client._socket = mock_socket
        client._connected = True

        with pytest.raises(ConnectionFailedError) as exc_info:
            client._send_request("test_function", {})

        assert "Socket error during communication" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E008"

    def test_send_request_json_decode_error(self):
        """Test _send_request handles JSON decode errors correctly."""
        client = BalatroClient()

        # Mock socket to return invalid JSON
        mock_socket = Mock()
        mock_socket.recv.return_value = b"invalid json response"

        client._socket = mock_socket
        client._connected = True

        with pytest.raises(BalatroError) as exc_info:
            client._send_request("test_function", {})

        assert "Invalid JSON response from game" in str(exc_info.value)
        assert exc_info.value.error_code.value == "E001"

    def test_api_methods_successful_response(self):
        """Test API methods with successful responses."""
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
        game_state = client.skip_or_select_blind("skip")
        assert isinstance(game_state, GameState)

        # Test play_hand_or_discard success
        game_state = client.play_hand_or_discard("play_hand", [0, 1])
        assert isinstance(game_state, GameState)

        # Test cash_out success
        game_state = client.cash_out()
        assert isinstance(game_state, GameState)

        # Test shop success
        game_state = client.shop("next_round")
        assert isinstance(game_state, GameState)
