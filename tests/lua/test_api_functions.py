"""Tests for BalatroBot TCP API game functions."""

import socket
from typing import Generator

import pytest
from conftest import assert_error_response, send_and_receive_api_message

from balatrobot.enums import ErrorCode, State


class TestGetGameState:
    """Tests for the get_game_state API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_get_game_state_response(self, tcp_client: socket.socket) -> None:
        """Test get_game_state message returns valid JSON game state."""
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})
        assert isinstance(game_state, dict)

    def test_game_state_structure(self, tcp_client: socket.socket) -> None:
        """Test that game state contains expected top-level fields."""
        game_state = send_and_receive_api_message(tcp_client, "get_game_state", {})

        assert isinstance(game_state, dict)

        expected_keys = {"state", "game"}
        assert expected_keys.issubset(game_state.keys())
        assert isinstance(game_state["state"], int)
        assert isinstance(game_state["game"], (dict, type(None)))

    def test_game_state_during_run(self, tcp_client: socket.socket) -> None:
        """Test getting game state at different points during a run."""
        # Start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        initial_state = send_and_receive_api_message(
            tcp_client, "start_run", start_run_args
        )
        assert initial_state["state"] == State.BLIND_SELECT.value

        # Get game state again to ensure it's consistent
        current_state = send_and_receive_api_message(tcp_client, "get_game_state", {})

        assert current_state["state"] == State.BLIND_SELECT.value
        assert current_state["state"] == initial_state["state"]


class TestStartRun:
    """Tests for the start_run API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_start_run(self, tcp_client: socket.socket) -> None:
        """Test starting a run and verifying the state."""
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        game_state = send_and_receive_api_message(
            tcp_client, "start_run", start_run_args
        )

        assert game_state["state"] == State.BLIND_SELECT.value

    def test_start_run_with_challenge(self, tcp_client: socket.socket) -> None:
        """Test starting a run with a challenge."""
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": "The Omelette",
            "seed": "EXAMPLE",
        }
        game_state = send_and_receive_api_message(
            tcp_client, "start_run", start_run_args
        )

        assert game_state["state"] == State.BLIND_SELECT.value
        assert len(game_state["jokers"]) == 5  # jokers in The Omelette challenge

    def test_start_run_different_stakes(self, tcp_client: socket.socket) -> None:
        """Test starting runs with different stake levels."""
        for stake in [1, 2, 3]:
            start_run_args = {
                "deck": "Red Deck",
                "stake": stake,
                "challenge": None,
                "seed": "EXAMPLE",
            }
            game_state = send_and_receive_api_message(
                tcp_client, "start_run", start_run_args
            )

            assert game_state["state"] == State.BLIND_SELECT.value

            # Go back to menu for next iteration
            send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_start_run_missing_required_args(self, tcp_client: socket.socket) -> None:
        """Test start_run with missing required arguments."""
        # Missing deck
        incomplete_args = {
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        # Should receive error response
        response = send_and_receive_api_message(
            tcp_client, "start_run", incomplete_args
        )
        assert_error_response(
            response,
            "Missing required field: deck",
            expected_error_code=ErrorCode.INVALID_PARAMETER.value,
        )

    def test_start_run_invalid_deck(self, tcp_client: socket.socket) -> None:
        """Test start_run with invalid deck name."""
        invalid_args = {
            "deck": "Nonexistent Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        # Should receive error response
        response = send_and_receive_api_message(tcp_client, "start_run", invalid_args)
        assert_error_response(
            response, "Invalid deck name", ["deck"], ErrorCode.DECK_NOT_FOUND.value
        )


class TestGoToMenu:
    """Tests for the go_to_menu API endpoint."""

    def test_go_to_menu(self, tcp_client: socket.socket) -> None:
        """Test going to the main menu."""
        game_state = send_and_receive_api_message(tcp_client, "go_to_menu", {})
        assert game_state["state"] == State.MENU.value

    def test_go_to_menu_from_run(self, tcp_client: socket.socket) -> None:
        """Test going to menu from within a run."""
        # First start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        initial_state = send_and_receive_api_message(
            tcp_client, "start_run", start_run_args
        )
        assert initial_state["state"] == State.BLIND_SELECT.value

        # Now go to menu
        menu_state = send_and_receive_api_message(tcp_client, "go_to_menu", {})

        assert menu_state["state"] == State.MENU.value


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


class TestPlayHandOrDiscard:
    """Tests for the play_hand_or_discard API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[dict, None, None]:
        """Set up and tear down each test method."""
        send_and_receive_api_message(
            tcp_client,
            "start_run",
            {
                "deck": "Red Deck",
                "stake": 1,
                "challenge": None,
                "seed": "OOOO155",  # four of a kind in first hand
            },
        )
        game_state = send_and_receive_api_message(
            tcp_client,
            "skip_or_select_blind",
            {"action": "select"},
        )
        assert game_state["state"] == State.SELECTING_HAND.value
        yield game_state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    @pytest.mark.parametrize(
        "cards,expected_new_cards",
        [
            ([7, 6, 5, 4, 3], 5),  # Test playing five cards
            ([0], 1),  # Test playing one card
        ],
    )
    def test_play_hand(
        self,
        tcp_client: socket.socket,
        setup_and_teardown: dict,
        cards: list[int],
        expected_new_cards: int,
    ) -> None:
        """Test playing a hand with different numbers of cards."""
        initial_game_state = setup_and_teardown
        play_hand_args = {"action": "play_hand", "cards": cards}

        init_card_keys = [
            card["config"]["card_key"] for card in initial_game_state["hand"]["cards"]
        ]
        played_hand_keys = [
            initial_game_state["hand"]["cards"][i]["config"]["card_key"]
            for i in play_hand_args["cards"]
        ]
        game_state = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", play_hand_args
        )
        final_card_keys = [
            card["config"]["card_key"] for card in game_state["hand"]["cards"]
        ]
        assert game_state["state"] == State.SELECTING_HAND.value
        assert game_state["game"]["hands_played"] == 1
        assert len(set(final_card_keys) - set(init_card_keys)) == expected_new_cards
        assert set(final_card_keys) & set(played_hand_keys) == set()

    def test_play_hand_winning(self, tcp_client: socket.socket) -> None:
        """Test playing a winning hand (four of a kind)"""
        play_hand_args = {"action": "play_hand", "cards": [0, 1, 2, 3]}
        game_state = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", play_hand_args
        )
        assert game_state["state"] == State.ROUND_EVAL.value

    def test_play_hands_losing(self, tcp_client: socket.socket) -> None:
        """Test playing a series of losing hands and reach Main menu again."""
        for _ in range(4):
            game_state = send_and_receive_api_message(
                tcp_client,
                "play_hand_or_discard",
                {"action": "play_hand", "cards": [0]},
            )
        assert game_state["state"] == State.GAME_OVER.value

    def test_play_hand_or_discard_invalid_cards(
        self, tcp_client: socket.socket
    ) -> None:
        """Test playing a hand with invalid card indices returns error."""
        play_hand_args = {"action": "play_hand", "cards": [10, 11, 12, 13, 14]}
        response = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", play_hand_args
        )

        # Should receive error response for invalid card index
        assert_error_response(
            response,
            "Invalid card index",
            ["card_index", "hand_size"],
            ErrorCode.INVALID_CARD_INDEX.value,
        )

    def test_play_hand_invalid_action(self, tcp_client: socket.socket) -> None:
        """Test playing a hand with invalid action returns error."""
        play_hand_args = {"action": "invalid_action", "cards": [0, 1, 2, 3, 4]}
        response = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", play_hand_args
        )

        # Should receive error response for invalid action
        assert_error_response(
            response,
            "Invalid action for play_hand_or_discard",
            ["action"],
            ErrorCode.INVALID_ACTION.value,
        )

    @pytest.mark.parametrize(
        "cards,expected_new_cards",
        [
            ([0, 1, 2, 3, 4], 5),  # Test discarding five cards
            ([0], 1),  # Test discarding one card
        ],
    )
    def test_discard(
        self,
        tcp_client: socket.socket,
        setup_and_teardown: dict,
        cards: list[int],
        expected_new_cards: int,
    ) -> None:
        """Test discarding with different numbers of cards."""
        initial_game_state = setup_and_teardown
        init_discards_left = initial_game_state["game"]["current_round"][
            "discards_left"
        ]
        discard_hand_args = {"action": "discard", "cards": cards}

        init_card_keys = [
            card["config"]["card_key"] for card in initial_game_state["hand"]["cards"]
        ]
        discarded_hand_keys = [
            initial_game_state["hand"]["cards"][i]["config"]["card_key"]
            for i in discard_hand_args["cards"]
        ]
        game_state = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", discard_hand_args
        )
        final_card_keys = [
            card["config"]["card_key"] for card in game_state["hand"]["cards"]
        ]
        assert game_state["state"] == State.SELECTING_HAND.value
        assert game_state["game"]["hands_played"] == 0
        assert (
            game_state["game"]["current_round"]["discards_left"]
            == init_discards_left - 1
        )
        assert len(set(final_card_keys) - set(init_card_keys)) == expected_new_cards
        assert set(final_card_keys) & set(discarded_hand_keys) == set()

    def test_try_to_discard_when_no_discards_left(
        self, tcp_client: socket.socket
    ) -> None:
        """Test trying to discard when no discards are left."""
        for _ in range(4):
            game_state = send_and_receive_api_message(
                tcp_client,
                "play_hand_or_discard",
                {"action": "discard", "cards": [0]},
            )
        assert game_state["state"] == State.SELECTING_HAND.value
        assert game_state["game"]["hands_played"] == 0
        assert game_state["game"]["current_round"]["discards_left"] == 0

        response = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "discard", "cards": [0]},
        )

        # Should receive error response for no discards left
        assert_error_response(
            response,
            "No discards left to perform discard",
            ["discards_left"],
            ErrorCode.NO_DISCARDS_LEFT.value,
        )

    def test_play_hand_or_discard_empty_cards(self, tcp_client: socket.socket) -> None:
        """Test playing a hand with no cards returns error."""
        play_hand_args = {"action": "play_hand", "cards": []}
        response = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", play_hand_args
        )

        # Should receive error response for no cards
        assert_error_response(
            response,
            "Invalid number of cards",
            ["cards_count", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_play_hand_or_discard_too_many_cards(
        self, tcp_client: socket.socket
    ) -> None:
        """Test playing a hand with more than 5 cards returns error."""
        play_hand_args = {"action": "play_hand", "cards": [0, 1, 2, 3, 4, 5]}
        response = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", play_hand_args
        )

        # Should receive error response for too many cards
        assert_error_response(
            response,
            "Invalid number of cards",
            ["cards_count", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_discard_empty_cards(self, tcp_client: socket.socket) -> None:
        """Test discarding with no cards returns error."""
        discard_args = {"action": "discard", "cards": []}
        response = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", discard_args
        )

        # Should receive error response for no cards
        assert_error_response(
            response,
            "Invalid number of cards",
            ["cards_count", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_discard_too_many_cards(self, tcp_client: socket.socket) -> None:
        """Test discarding with more than 5 cards returns error."""
        discard_args = {"action": "discard", "cards": [0, 1, 2, 3, 4, 5, 6]}
        response = send_and_receive_api_message(
            tcp_client, "play_hand_or_discard", discard_args
        )

        # Should receive error response for too many cards
        assert_error_response(
            response,
            "Invalid number of cards",
            ["cards_count", "valid_range"],
            ErrorCode.PARAMETER_OUT_OF_RANGE.value,
        )

    def test_play_hand_or_discard_invalid_state(
        self, tcp_client: socket.socket
    ) -> None:
        """Test that play_hand_or_discard returns error when not in selecting hand state."""
        # Go to menu to ensure we're not in selecting hand state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

        # Try to play hand when not in selecting hand state
        error_response = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3, 4]},
        )

        # Verify error response
        assert_error_response(
            error_response,
            "Cannot play hand or discard when not selecting hand",
            ["current_state"],
            ErrorCode.INVALID_GAME_STATE.value,
        )


class TestShop:
    """Tests for the shop API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        # Start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "OOOO155",  # four of a kind in first hand
        }
        send_and_receive_api_message(tcp_client, "start_run", start_run_args)

        # Select blind
        send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        # Play a winning hand (four of a kind) to reach shop
        game_state = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3]},
        )
        assert game_state["state"] == State.ROUND_EVAL.value

        # Cash out to reach shop
        game_state = send_and_receive_api_message(tcp_client, "cash_out", {})
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
            assert "highlighted" in card
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
            assert "highlighted" in card
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

    def test_shop_buy_card(self, tcp_client: socket.socket) -> None:
        """Test buying a card from shop."""
        # TODO: Implement test
        ...

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


