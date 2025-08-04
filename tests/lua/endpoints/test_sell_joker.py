import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import assert_error_response, send_and_receive_api_message


class TestSellJoker:
    """Tests for the sell_joker API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[dict, None, None]:
        """Start a run, reach SELECTING_HAND phase with jokers, yield initial state, then clean up."""
        # Begin a run with The Omelette challenge which starts with jokers
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {
                "deck": "Red Deck",
                "stake": 1,
                "challenge": "The Omelette",
                "seed": "OOOO155",
            },
        )

        # Select blind to enter SELECTING_HAND state with jokers already available
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        assert game_state["state"] == State.SELECTING_HAND.value

        # Skip if we don't have any jokers to test with
        if (
            not game_state.get("jokers")
            or not game_state["jokers"].get("cards")
            or len(game_state["jokers"]["cards"]) < 1
        ):
            pytest.skip("No jokers available for testing sell_joker")

        yield game_state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    # ------------------------------------------------------------------
    # Success scenario
    # ------------------------------------------------------------------

    def test_sell_joker_success(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sell the first joker and verify it's removed from the collection."""
        initial_state = setup_and_teardown
        initial_jokers = initial_state["jokers"]["cards"]
        initial_count = len(initial_jokers)
        initial_money = initial_state.get("dollars", 0)

        # Get the joker we're about to sell for reference
        joker_to_sell = initial_jokers[0]

        # Sell the first joker (index 0)
        final_state = send_and_receive_api_message(
            tcp_client,
            "sell_joker",
            {"index": 0},
        )

        # Ensure we remain in selecting hand state
        assert final_state["state"] == State.SELECTING_HAND.value

        # Verify joker count decreased by 1
        final_jokers = final_state["jokers"]["cards"]
        assert len(final_jokers) == initial_count - 1

        # Verify the sold joker is no longer in the collection
        final_sort_ids = [joker["sort_id"] for joker in final_jokers]
        assert joker_to_sell["sort_id"] not in final_sort_ids

        # Verify money increased (jokers typically have sell value)
        final_money = final_state.get("dollars", 0)
        assert final_money >= initial_money

    def test_sell_joker_last_joker(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sell the last joker by index and verify it's removed."""
        initial_state = setup_and_teardown
        initial_jokers = initial_state["jokers"]["cards"]
        initial_count = len(initial_jokers)
        last_index = initial_count - 1

        # Get the last joker for reference
        joker_to_sell = initial_jokers[last_index]

        # Sell the last joker
        final_state = send_and_receive_api_message(
            tcp_client,
            "sell_joker",
            {"index": last_index},
        )

        # Verify joker count decreased by 1
        final_jokers = final_state["jokers"]["cards"]
        assert len(final_jokers) == initial_count - 1

        # Verify the sold joker is no longer in the collection
        final_sort_ids = [joker["sort_id"] for joker in final_jokers]
        assert joker_to_sell["sort_id"] not in final_sort_ids

    def test_sell_joker_multiple_sequential(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sell multiple jokers sequentially and verify each removal."""
        initial_state = setup_and_teardown
        initial_jokers = initial_state["jokers"]["cards"]
        initial_count = len(initial_jokers)

        # Skip if we don't have enough jokers for this test
        if initial_count < 2:
            pytest.skip("Need at least 2 jokers for sequential selling test")

        current_state = initial_state

        # Sell jokers one by one, always selling index 0
        for i in range(2):  # Sell 2 jokers
            current_jokers = current_state["jokers"]["cards"]
            joker_to_sell = current_jokers[0]

            current_state = send_and_receive_api_message(
                tcp_client,
                "sell_joker",
                {"index": 0},
            )

            # Verify the joker was removed
            remaining_jokers = current_state["jokers"]["cards"]
            remaining_sort_ids = [joker["sort_id"] for joker in remaining_jokers]
            assert joker_to_sell["sort_id"] not in remaining_sort_ids
            assert len(remaining_jokers) == len(current_jokers) - 1

        # Verify final count
        assert len(current_state["jokers"]["cards"]) == initial_count - 2

    # ------------------------------------------------------------------
    # Validation / error scenarios
    # ------------------------------------------------------------------

    def test_sell_joker_index_out_of_range_high(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing an index >= jokers count should error."""
        jokers_count = len(setup_and_teardown["jokers"]["cards"])
        invalid_index = jokers_count  # out-of-range zero-based index

        response = send_and_receive_api_message(
            tcp_client,
            "sell_joker",
            {"index": invalid_index},
        )

        assert_error_response(
            response,
            "Joker index out of range",
            ["index", "jokers_count"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_sell_joker_negative_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing a negative index should error."""
        response = send_and_receive_api_message(
            tcp_client,
            "sell_joker",
            {"index": -1},
        )

        assert_error_response(
            response,
            "Joker index out of range",
            ["index", "jokers_count"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_sell_joker_no_jokers_available(self, tcp_client: socket.socket) -> None:
        """Calling sell_joker when no jokers are available should error."""
        # Start a run without jokers (regular Red Deck without The Omelette challenge)
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {
                "deck": "Red Deck",
                "stake": 1,
                "seed": "OOOO155",
            },
        )
        send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        response = send_and_receive_api_message(
            tcp_client,
            "sell_joker",
            {"index": 0},
        )

        assert_error_response(
            response,
            "No jokers available to sell",
            ["jokers_available"],
            ErrorCode.MISSING_GAME_OBJECT.value,
        )

        # Clean up
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_sell_joker_missing_required_field(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Calling sell_joker without the index field should error."""
        response = send_and_receive_api_message(
            tcp_client,
            "sell_joker",
            {},  # Missing required 'index' field
        )

        assert_error_response(
            response,
            "Missing required field: index",
            ["field"],
            ErrorCode.INVALID_PARAMETER.value,
        )

    def test_sell_joker_non_numeric_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing a non-numeric index should error."""
        response = send_and_receive_api_message(
            tcp_client,
            "sell_joker",
            {"index": "invalid"},
        )

        assert_error_response(
            response,
            "Invalid parameter type",
            ["parameter", "expected_type"],
            ErrorCode.INVALID_PARAMETER.value,
        )

    def test_sell_joker_unsellable_joker(self, tcp_client: socket.socket) -> None:
        """Attempting to sell an unsellable joker should error."""

        initial_state = send_and_receive_api_message(
            tcp_client,
            "start_run",
            {
                "deck": "Red Deck",
                "stake": 1,
                "challenge": "Bram Poker",  # contains an unsellable joker
                "seed": "OOOO155",
            },
        )

        assert len(initial_state["jokers"]["cards"]) == 1

        response = send_and_receive_api_message(
            tcp_client,
            "sell_joker",
            {"index": 0},
        )

        assert "cannot be sold" in response.get("error", "").lower()
