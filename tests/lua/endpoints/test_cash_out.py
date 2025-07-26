import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import assert_error_response, send_and_receive_api_message


class TestCashOut:
    """Tests for the cash_out API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        # Start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "OOOO155",  # four of a kind in first hand
        }
        send_and_receive_api_message(tcp_client, "start_run", start_run_args)

        # Select blind
        send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        # Play a winning hand (four of a kind) to reach shop
        game_state = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3]},
        )
        assert game_state["state"] == State.ROUND_EVAL.value
        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_cash_out_success(self, tcp_client: socket.socket) -> None:
        """Test successful cash out returns to shop state."""
        # Cash out should transition to shop state
        game_state = send_and_receive_api_message(tcp_client, "cash_out", {})

        # Verify we're in shop state after cash out
        assert game_state["state"] == State.SHOP.value

    def test_cash_out_invalid_state_error(self, tcp_client: socket.socket) -> None:
        """Test cash out returns error when not in shop state."""
        # Go to menu first to ensure we're not in shop state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

        # Try to cash out when not in shop - should return error
        response = send_and_receive_api_message(tcp_client, "cash_out", {})

        # Verify error response
        assert_error_response(
            response,
            "Cannot cash out when not in round evaluation",
            ["current_state"],
            ErrorCode.INVALID_GAME_STATE.value,
        )