class TestCashOut:
    """Tests for the cash_out API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        # Start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "OOOO155",  # four of a kind in first hand
        }
        send_and_receive_api_message(tcp_client, "start_run", start_run_args)

        # Select blind
        send_and_receive_api_message(
            tcp_client, "skip_or_select_blind", {"action": "select"}
        )

        # Play a winning hand (four of a kind) to reach shop
        game_state = send_and_receive_api_message(
            tcp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3]},
        )
        assert game_state["state"] == State.ROUND_EVAL.value
        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_cash_out_success(self, tcp_client: socket.socket) -> None:
        """Test successful cash out returns to shop state."""
        # Cash out should transition to shop state
        game_state = send_and_receive_api_message(tcp_client, "cash_out", {})

        # Verify we're in shop state after cash out
        assert game_state["state"] == State.SHOP.value

    def test_cash_out_invalid_state_error(self, tcp_client: socket.socket) -> None:
        """Test cash out returns error when not in shop state."""
        # Go to menu first to ensure we're not in shop state
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

        # Try to cash out when not in shop - should return error
        response = send_and_receive_api_message(tcp_client, "cash_out", {})

        # Verify error response
        assert_error_response(
            response,
            "Cannot cash out when not in round evaluation",
            ["current_state"],
            ErrorCode.INVALID_GAME_STATE.value,
        )
