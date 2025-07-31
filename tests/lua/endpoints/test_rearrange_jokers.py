import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import assert_error_response, send_and_receive_api_message


class TestRearrangeJokers:
    """Tests for the rearrange_jokers API endpoint."""

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

        # Skip if we don't have enough jokers to test with
        if (
            not game_state.get("jokers")
            or not game_state["jokers"].get("cards")
            or len(game_state["jokers"]["cards"]) < 2
        ):
            pytest.skip("Not enough jokers available for testing rearrange_jokers")

        yield game_state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    # ------------------------------------------------------------------
    # Success scenario
    # ------------------------------------------------------------------

    def test_rearrange_jokers_success(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Reverse the joker order and verify the API response reflects it."""
        initial_state = setup_and_teardown
        initial_jokers = initial_state["jokers"]["cards"]
        jokers_count: int = len(initial_jokers)

        # Reverse order indices (API expects zero-based indices)
        new_order = list(range(jokers_count - 1, -1, -1))

        final_state = send_and_receive_api_message(
            tcp_client,
            "rearrange_jokers",
            {"jokers": new_order},
        )

        # Ensure we remain in selecting hand state
        assert final_state["state"] == State.SELECTING_HAND.value

        # Compare sort_id ordering to make sure it's reversed
        initial_sort_ids = [joker["sort_id"] for joker in initial_jokers]
        final_sort_ids = [joker["sort_id"] for joker in final_state["jokers"]["cards"]]
        assert final_sort_ids == list(reversed(initial_sort_ids))

    def test_rearrange_jokers_noop(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sending indices in current order should leave the jokers unchanged."""
        initial_state = setup_and_teardown
        initial_jokers = initial_state["jokers"]["cards"]
        jokers_count: int = len(initial_jokers)

        # Existing order indices (0-based)
        current_order = list(range(jokers_count))

        final_state = send_and_receive_api_message(
            tcp_client,
            "rearrange_jokers",
            {"jokers": current_order},
        )

        assert final_state["state"] == State.SELECTING_HAND.value

        initial_sort_ids = [joker["sort_id"] for joker in initial_jokers]
        final_sort_ids = [joker["sort_id"] for joker in final_state["jokers"]["cards"]]
        assert final_sort_ids == initial_sort_ids

    # ------------------------------------------------------------------
    # Validation / error scenarios
    # ------------------------------------------------------------------

    def test_rearrange_jokers_invalid_number_of_jokers(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing an index list with the wrong length should error."""
        jokers_count = len(setup_and_teardown["jokers"]["cards"])
        invalid_order = list(range(jokers_count - 1))  # one short

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_jokers",
            {"jokers": invalid_order},
        )

        assert_error_response(
            response,
            "Invalid number of jokers to rearrange",
            ["jokers_count", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_jokers_out_of_range_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Including an index >= jokers count should error."""
        jokers_count = len(setup_and_teardown["jokers"]["cards"])
        order = list(range(jokers_count))
        order[-1] = jokers_count  # out-of-range zero-based index

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_jokers",
            {"jokers": order},
        )

        assert_error_response(
            response,
            "Joker index out of range",
            ["index", "max_index"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_jokers_no_jokers_available(
        self, tcp_client: socket.socket
    ) -> None:
        """Calling rearrange_jokers when no jokers are available should error."""
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
            "rearrange_jokers",
            {"jokers": []},
        )

        assert_error_response(
            response,
            "No jokers available to rearrange",
            ["jokers_available"],
            ErrorCode.MISSING_GAME_OBJECT.value,
        )

        # Clean up
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_rearrange_jokers_missing_required_field(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Calling rearrange_jokers without the jokers field should error."""
        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_jokers",
            {},  # Missing required 'jokers' field
        )

        assert_error_response(
            response,
            "Missing required field: jokers",
            ["field"],
            ErrorCode.INVALID_PARAMETER.value,
        )
