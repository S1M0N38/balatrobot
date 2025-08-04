import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode

from ..conftest import assert_error_response, send_and_receive_api_message


class TestRearrangeConsumables:
    """Tests for the rearrange_consumables API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[dict, None, None]:
        """Start a run, reach shop phase, buy consumables, then enter selecting hand phase."""
        game_state = send_and_receive_api_message(
            tcp_client,
            "start_run",
            {
                "deck": "Red Deck",
                "seed": "OOOO155",
                "stake": 1,
                "challenge": "Bram Poker",  # it starts with two consumable
            },
        )

        assert len(game_state["consumables"]["cards"]) == 2

        yield game_state

        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    # ------------------------------------------------------------------
    # Success scenarios
    # ------------------------------------------------------------------

    def test_rearrange_consumables_success(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Reverse the consumable order and verify the API response reflects it."""
        initial_state = setup_and_teardown
        initial_consumables = initial_state["consumables"]["cards"]
        consumables_count: int = len(initial_consumables)

        # Reverse order indices (API expects zero-based indices)
        new_order = list(range(consumables_count - 1, -1, -1))

        final_state = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumables",
            {"consumables": new_order},
        )

        # Compare sort_id ordering to make sure it's reversed
        initial_sort_ids = [consumable["sort_id"] for consumable in initial_consumables]
        final_sort_ids = [
            consumable["sort_id"] for consumable in final_state["consumables"]["cards"]
        ]
        assert final_sort_ids == list(reversed(initial_sort_ids))

    def test_rearrange_consumables_noop(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sending indices in current order should leave the consumables unchanged."""
        initial_state = setup_and_teardown
        initial_consumables = initial_state["consumables"]["cards"]
        consumables_count: int = len(initial_consumables)

        # Existing order indices (0-based)
        current_order = list(range(consumables_count))

        final_state = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumables",
            {"consumables": current_order},
        )

        initial_sort_ids = [consumable["sort_id"] for consumable in initial_consumables]
        final_sort_ids = [
            consumable["sort_id"] for consumable in final_state["consumables"]["cards"]
        ]
        assert final_sort_ids == initial_sort_ids

    def test_rearrange_consumables_single_consumable(
        self, tcp_client: socket.socket
    ) -> None:
        """Test rearranging when only one consumable is available."""
        # Start a simpler setup with just one consumable
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {"deck": "Red Deck", "seed": "OOOO155", "stake": 1},
        )

        send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3]},
        )

        send_and_receive_api_message(tcp_client, "cash_out", {})

        # Buy only one consumable
        send_and_receive_api_message(
            tcp_client, "shop", {"index": 1, "action": "buy_card"}
        )

        final_state = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumables",
            {"consumables": [0]},
        )

        assert len(final_state["consumables"]["cards"]) == 1

        # Clean up
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    # ------------------------------------------------------------------
    # Validation / error scenarios
    # ------------------------------------------------------------------

    def test_rearrange_consumables_invalid_number_of_consumables(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing an index list with the wrong length should error."""
        consumables_count = len(setup_and_teardown["consumables"]["cards"])
        invalid_order = list(range(consumables_count - 1))  # one short

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumables",
            {"consumables": invalid_order},
        )

        assert_error_response(
            response,
            "Invalid number of consumables to rearrange",
            ["consumables_count", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_consumables_out_of_range_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Including an index >= consumables count should error."""
        consumables_count = len(setup_and_teardown["consumables"]["cards"])
        order = list(range(consumables_count))
        order[-1] = consumables_count  # out-of-range zero-based index

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumables",
            {"consumables": order},
        )

        assert_error_response(
            response,
            "Consumable index out of range",
            ["index", "max_index"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_consumables_no_consumables_available(
        self, tcp_client: socket.socket
    ) -> None:
        """Calling rearrange_consumables when no consumables are available should error."""
        # Start a run without buying consumables
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {"deck": "Red Deck", "stake": 1, "seed": "OOOO155"},
        )
        send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumables",
            {"consumables": []},
        )

        assert_error_response(
            response,
            "No consumables available to rearrange",
            ["consumables_available"],
            ErrorCode.MISSING_GAME_OBJECT.value,
        )

        # Clean up
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_rearrange_consumables_missing_required_field(
        self, tcp_client: socket.socket
    ) -> None:
        """Calling rearrange_consumables without the consumables field should error."""
        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumables",
            {},  # Missing required 'consumables' field
        )

        assert_error_response(
            response,
            "Missing required field: consumables",
            ["field"],
            ErrorCode.INVALID_PARAMETER.value,
        )

    def test_rearrange_consumables_negative_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing negative indices should error (after 0-to-1 based conversion)."""
        consumables_count = len(setup_and_teardown["consumables"]["cards"])
        order = list(range(consumables_count))
        order[0] = -1  # negative index

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumables",
            {"consumables": order},
        )

        assert_error_response(
            response,
            "Consumable index out of range",
            ["index", "max_index"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_consumables_duplicate_indices(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing duplicate indices should work (last occurrence wins)."""
        consumables_count = len(setup_and_teardown["consumables"]["cards"])

        if consumables_count >= 2:
            # Use duplicate index (this should work in current implementation)
            order = [0, 0]  # duplicate first index
            if consumables_count > 2:
                order.extend(range(2, consumables_count))

            final_state = send_and_receive_api_message(
                tcp_client,
                "rearrange_consumables",
                {"consumables": order},
            )

            assert len(final_state["consumables"]["cards"]) == consumables_count
