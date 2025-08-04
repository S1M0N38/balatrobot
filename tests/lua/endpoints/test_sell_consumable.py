import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode

from ..conftest import assert_error_response, send_and_receive_api_message


class TestSellConsumable:
    """Tests for the sell_consumable API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[dict, None, None]:
        """Start a run with consumables and yield initial state."""
        current_state = send_and_receive_api_message(
            tcp_client,
            "start_run",
            {
                "deck": "Red Deck",
                "stake": 1,
                "challenge": "Bram Poker",
                "seed": "OOOO155",
            },
        )

        yield current_state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    # ------------------------------------------------------------------
    # Success scenario
    # ------------------------------------------------------------------

    def test_sell_consumable_success(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sell the first consumable and verify it's removed from the collection."""
        initial_state = setup_and_teardown
        initial_consumables = initial_state["consumables"]["cards"]
        initial_count = len(initial_consumables)
        initial_money = initial_state.get("game", {}).get("dollars", 0)

        # Get the consumable we're about to sell for reference
        consumable_to_sell = initial_consumables[0]

        # Sell the first consumable (index 0)
        final_state = send_and_receive_api_message(
            tcp_client,
            "sell_consumable",
            {"index": 0},
        )

        # Verify consumable count decreased by 1
        final_consumables = final_state["consumables"]["cards"]
        assert len(final_consumables) == initial_count - 1

        # Verify the sold consumable is no longer in the collection
        final_sort_ids = [consumable["sort_id"] for consumable in final_consumables]
        assert consumable_to_sell["sort_id"] not in final_sort_ids

        # Verify money increased (consumables typically have sell value)
        final_money = final_state.get("game", {}).get("dollars", 0)
        assert final_money > initial_money

    def test_sell_consumable_last_consumable(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sell the last consumable by index and verify it's removed."""
        initial_state = setup_and_teardown
        initial_consumables = initial_state["consumables"]["cards"]
        initial_count = len(initial_consumables)
        last_index = initial_count - 1

        # Get the last consumable for reference
        consumable_to_sell = initial_consumables[last_index]

        # Sell the last consumable
        final_state = send_and_receive_api_message(
            tcp_client,
            "sell_consumable",
            {"index": last_index},
        )

        # Verify consumable count decreased by 1
        final_consumables = final_state["consumables"]["cards"]
        assert len(final_consumables) == initial_count - 1

        # Verify the sold consumable is no longer in the collection
        final_sort_ids = [consumable["sort_id"] for consumable in final_consumables]
        assert consumable_to_sell["sort_id"] not in final_sort_ids

    def test_sell_consumable_multiple_sequential(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sell multiple consumables sequentially and verify each removal."""
        initial_state = setup_and_teardown
        initial_consumables = initial_state["consumables"]["cards"]
        initial_count = len(initial_consumables)

        # Skip if we don't have enough consumables for this test
        if initial_count < 2:
            pytest.skip("Need at least 2 consumables for sequential selling test")

        current_state = initial_state

        # Sell consumables one by one, always selling index 0
        for _ in range(2):  # Sell 2 consumables
            current_consumables = current_state["consumables"]["cards"]
            consumable_to_sell = current_consumables[0]

            current_state = send_and_receive_api_message(
                tcp_client,
                "sell_consumable",
                {"index": 0},
            )

            # Verify the consumable was removed
            remaining_consumables = current_state["consumables"]["cards"]
            remaining_sort_ids = [
                consumable["sort_id"] for consumable in remaining_consumables
            ]
            assert consumable_to_sell["sort_id"] not in remaining_sort_ids
            assert len(remaining_consumables) == len(current_consumables) - 1

        # Verify final count
        assert len(current_state["consumables"]["cards"]) == initial_count - 2

    # ------------------------------------------------------------------
    # Validation / error scenarios
    # ------------------------------------------------------------------

    def test_sell_consumable_index_out_of_range_high(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing an index >= consumables count should error."""
        consumables_count = len(setup_and_teardown["consumables"]["cards"])
        invalid_index = consumables_count  # out-of-range zero-based index

        response = send_and_receive_api_message(
            tcp_client,
            "sell_consumable",
            {"index": invalid_index},
        )

        assert_error_response(
            response,
            "Consumable index out of range",
            ["index", "consumables_count"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_sell_consumable_negative_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing a negative index should error."""
        response = send_and_receive_api_message(
            tcp_client,
            "sell_consumable",
            {"index": -1},
        )

        assert_error_response(
            response,
            "Consumable index out of range",
            ["index", "consumables_count"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_sell_consumable_no_consumables_available(
        self, tcp_client: socket.socket
    ) -> None:
        """Calling sell_consumable when no consumables are available should error."""
        # Start a run without consumables (regular Red Deck without The Omelette challenge)
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
            "sell_consumable",
            {"index": 0},
        )

        assert_error_response(
            response,
            "No consumables available to sell",
            ["consumables_available"],
            ErrorCode.MISSING_GAME_OBJECT.value,
        )

        # Clean up
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_sell_consumable_missing_required_field(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Calling sell_consumable without the index field should error."""
        response = send_and_receive_api_message(
            tcp_client,
            "sell_consumable",
            {},  # Missing required 'index' field
        )

        assert_error_response(
            response,
            "Missing required field: index",
            ["field"],
            ErrorCode.INVALID_PARAMETER.value,
        )

    def test_sell_consumable_non_numeric_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing a non-numeric index should error."""
        response = send_and_receive_api_message(
            tcp_client,
            "sell_consumable",
            {"index": "invalid"},
        )

        assert_error_response(
            response,
            "Invalid parameter type",
            ["parameter", "expected_type"],
            ErrorCode.INVALID_PARAMETER.value,
        )
