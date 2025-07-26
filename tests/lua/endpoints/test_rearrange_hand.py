import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import assert_error_response, send_and_receive_api_message


class TestRearrangeHand:
    """Tests for the rearrange_hand API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[dict, None, None]:
        """Start a run, reach SELECTING_HAND phase, yield initial state, then clean up."""
        # Begin a run and select the first blind to obtain an initial hand
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {
                "deck": "Red Deck",
                "stake": 1,
                "challenge": None,
                "seed": "TESTSEED",
            },
        )
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )
        assert game_state["state"] == State.SELECTING_HAND.value
        yield game_state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    # ------------------------------------------------------------------
    # Success scenario
    # ------------------------------------------------------------------

    def test_rearrange_hand_success(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Reverse the hand order and verify the API response reflects it."""
        initial_state = setup_and_teardown
        initial_cards = initial_state["hand"]["cards"]
        hand_size: int = len(initial_cards)

        # Reverse order indices (API expects zero-based indices)
        new_order = list(range(hand_size - 1, -1, -1))

        final_state = send_and_receive_api_message(
            tcp_client,
            "rearrange_hand",
            {"cards": new_order},
        )

        # Ensure we remain in selecting hand state
        assert final_state["state"] == State.SELECTING_HAND.value

        # Compare card_key ordering to make sure it's reversed
        initial_keys = [card["config"]["card_key"] for card in initial_cards]
        final_keys = [
            card["config"]["card_key"] for card in final_state["hand"]["cards"]
        ]
        assert final_keys == list(reversed(initial_keys))

    def test_rearrange_hand_noop(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sending indices in current order should leave the hand unchanged."""
        initial_state = setup_and_teardown
        initial_cards = initial_state["hand"]["cards"]
        hand_size: int = len(initial_cards)

        # Existing order indices (0-based)
        current_order = list(range(hand_size))

        final_state = send_and_receive_api_message(
            tcp_client,
            "rearrange_hand",
            {"cards": current_order},
        )

        assert final_state["state"] == State.SELECTING_HAND.value

        initial_keys = [card["config"]["card_key"] for card in initial_cards]
        final_keys = [
            card["config"]["card_key"] for card in final_state["hand"]["cards"]
        ]
        assert final_keys == initial_keys

    # ------------------------------------------------------------------
    # Validation / error scenarios
    # ------------------------------------------------------------------

    def test_rearrange_hand_invalid_number_of_cards(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing an index list with the wrong length should error."""
        hand_size = len(setup_and_teardown["hand"]["cards"])
        invalid_order = list(range(hand_size - 1))  # one short

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_hand",
            {"cards": invalid_order},
        )

        assert_error_response(
            response,
            "Invalid number of cards to rearrange",
            ["cards_count", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_hand_out_of_range_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Including an index >= hand size should error."""
        hand_size = len(setup_and_teardown["hand"]["cards"])
        order = list(range(hand_size))
        order[-1] = hand_size  # out-of-range zero-based index

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_hand",
            {"cards": order},
        )

        assert_error_response(
            response,
            "Card index out of range",
            ["index", "max_index"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_hand_invalid_state(self, tcp_client: socket.socket) -> None:
        """Calling rearrange_hand outside of SELECTING_HAND should error."""
        # Ensure we're in MENU state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_hand",
            {"cards": [0]},
        )

        assert_error_response(
            response,
            "Cannot rearrange hand when not selecting hand",
            ["current_state"],
            ErrorCode.INVALID_GAME_STATE.value,
        )
