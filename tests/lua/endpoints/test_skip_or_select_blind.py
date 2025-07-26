import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import assert_error_response, send_and_receive_api_message


class TestSkipOrSelectBlind:
    """Tests for the skip_or_select_blind API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "OOOO155",
        }
        game_state = send_and_receive_api_message(
            tcp_client, "start_run", start_run_args
        )
        assert game_state["state"] == State.BLIND_SELECT.value
        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_select_blind(self, tcp_client: socket.socket) -> None:
        """Test selecting a blind during the blind selection phase."""
        # Select the blind
        select_blind_args = {"action": "select"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", select_blind_args
        )

        # Verify we get a valid game state response
        assert game_state["state"] == State.SELECTING_HAND.value

        # Assert that there are 8 cards in the hand
        assert len(game_state["hand"]["cards"]) == 8

    def test_skip_blind(self, tcp_client: socket.socket) -> None:
        """Test skipping a blind during the blind selection phase."""
        # Skip the blind
        skip_blind_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_blind_args
        )

        # Verify we get a valid game state response
        assert game_state["state"] == State.BLIND_SELECT.value

        # Assert that the current blind is "Big", the "Small" blind was skipped
        assert game_state["game"]["blind_on_deck"] == "Big"

    def test_skip_big_blind(self, tcp_client: socket.socket) -> None:
        """Test complete flow: play small blind, cash out, skip shop, skip big blind."""
        # 1. Play small blind (select it)
        select_blind_args = {"action": "select"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", select_blind_args
        )

        # Verify we're in hand selection state
        assert game_state["state"] == State.SELECTING_HAND.value

        # 2. Play winning hand (four of a kind)
        play_hand_args = {"action": "play_hand", "cards": [0, 1, 2, 3]}
        game_state = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", play_hand_args
        )

        # Verify we're in round evaluation state
        assert game_state["state"] == State.ROUND_EVAL.value

        # 3. Cash out to go to shop
        game_state = send_and_receive_api_message(tcp_client, "cash_out", {})

        # Verify we're in shop state
        assert game_state["state"] == State.SHOP.value

        # 4. Skip shop (next round)
        game_state = send_and_receive_api_message(
            tcp_client, "shop", {"action": "next_round"}
        )

        # Verify we're back in blind selection state
        assert game_state["state"] == State.BLIND_SELECT.value

        # 5. Skip the big blind
        skip_big_blind_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_big_blind_args
        )

        # Verify we successfully skipped the big blind and are still in blind selection
        assert game_state["state"] == State.BLIND_SELECT.value

    def test_skip_both_blinds(self, tcp_client: socket.socket) -> None:
        """Test skipping small blind then immediately skipping big blind."""
        # 1. Skip the small blind
        skip_small_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_small_args
        )

        # Verify we're still in blind selection and the big blind is on deck
        assert game_state["state"] == State.BLIND_SELECT.value
        assert game_state["game"]["blind_on_deck"] == "Big"

        # 2. Skip the big blind
        skip_big_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_big_args
        )

        # Verify we successfully skipped both blinds
        assert game_state["state"] == State.BLIND_SELECT.value

    def test_invalid_blind_action(self, tcp_client: socket.socket) -> None:
        """Test that invalid blind action arguments are handled properly."""
        # Should receive error response
        error_response = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "invalid_action"}
        )

        # Verify error response
        assert_error_response(
            error_response,
            "Invalid action for skip_or_select_blind",
            ["action"],
            ErrorCode.INVALID_ACTION.value,
        )

    def test_skip_or_select_blind_invalid_state(
        self, tcp_client: socket.socket
    ) -> None:
        """Test that skip_or_select_blind returns error when not in blind selection state."""
        # Go to menu to ensure we're not in blind selection state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

        # Try to select blind when not in blind selection state
        error_response = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        # Verify error response
        assert_error_response(
            error_response,
            "Cannot skip or select blind when not in blind selection",
            ["current_state"],
            ErrorCode.INVALID_GAME_STATE.value,
        )

    def test_boss_blind_skip_prevention(self, tcp_client: socket.socket) -> None:
        """Test that trying to skip a Boss blind returns INVALID_PARAMETER error."""
        # Skip small blind to reach big blind
        skip_small_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_small_args
        )
        assert game_state["game"]["blind_on_deck"] == "Big"

        # Skip big blind to reach boss blind
        skip_big_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_big_args
        )
        assert game_state["game"]["blind_on_deck"] == "Boss"

        # Try to skip boss blind - should return error
        skip_boss_args = {"action": "skip"}
        error_response = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_boss_args
        )

        # Verify error response
        assert_error_response(
            error_response,
            "Cannot skip Boss blind. Use select instead",
            ["current_state"],
            ErrorCode.INVALID_PARAMETER.value,
        )

    def test_boss_blind_select_still_works(self, tcp_client: socket.socket) -> None:
        """Test that selecting a Boss blind still works correctly."""
        # Skip small blind to reach big blind
        skip_small_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_small_args
        )
        assert game_state["game"]["blind_on_deck"] == "Big"

        # Skip big blind to reach boss blind
        skip_big_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_big_args
        )
        assert game_state["game"]["blind_on_deck"] == "Boss"

        # Select boss blind - should work successfully
        select_boss_args = {"action": "select"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", select_boss_args
        )

        # Verify we successfully selected the boss blind and transitioned to hand selection
        assert game_state["state"] == State.SELECTING_HAND.value

    def test_non_boss_blind_skip_still_works(self, tcp_client: socket.socket) -> None:
        """Test that skipping Small and Big blinds still works correctly."""
        # Skip small blind - should work fine
        skip_small_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_small_args
        )
        assert game_state["state"] == State.BLIND_SELECT.value
        assert game_state["game"]["blind_on_deck"] == "Big"

        # Skip big blind - should also work fine
        skip_big_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", skip_big_args
        )
        assert game_state["state"] == State.BLIND_SELECT.value
        assert game_state["game"]["blind_on_deck"] == "Boss"
