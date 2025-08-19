import socket
import time
from pathlib import Path
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import (
    assert_error_response,
    prepare_checkpoint,
    send_and_receive_api_message,
)


class TestShop:
    """Tests for the shop API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        # Load checkpoint that already has the game in shop state
        checkpoint_path = Path(__file__).parent / "checkpoints" / "basic_shop_setup.jkr"

        game_state = prepare_checkpoint(tcp_client, checkpoint_path)
        time.sleep(0.5)
        assert game_state["state"] == State.SHOP.value

        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_shop_next_round_success(self, tcp_client: socket.socket) -> None:
        """Test successful shop next_round action transitions to blind select."""
        # Execute next_round action
        game_state = send_and_receive_api_message(
            tcp_client, "shop", {"action": "next_round"}
        )

        # Verify we're in blind select state after next_round
        assert game_state["state"] == State.BLIND_SELECT.value

    def test_shop_invalid_action_error(self, tcp_client: socket.socket) -> None:
        """Test shop returns error for invalid action."""
        # Try invalid action
        response = send_and_receive_api_message(
            tcp_client, "shop", {"action": "invalid_action"}
        )

        # Verify error response
        assert_error_response(
            response,
            "Invalid action for shop",
            ["action"],
            ErrorCode.INVALID_ACTION.value,
        )

    def test_shop_jokers_structure(self, tcp_client: socket.socket) -> None:
        """Test that shop_jokers contains expected structure when in shop state."""
        # Get current game state while in shop
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})

        # Verify we're in shop state
        assert game_state["state"] == State.SHOP.value

        # Verify shop_jokers exists and has correct structure
        assert "shop_jokers" in game_state
        shop_jokers = game_state["shop_jokers"]

        # Verify top-level structure
        assert "cards" in shop_jokers
        assert "config" in shop_jokers
        assert isinstance(shop_jokers["cards"], list)
        assert isinstance(shop_jokers["config"], dict)

        # Verify config structure
        config = shop_jokers["config"]
        assert "card_count" in config
        assert "card_limit" in config
        assert isinstance(config["card_count"], int)
        assert isinstance(config["card_limit"], int)

        # Verify each card has required fields
        for card in shop_jokers["cards"]:
            assert "ability" in card
            assert "config" in card
            assert "cost" in card
            assert "debuff" in card
            assert "facing" in card
            # TODO: Use traditional method for checking shop structure.
            # TODO: continuing a run causes the highlighted field to be vacant
            # TODO: this does not prevent the cards from being selected, seems to be a quirk of balatro.
            # assert "highlighted" in card
            assert "label" in card
            assert "sell_cost" in card

            # Verify card config has center_key
            assert "center_key" in card["config"]
            assert isinstance(card["config"]["center_key"], str)

            # Verify ability has set field
            assert "set" in card["ability"]
            assert isinstance(card["ability"]["set"], str)

        # Verify we have expected cards from the reference game state
        center_key = [card["config"]["center_key"] for card in shop_jokers["cards"]]
        card_labels = [card["label"] for card in shop_jokers["cards"]]

        # Should contain Burglar joker and Jupiter planet card based on reference
        assert "j_burglar" in center_key
        assert "c_jupiter" in center_key
        assert "Burglar" in card_labels
        assert "Jupiter" in card_labels

    def test_shop_vouchers_structure(self, tcp_client: socket.socket) -> None:
        """Test that shop_vouchers contains expected structure when in shop state."""
        # Get current game state while in shop
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})

        # Verify we're in shop state
        assert game_state["state"] == State.SHOP.value

        # Verify shop_vouchers exists and has correct structure
        assert "shop_vouchers" in game_state
        shop_vouchers = game_state["shop_vouchers"]

        # Verify top-level structure
        assert "cards" in shop_vouchers
        assert "config" in shop_vouchers
        assert isinstance(shop_vouchers["cards"], list)
        assert isinstance(shop_vouchers["config"], dict)

        # Verify config structure
        config = shop_vouchers["config"]
        assert "card_count" in config
        assert "card_limit" in config
        assert isinstance(config["card_count"], int)
        assert isinstance(config["card_limit"], int)

        # Verify each voucher card has required fields
        for card in shop_vouchers["cards"]:
            assert "ability" in card
            assert "config" in card
            assert "cost" in card
            assert "debuff" in card
            assert "facing" in card
            # TODO: Use traditional method for checking shop structure.
            # TODO: continuing a run causes the highlighted field to be vacant
            # TODO: this does not prevent the cards from being selected, seems to be a quirk of balatro.
            # assert "highlighted" in card
            assert "label" in card
            assert "sell_cost" in card

            # Verify card config has center_key (vouchers use center_key not card_key)
            assert "center_key" in card["config"]
            assert isinstance(card["config"]["center_key"], str)

            # Verify ability has set field with "Voucher" value
            assert "set" in card["ability"]
            assert card["ability"]["set"] == "Voucher"

        # Verify we have expected voucher from the reference game state
        center_keys = [card["config"]["center_key"] for card in shop_vouchers["cards"]]
        card_labels = [card["label"] for card in shop_vouchers["cards"]]

        # Should contain Hone voucher based on reference
        assert "v_hone" in center_keys
        assert "Hone" in card_labels

    def test_shop_booster_structure(self, tcp_client: socket.socket) -> None:
        """Test that shop_booster contains expected structure when in shop state."""
        # Get current game state while in shop
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})

        # Verify we're in shop state
        assert game_state["state"] == State.SHOP.value

        # Verify shop_booster exists and has correct structure
        assert "shop_booster" in game_state
        shop_booster = game_state["shop_booster"]

        # Verify top-level structure
        assert "cards" in shop_booster
        assert "config" in shop_booster
        assert isinstance(shop_booster["cards"], list)
        assert isinstance(shop_booster["config"], dict)

        # Verify config structure
        config = shop_booster["config"]
        assert "card_count" in config
        assert "card_limit" in config
        assert isinstance(config["card_count"], int)
        assert isinstance(config["card_limit"], int)

        # Verify each booster card has required fields
        for card in shop_booster["cards"]:
            assert "ability" in card
            assert "config" in card
            assert "cost" in card
            # TODO: Use traditional method for checking shop structure.
            # TODO: continuing a run causes the highlighted field to be vacant
            # TODO: this does not prevent the cards from being selected, seems to be a quirk of balatro.
            # assert "highlighted" in card
            assert "label" in card
            assert "sell_cost" in card

            # Verify card config has center_key
            assert "center_key" in card["config"]
            assert isinstance(card["config"]["center_key"], str)

            # Verify ability has set field with "Booster" value
            assert "set" in card["ability"]
            assert card["ability"]["set"] == "Booster"

        # Verify we have expected booster packs from the reference game state
        center_keys = [card["config"]["center_key"] for card in shop_booster["cards"]]
        card_labels = [card["label"] for card in shop_booster["cards"]]

        # Should contain Buffoon Pack and Jumbo Buffoon Pack based on reference
        assert "p_buffoon_normal_1" in center_keys
        assert "p_buffoon_jumbo_1" in center_keys
        assert "Buffoon Pack" in card_labels
        assert "Jumbo Buffoon Pack" in card_labels

    def test_shop_buy_card(self, tcp_client: socket.socket) -> None:
        """Test buying a card from the shop."""
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        assert game_state["state"] == State.SHOP.value
        assert game_state["shop_jokers"]["cards"][0]["cost"] == 6
        assert game_state["game"]["dollars"] == 10
        # Buy the burglar
        purchase_response = send_and_receive_api_message(
            tcp_client,
            "shop",
            {"action": "buy_card", "index": 0},
        )
        assert purchase_response["state"] == State.SHOP.value
        assert purchase_response["shop_jokers"]["cards"][0]["cost"] == 3
        assert purchase_response["game"]["dollars"] == 4
        assert purchase_response["jokers"]["cards"][0]["cost"] == 6

    # ------------------------------------------------------------------
    # buy_and_use_card
    # ------------------------------------------------------------------

    def test_buy_and_use_card_success(self, tcp_client: socket.socket) -> None:
        """Buy-and-use a consumable card directly from the shop."""

        def _consumables_count(state: dict) -> int:
            consumables = state.get("shop_jokers") or {}
            return len(consumables.get("cards", []) or [])

        before_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        assert before_state["state"] == State.SHOP.value

        # Find a consumable in shop_jokers (Planet/Tarot/Spectral)
        idx = None
        cost = None
        for i, card in enumerate(before_state["shop_jokers"]["cards"]):
            if card["ability"]["set"] in {"Planet", "Tarot", "Spectral"}:
                idx = i
                cost = card["cost"]
                break

        if idx is None:
            pytest.skip("No consumable available in shop to buy_and_use for this seed")

        dollars_before = before_state["game"]["dollars"]
        consumables_before = _consumables_count(before_state)

        after_state = send_and_receive_api_message(
            tcp_client, "shop", {"action": "buy_and_use_card", "index": idx}
        )

        assert after_state["state"] == State.SHOP.value
        assert after_state["game"]["dollars"] == dollars_before - cost
        # Using directly should not add to consumables area
        assert _consumables_count(after_state) == consumables_before

    def test_buy_and_use_card_missing_index(self, tcp_client: socket.socket) -> None:
        """Missing index for buy_and_use_card should raise INVALID_PARAMETER."""
        response = send_and_receive_api_message(
            tcp_client, "shop", {"action": "buy_and_use_card"}
        )
        assert_error_response(
            response,
            "Missing required field: index",
            ["field"],
            ErrorCode.MISSING_ARGUMENTS.value,
        )

    def test_buy_and_use_card_index_out_of_range(
        self, tcp_client: socket.socket
    ) -> None:
        """Index >= len(shop_jokers.cards) should raise PARAMETER_OUT_OF_RANGE."""
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        assert game_state["state"] == State.SHOP.value

        out_of_range_index = len(game_state["shop_jokers"]["cards"])
        response = send_and_receive_api_message(
            tcp_client,
            "shop",
            {"action": "buy_and_use_card", "index": out_of_range_index},
        )
        assert_error_response(
            response,
            "Card index out of range",
            ["index", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_buy_and_use_card_not_affordable(self, tcp_client: socket.socket) -> None:
        """Attempting to buy_and_use a consumable more expensive than current dollars should error."""
        # Reduce dollars first by buying a cheap joker
        _ = send_and_receive_api_message(
            tcp_client, "shop", {"action": "buy_card", "index": 0}
        )

        mid_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        dollars_now = mid_state["game"]["dollars"]

        # Find a consumable still in the shop with cost greater than current dollars
        idx = None
        for i, card in enumerate(mid_state["shop_jokers"]["cards"]):
            if (
                card["ability"]["set"] in {"Planet", "Tarot", "Spectral"}
                and card["cost"] > dollars_now
            ):
                idx = i
                break

        if idx is None:
            pytest.skip(
                "No unaffordable consumable found to test buy_and_use_card error path"
            )

        response = send_and_receive_api_message(
            tcp_client, "shop", {"action": "buy_and_use_card", "index": idx}
        )
        assert_error_response(
            response,
            "Card is not affordable",
            ["index", "cost", "dollars"],
            ErrorCode.INVALID_ACTION.value,
        )

    # ------------------------------------------------------------------
    # reroll shop
    # ------------------------------------------------------------------

    def test_shop_reroll_success(self, tcp_client: socket.socket) -> None:
        """Successful reroll keeps us in shop and updates cards / dollars."""

        # Capture shop state before reroll
        before_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        assert before_state["state"] == State.SHOP.value
        before_keys = [
            c["config"]["center_key"] for c in before_state["shop_jokers"]["cards"]
        ]
        dollars_before = before_state["game"]["dollars"]
        reroll_cost = before_state["game"]["current_round"]["reroll_cost"]

        # Perform the reroll
        after_state = send_and_receive_api_message(
            tcp_client, "shop", {"action": "reroll"}
        )

        # verify state
        assert after_state["state"] == State.SHOP.value
        assert after_state["game"]["dollars"] == dollars_before - reroll_cost
        after_keys = [
            c["config"]["center_key"] for c in after_state["shop_jokers"]["cards"]
        ]
        assert before_keys != after_keys

    def test_shop_reroll_insufficient_dollars(self, tcp_client: socket.socket) -> None:
        """Repeated rerolls eventually raise INVALID_ACTION when too expensive."""

        # Perform rerolls until an error is returned or a reasonable max tries reached
        max_attempts = 10
        for _ in range(max_attempts):
            response = send_and_receive_api_message(
                tcp_client, "shop", {"action": "reroll"}
            )

            # Break when error encountered and validate
            if "error" in response:
                assert_error_response(
                    response,
                    "Not enough dollars to reroll",
                    ["dollars", "reroll_cost"],
                    ErrorCode.INVALID_ACTION.value,
                )
                break
        else:
            pytest.fail("Rerolls did not exhaust dollars within expected attempts")

    # ------------------------------------------------------------------
    # buy_card validation / error scenarios
    # ------------------------------------------------------------------

    def test_buy_card_missing_index(self, tcp_client: socket.socket) -> None:
        """Missing index for buy_card should raise INVALID_PARAMETER."""
        response = send_and_receive_api_message(
            tcp_client,
            "shop",
            {"action": "buy_card"},
        )

        assert_error_response(
            response,
            "Missing required field: index",
            ["field"],
            ErrorCode.MISSING_ARGUMENTS.value,
        )

    def test_buy_card_index_out_of_range(self, tcp_client: socket.socket) -> None:
        """Index >= len(shop_jokers.cards) should raise PARAMETER_OUT_OF_RANGE."""
        # Fetch current shop state to know max index
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        assert game_state["state"] == State.SHOP.value

        out_of_range_index = len(game_state["shop_jokers"]["cards"])
        response = send_and_receive_api_message(
            tcp_client,
            "shop",
            {"action": "buy_card", "index": out_of_range_index},
        )
        assert_error_response(
            response,
            "Card index out of range",
            ["index", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_buy_card_not_affordable(self, tcp_client: socket.socket) -> None:
        """Index >= len(shop_jokers.cards) should raise PARAMETER_OUT_OF_RANGE."""
        # Fetch current shop state to know max index
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {"deck": "Red Deck", "stake": 1, "seed": "OOOO155"},
        )
        send_and_receive_api_message(
            tcp_client,
            "skip_or_select_blind",
            {"action": "select"},
        )
        # Get to shop with fewer than 9 dollars so planet cannot be afforded
        send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [5]},
        )
        send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [5]},
        )
        send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [2, 3, 4, 5]},  # 2 aces are drawn
        )
        send_and_receive_api_message(tcp_client, "cash_out", {})

        # Buy the burglar
        send_and_receive_api_message(
            tcp_client,
            "shop",
            {"action": "buy_card", "index": 0},
        )
        # Fail to buy the jupiter
        game_state = send_and_receive_api_message(
            tcp_client,
            "shop",
            {"action": "buy_card", "index": 0},
        )
        assert_error_response(
            game_state,
            "Card is not affordable",
            ["index", "cost", "dollars"],
            ErrorCode.INVALID_ACTION.value,
        )

    def test_shop_invalid_state_error(self, tcp_client: socket.socket) -> None:
        """Test shop returns error when not in shop state."""
        # Go to menu first to ensure we're not in shop state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

        # Try to use shop when not in shop state - should return error
        response = send_and_receive_api_message(
            tcp_client, "shop", {"action": "next_round"}
        )

        # Verify error response
        assert_error_response(
            response,
            "Cannot select shop action when not in shop",
            ["current_state"],
            ErrorCode.INVALID_GAME_STATE.value,
        )

    def test_redeem_voucher_success(self, tcp_client: socket.socket) -> None:
        """Redeem the first voucher successfully and verify effects."""
        # Capture shop state before redemption
        before_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        assert before_state["state"] == State.SHOP.value
        assert "shop_vouchers" in before_state
        assert before_state["shop_vouchers"]["cards"], "No vouchers available to redeem"

        voucher_cost = before_state["shop_vouchers"]["cards"][0]["cost"]
        dollars_before = before_state["game"]["dollars"]
        discount_before = before_state["game"].get("discount_percent", 0)

        # Redeem the voucher at index 0
        after_state = send_and_receive_api_message(
            tcp_client, "shop", {"action": "redeem_voucher", "index": 0}
        )

        # Verify we remain in shop state
        assert after_state["state"] == State.SHOP.value

        # Dollar count should decrease by voucher cost (cost may be 0 for free vouchers)
        assert after_state["game"]["dollars"] == dollars_before - voucher_cost

        # Discount percent should not decrease; usually increases after redeem
        assert after_state["game"].get("discount_percent", 0) >= discount_before

    def test_redeem_voucher_missing_index(self, tcp_client: socket.socket) -> None:
        """Missing index for redeem_voucher should raise INVALID_PARAMETER."""
        response = send_and_receive_api_message(
            tcp_client, "shop", {"action": "redeem_voucher"}
        )
        assert_error_response(
            response,
            "Missing required field: index",
            ["field"],
            ErrorCode.MISSING_ARGUMENTS.value,
        )

    def test_redeem_voucher_index_out_of_range(self, tcp_client: socket.socket) -> None:
        """Index >= len(shop_vouchers.cards) should raise PARAMETER_OUT_OF_RANGE."""
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        assert game_state["state"] == State.SHOP.value
        out_of_range_index = len(game_state["shop_vouchers"]["cards"])

        response = send_and_receive_api_message(
            tcp_client,
            "shop",
            {"action": "redeem_voucher", "index": out_of_range_index},
        )
        assert_error_response(
            response,
            "Voucher index out of range",
            ["index", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )
