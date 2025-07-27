import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import assert_error_response, send_and_receive_api_message


class TestStartRun:
    """Tests for the start_run API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_start_run(self, tcp_client: socket.socket) -> None:
        """Test starting a run and verifying the state."""
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        game_state = send_and_receive_api_message(
            tcp_client, "start_run", start_run_args
        )

        assert game_state["state"] == State.BLIND_SELECT.value

    def test_start_run_with_challenge(self, tcp_client: socket.socket) -> None:
        """Test starting a run with a challenge."""
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": "The Omelette",
            "seed": "EXAMPLE",
        }
        game_state = send_and_receive_api_message(
            tcp_client, "start_run", start_run_args
        )

        print("challenge gamestates")
        print(game_state)
        assert game_state["state"] == State.BLIND_SELECT.value
        assert len(game_state["jokers"]) == 5  # jokers in The Omelette challenge

    def test_start_run_different_stakes(self, tcp_client: socket.socket) -> None:
        """Test starting runs with different stake levels."""
        for stake in [1, 2, 3]:
            start_run_args = {
                "deck": "Red Deck",
                "stake": stake,
                "challenge": None,
                "seed": "EXAMPLE",
            }
            game_state = send_and_receive_api_message(
                tcp_client, "start_run", start_run_args
            )

            assert game_state["state"] == State.BLIND_SELECT.value

            # Go back to menu for next iteration
            send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_start_run_missing_required_args(self, tcp_client: socket.socket) -> None:
        """Test start_run with missing required arguments."""
        # Missing deck
        incomplete_args = {
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        # Should receive error response
        response = send_and_receive_api_message(
            tcp_client, "start_run", incomplete_args
        )
        assert_error_response(
            response,
            "Missing required field: deck",
            expected_error_code=ErrorCode.INVALID_PARAMETER.value,
        )

    def test_start_run_invalid_deck(self, tcp_client: socket.socket) -> None:
        """Test start_run with invalid deck name."""
        invalid_args = {
            "deck": "Nonexistent Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        # Should receive error response
        response = send_and_receive_api_message(tcp_client, "start_run", invalid_args)
        assert_error_response(
            response, "Invalid deck name", ["deck"], ErrorCode.DECK_NOT_FOUND.value
        )
