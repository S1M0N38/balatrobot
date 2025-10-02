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
            "Consumable index out of range",
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
            "Consumable index out of range",
            expected_error_code=ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_use_consumable_float_index(
        self,
        tcp_client: socket.socket,
    ) -> None:
        """Test using consumable with float index."""
        response = send_and_receive_api_message(
            tcp_client, "use_consumable", {"index": 1.5}
        )
        assert_error_response(
            response,
            "Invalid parameter type",
            expected_error_code=ErrorCode.INVALID_PARAMETER.value,
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
            "No consumables available to use",
            expected_error_code=ErrorCode.MISSING_GAME_OBJECT.value,
        )


class TestUseConsumableWithCards:
    """Test use_consumable with cards parameter for consumables that target specific cards."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[dict, None, None]:
        # Start a run and get to SELECTING_HAND state with a consumable
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {
                "deck": "Red Deck",
                "stake": 1,
                "seed": "TEST123",
            },
        )
        send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        # Play a hand to get to shop
        send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3]},
        )
        send_and_receive_api_message(tcp_client, "cash_out", {})

        # Buy a consumable
        send_and_receive_api_message(
            tcp_client,
            "shop",
            {"action": "buy_card", "index": 2},
        )

        # Start next round to get back to SELECTING_HAND state
        send_and_receive_api_message(tcp_client, "shop", {"action": "next_round"})
        game_state = send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        yield game_state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_use_consumable_with_cards_success(
        self, tcp_client: socket.socket, setup_and_teardown
    ) -> None:
        """Test successfully using a consumable with specific cards selected."""
        game_state = setup_and_teardown

        # Verify we're in SELECTING_HAND state
        assert game_state["state"] == State.SELECTING_HAND.value

        # Skip test if no consumables available
        if len(game_state["consumables"]["cards"]) == 0:
            pytest.skip("No consumables available in this test run")

        # Use the consumable with specific cards selected
        response = send_and_receive_api_message(
            tcp_client,
            "use_consumable",
            {"index": 0, "cards": [0, 2, 4]},  # Select cards 0, 2, and 4
        )

        # Verify response is successful
        assert "error" not in response

    def test_use_consumable_with_invalid_cards(
        self, tcp_client: socket.socket, setup_and_teardown
    ) -> None:
        """Test using consumable with invalid card indices."""
        game_state = setup_and_teardown

        # Skip test if no consumables available
        if len(game_state["consumables"]["cards"]) == 0:
            pytest.skip("No consumables available in this test run")

        # Try to use consumable with out-of-range card indices
        response = send_and_receive_api_message(
            tcp_client,
            "use_consumable",
            {"index": 0, "cards": [99, 100]},  # Invalid card indices
        )
        assert_error_response(
            response,
            "Invalid card index",
            expected_error_code=ErrorCode.INVALID_CARD_INDEX.value,
        )

    def test_use_consumable_with_too_many_cards(
        self, tcp_client: socket.socket, setup_and_teardown
    ) -> None:
        """Test using consumable with more than 5 cards."""
        game_state = setup_and_teardown

        # Skip test if no consumables available
        if len(game_state["consumables"]["cards"]) == 0:
            pytest.skip("No consumables available in this test run")

        # Try to use consumable with more than 5 cards
        response = send_and_receive_api_message(
            tcp_client,
            "use_consumable",
            {"index": 0, "cards": [0, 1, 2, 3, 4, 5]},  # 6 cards - too many
        )
        assert_error_response(
            response,
            "Invalid number of cards",
            expected_error_code=ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_use_consumable_with_empty_cards(
        self, tcp_client: socket.socket, setup_and_teardown
    ) -> None:
        """Test using consumable with empty cards array."""
        game_state = setup_and_teardown

        # Skip test if no consumables available
        if len(game_state["consumables"]["cards"]) == 0:
            pytest.skip("No consumables available in this test run")

        # Try to use consumable with empty cards array
        response = send_and_receive_api_message(
            tcp_client,
            "use_consumable",
            {"index": 0, "cards": []},  # Empty array
        )
        assert_error_response(
            response,
            "Invalid number of cards",
            expected_error_code=ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_use_consumable_with_invalid_cards_type(
        self, tcp_client: socket.socket, setup_and_teardown
    ) -> None:
        """Test using consumable with non-array cards parameter."""
        game_state = setup_and_teardown

        # Skip test if no consumables available
        if len(game_state["consumables"]["cards"]) == 0:
            pytest.skip("No consumables available in this test run")

        # Try to use consumable with invalid cards type
        response = send_and_receive_api_message(
            tcp_client,
            "use_consumable",
            {"index": 0, "cards": "invalid"},  # Not an array
        )
        assert_error_response(
            response,
            "Invalid parameter type",
            expected_error_code=ErrorCode.INVALID_PARAMETER.value,
        )

    def test_use_planet_without_cards(
        self, tcp_client: socket.socket, setup_and_teardown
    ) -> None:
        """Test that planet consumables still work without cards parameter."""
        game_state = setup_and_teardown

        # Skip test if no consumables available
        if len(game_state["consumables"]["cards"]) == 0:
            pytest.skip("No consumables available in this test run")

        # Use consumable without cards parameter (original behavior)
        response = send_and_receive_api_message(
            tcp_client,
            "use_consumable",
            {"index": 0},  # No cards parameter
        )

        # Should still work for consumables that don't need cards
        assert "error" not in response

    def test_use_consumable_with_cards_wrong_state(
        self, tcp_client: socket.socket
    ) -> None:
        """Test that using consumable with cards fails in non-SELECTING_HAND states."""
        # Start a run and get to shop state
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {"deck": "Red Deck", "stake": 1, "seed": "OOOO155"},
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

        # Verify we're in SHOP state
        assert game_state["state"] == State.SHOP.value

        # Try to use consumable with cards while in SHOP state (should fail)
        response = send_and_receive_api_message(
            tcp_client, "use_consumable", {"index": 0, "cards": [0, 1, 2]}
        )
        assert_error_response(
            response,
            "Cannot use consumable with cards when not in selecting hand state",
            expected_error_code=ErrorCode.INVALID_GAME_STATE.value,
        )

        send_and_receive_api_message(tcp_client, "go_to_menu", {})
