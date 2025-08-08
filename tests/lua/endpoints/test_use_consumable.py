import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import assert_error_response, send_and_receive_api_message


class TestUseConsumablePlanet:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[dict, None, None]:
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
        send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3]},
        )
        send_and_receive_api_message(tcp_client, "cash_out", {})
        game_state = send_and_receive_api_message(
            tcp_client,
            "shop",
            {"action": "buy_card", "index": 1},
        )

        assert game_state["state"] == State.SHOP.value
        print(game_state["consumables"]["cards"][0]["label"])
        # we are expecting to have a planet card in the consumables

        yield game_state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    # ------------------------------------------------------------------
    # Success scenario
    # ------------------------------------------------------------------

    def test_use_consumable_planet_success(
        self, tcp_client: socket.socket, setup_and_teardown
    ) -> None:
        """Test successfully using a planet consumable."""
        game_state = setup_and_teardown

        # Verify we have a consumable (planet) in slot 0
        assert len(game_state["consumables"]["cards"]) > 0

        # Use the first consumable (index 0)
        response = send_and_receive_api_message(
            tcp_client, "use_consumable", {"index": 0}
        )

        # Verify the consumable was used (should be removed from consumables)
        assert response["state"] == State.SHOP.value
        # The consumable should be consumed and removed
        assert (
            len(response["consumables"]["cards"])
            == len(game_state["consumables"]["cards"]) - 1
        )

    # ------------------------------------------------------------------
    # Validation / error scenarios
    # ------------------------------------------------------------------

    def test_use_consumable_invalid_index(
        self, tcp_client: socket.socket, setup_and_teardown
    ) -> None:
        """Test using consumable with invalid index."""
        game_state = setup_and_teardown
        consumables_count = len(game_state["consumables"]["cards"])

        # Test with index out of range
        response = send_and_receive_api_message(
            tcp_client, "use_consumable", {"index": consumables_count}
        )
        assert_error_response(
            response,
            "index out of range",
            expected_error_code=ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_use_consumable_missing_index(
        self,
        tcp_client: socket.socket,
    ) -> None:
        """Test using consumable without providing index."""
        response = send_and_receive_api_message(tcp_client, "use_consumable", {})
        assert_error_response(
            response,
            "Missing required field",
            expected_error_code=ErrorCode.INVALID_PARAMETER.value,
        )

    def test_use_consumable_invalid_index_type(
        self,
        tcp_client: socket.socket,
    ) -> None:
        """Test using consumable with non-numeric index."""
        response = send_and_receive_api_message(
            tcp_client, "use_consumable", {"index": "invalid"}
        )
        assert_error_response(
            response,
            "Invalid parameter type",
            expected_error_code=ErrorCode.INVALID_PARAMETER.value,
        )

    def test_use_consumable_negative_index(
        self,
        tcp_client: socket.socket,
    ) -> None:
        """Test using consumable with negative index."""
        response = send_and_receive_api_message(
            tcp_client, "use_consumable", {"index": -1}
        )
        assert_error_response(
            response,
            "index out of range",
            expected_error_code=ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )


class TestUseConsumableNoConsumables:
    """Test use_consumable when no consumables are available."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[dict, None, None]:
        # Start a run but don't buy any consumables
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
        send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3]},
        )
        game_state = send_and_receive_api_message(tcp_client, "cash_out", {})

        yield game_state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_use_consumable_no_consumables_available(
        self, tcp_client: socket.socket, setup_and_teardown
    ) -> None:
        """Test using consumable when no consumables are available."""
        game_state = setup_and_teardown

        # Verify no consumables are available
        assert len(game_state["consumables"]["cards"]) == 0

        response = send_and_receive_api_message(
            tcp_client, "use_consumable", {"index": 0}
        )
        assert_error_response(
            response,
            "No consumables available",
            expected_error_code=ErrorCode.MISSING_GAME_OBJECT.value,
        )


# TODO: add test for other types of consumables
class TestUseConsumableOtherType: ...
