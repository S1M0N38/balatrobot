import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import assert_error_response, send_and_receive_api_message


class TestRearrangeConsumeables:
    """Tests for the rearrange_consumeables API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[dict, None, None]:
        """Start a run, reach shop phase, buy consumables, then enter selecting hand phase."""
        # Start a run with specific seed
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {"deck": "Red Deck", "seed": "OOOO155", "stake": 1},
        )

        # Select blind to enter selecting hand state
        send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        # Play hand to progress
        send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3]},
        )

        # Cash out to enter shop
        send_and_receive_api_message(tcp_client, "cash_out", {})

        # Buy first consumable card (usually index 1 is a planet/tarot card)
        game_state = send_and_receive_api_message(
            tcp_client, "shop", {"index": 1, "action": "buy_card"}
        )

        # Go to next round to enter selecting hand state with consumables
        send_and_receive_api_message(tcp_client, "shop", {"action": "next_round"})

        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        # add the other setup from the comment above

        game_state = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "discard", "cards": [0, 1, 2, 3, 4]},
        )
        game_state = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "discard", "cards": [4, 5, 6, 7]},
        )
        game_state = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [2, 3, 4, 5, 6]},
        )
        game_state = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "discard", "cards": [1, 2, 3, 6]},
        )
        game_state = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 3, 4, 5, 6]},
        )

        send_and_receive_api_message(tcp_client, "cash_out", {})

        game_state = send_and_receive_api_message(
            tcp_client, "shop", {"action": "reroll"}
        )
        game_state = send_and_receive_api_message(
            tcp_client, "shop", {"action": "reroll"}
        )

        game_state = send_and_receive_api_message(
            tcp_client, "shop", {"index": 1, "action": "buy_card"}
        )

        assert game_state["state"] == State.SHOP.value
        assert len(game_state["consumeables"]["cards"]) == 2

        yield game_state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    # ------------------------------------------------------------------
    # Success scenarios
    # ------------------------------------------------------------------

    def test_rearrange_consumeables_success(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Reverse the consumable order and verify the API response reflects it."""
        initial_state = setup_and_teardown
        initial_consumeables = initial_state["consumeables"]["cards"]
        consumeables_count: int = len(initial_consumeables)

        # Reverse order indices (API expects zero-based indices)
        new_order = list(range(consumeables_count - 1, -1, -1))

        final_state = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumeables",
            {"consumeables": new_order},
        )

        # Compare sort_id ordering to make sure it's reversed
        initial_sort_ids = [
            consumeable["sort_id"] for consumeable in initial_consumeables
        ]
        final_sort_ids = [
            consumeable["sort_id"]
            for consumeable in final_state["consumeables"]["cards"]
        ]
        assert final_sort_ids == list(reversed(initial_sort_ids))

    def test_rearrange_consumeables_noop(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Sending indices in current order should leave the consumables unchanged."""
        initial_state = setup_and_teardown
        initial_consumeables = initial_state["consumeables"]["cards"]
        consumeables_count: int = len(initial_consumeables)

        # Existing order indices (0-based)
        current_order = list(range(consumeables_count))

        final_state = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumeables",
            {"consumeables": current_order},
        )

        initial_sort_ids = [
            consumeable["sort_id"] for consumeable in initial_consumeables
        ]
        final_sort_ids = [
            consumeable["sort_id"]
            for consumeable in final_state["consumeables"]["cards"]
        ]
        assert final_sort_ids == initial_sort_ids

    def test_rearrange_consumeables_single_consumable(
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
            "rearrange_consumeables",
            {"consumeables": [0]},
        )

        assert len(final_state["consumeables"]["cards"]) == 1

        # Clean up
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    # ------------------------------------------------------------------
    # Validation / error scenarios
    # ------------------------------------------------------------------

    def test_rearrange_consumeables_invalid_number_of_consumeables(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing an index list with the wrong length should error."""
        consumeables_count = len(setup_and_teardown["consumeables"]["cards"])
        invalid_order = list(range(consumeables_count - 1))  # one short

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumeables",
            {"consumeables": invalid_order},
        )

        assert_error_response(
            response,
            "Invalid number of consumeables to rearrange",
            ["consumeables_count", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_consumeables_out_of_range_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Including an index >= consumables count should error."""
        consumeables_count = len(setup_and_teardown["consumeables"]["cards"])
        order = list(range(consumeables_count))
        order[-1] = consumeables_count  # out-of-range zero-based index

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumeables",
            {"consumeables": order},
        )

        assert_error_response(
            response,
            "Consumable index out of range",
            ["index", "max_index"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_consumeables_no_consumeables_available(
        self, tcp_client: socket.socket
    ) -> None:
        """Calling rearrange_consumeables when no consumables are available should error."""
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
            "rearrange_consumeables",
            {"consumeables": []},
        )

        assert_error_response(
            response,
            "No consumeables available to rearrange",
            ["consumeables_available"],
            ErrorCode.MISSING_GAME_OBJECT.value,
        )

        # Clean up
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_rearrange_consumeables_missing_required_field(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Calling rearrange_consumeables without the consumeables field should error."""
        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumeables",
            {},  # Missing required 'consumeables' field
        )

        assert_error_response(
            response,
            "Missing required field: consumeables",
            ["field"],
            ErrorCode.INVALID_PARAMETER.value,
        )

    def test_rearrange_consumeables_negative_index(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing negative indices should error (after 0-to-1 based conversion)."""
        consumeables_count = len(setup_and_teardown["consumeables"]["cards"])
        order = list(range(consumeables_count))
        order[0] = -1  # negative index

        response = send_and_receive_api_message(
            tcp_client,
            "rearrange_consumeables",
            {"consumeables": order},
        )

        assert_error_response(
            response,
            "Consumable index out of range",
            ["index", "max_index"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_rearrange_consumeables_duplicate_indices(
        self, tcp_client: socket.socket, setup_and_teardown: dict
    ) -> None:
        """Providing duplicate indices should work (last occurrence wins)."""
        consumeables_count = len(setup_and_teardown["consumeables"]["cards"])

        if consumeables_count >= 2:
            # Use duplicate index (this should work in current implementation)
            order = [0, 0]  # duplicate first index
            if consumeables_count > 2:
                order.extend(range(2, consumeables_count))

            final_state = send_and_receive_api_message(
                tcp_client,
                "rearrange_consumeables",
                {"consumeables": order},
            )

            assert len(final_state["consumeables"]["cards"]) == consumeables_count
