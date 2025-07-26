import socket
from typing import Generator

import pytest

from balatrobot.enums import State

from ..conftest import send_and_receive_api_message


class TestGetGameState:
    """Tests for the get_game_state API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_get_game_state_response(self, tcp_client: socket.socket) -> None:
        """Test get_game_state message returns valid JSON game state."""
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        assert isinstance(game_state, dict)

    def test_game_state_structure(self, tcp_client: socket.socket) -> None:
        """Test that game state contains expected top-level fields."""
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})

        assert isinstance(game_state, dict)

        expected_keys = {"state", "game"}
        assert expected_keys.issubset(game_state.keys())
        assert isinstance(game_state["state"], int)
        assert isinstance(game_state["game"], (dict, type(None)))

    def test_game_state_during_run(self, tcp_client: socket.socket) -> None:
        """Test getting game state at different points during a run."""
        # Start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        initial_state = send_and_receive_api_message(
            tcp_client, "start_run", start_run_args
        )
        assert initial_state["state"] == State.BLIND_SELECT.value

        # Get game state again to ensure it's consistent
        current_state = send_and_receive_api_message(tcp_client, "get_game_state", {})

        assert current_state["state"] == State.BLIND_SELECT.value
        assert current_state["state"] == initial_state["state"]
