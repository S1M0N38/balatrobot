"""Tests for BalatroBot UDP API game functions."""

import socket
from typing import Generator

import pytest
from conftest import send_and_receive_api_message

from balatrobot.enums import State


class TestGetGameState:
    """Tests for the get_game_state API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, udp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        yield
        send_and_receive_api_message(udp_client, "go_to_menu", {})

    def test_get_game_state_response(self, udp_client: socket.socket) -> None:
        """Test get_game_state message returns valid JSON game state."""
        game_state = send_and_receive_api_message(udp_client, "get_game_state", {})
        assert isinstance(game_state, dict)

    def test_game_state_structure(self, udp_client: socket.socket) -> None:
        """Test that game state contains expected top-level fields."""
        game_state = send_and_receive_api_message(udp_client, "get_game_state", {})

        assert isinstance(game_state, dict)

        expected_keys = {"state", "game"}
        assert expected_keys.issubset(game_state.keys())
        assert isinstance(game_state["state"], int)
        assert isinstance(game_state["game"], (dict, type(None)))

    def test_game_state_during_run(self, udp_client: socket.socket) -> None:
        """Test getting game state at different points during a run."""
        # Start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        initial_state = send_and_receive_api_message(
            udp_client, "start_run", start_run_args
        )
        assert initial_state["state"] == State.BLIND_SELECT.value

        # Get game state again to ensure it's consistent
        current_state = send_and_receive_api_message(udp_client, "get_game_state", {})

        assert current_state["state"] == State.BLIND_SELECT.value
        assert current_state["state"] == initial_state["state"]


class TestStartRun:
    """Tests for the start_run API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, udp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        yield
        send_and_receive_api_message(udp_client, "go_to_menu", {})

    def test_start_run(self, udp_client: socket.socket) -> None:
        """Test starting a run and verifying the state."""
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        game_state = send_and_receive_api_message(
            udp_client, "start_run", start_run_args
        )

        assert game_state["state"] == State.BLIND_SELECT.value

    def test_start_run_with_challenge(self, udp_client: socket.socket) -> None:
        """Test starting a run with a challenge."""
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": "The Omelette",
            "seed": "EXAMPLE",
        }
        game_state = send_and_receive_api_message(
            udp_client, "start_run", start_run_args
        )

        assert game_state["state"] == State.BLIND_SELECT.value
        assert len(game_state["jokers"]) == 5  # jokers in The Omelette challenge

    def test_start_run_different_stakes(self, udp_client: socket.socket) -> None:
        """Test starting runs with different stake levels."""
        for stake in [1, 2, 3]:
            start_run_args = {
                "deck": "Red Deck",
                "stake": stake,
                "challenge": None,
                "seed": "EXAMPLE",
            }
            game_state = send_and_receive_api_message(
                udp_client, "start_run", start_run_args
            )

            assert game_state["state"] == State.BLIND_SELECT.value

            # Go back to menu for next iteration
            send_and_receive_api_message(udp_client, "go_to_menu", {})

    def test_start_run_missing_required_args(self, udp_client: socket.socket) -> None:
        """Test start_run with missing required arguments."""
        # Missing deck
        incomplete_args = {
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        # Should receive error response
        response = send_and_receive_api_message(
            udp_client, "start_run", incomplete_args
        )
        assert isinstance(response, dict)
        assert "error" in response
        assert "Invalid deck arg" in response["error"]

    def test_start_run_invalid_deck(self, udp_client: socket.socket) -> None:
        """Test start_run with invalid deck name."""
        invalid_args = {
            "deck": "Nonexistent Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        # Should receive error response
        response = send_and_receive_api_message(udp_client, "start_run", invalid_args)
        assert isinstance(response, dict)
        assert "error" in response
        assert "Invalid deck arg" in response["error"]


class TestGoToMenu:
    """Tests for the go_to_menu API endpoint."""

    def test_go_to_menu(self, udp_client: socket.socket) -> None:
        """Test going to the main menu."""
        game_state = send_and_receive_api_message(udp_client, "go_to_menu", {})
        assert game_state["state"] == State.MENU.value

    def test_go_to_menu_from_run(self, udp_client: socket.socket) -> None:
        """Test going to menu from within a run."""
        # First start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        initial_state = send_and_receive_api_message(
            udp_client, "start_run", start_run_args
        )
        assert initial_state["state"] == State.BLIND_SELECT.value

        # Now go to menu
        menu_state = send_and_receive_api_message(udp_client, "go_to_menu", {})

        assert menu_state["state"] == State.MENU.value


class TestSkipOrSelectBlind:
    """Tests for the skip_or_select_blind API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, udp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        game_state = send_and_receive_api_message(
            udp_client, "start_run", start_run_args
        )
        assert game_state["state"] == State.BLIND_SELECT.value
        yield
        send_and_receive_api_message(udp_client, "go_to_menu", {})

    def test_select_blind(self, udp_client: socket.socket) -> None:
        """Test selecting a blind during the blind selection phase."""
        # Select the blind
        select_blind_args = {"action": "select"}
        game_state = send_and_receive_api_message(
            udp_client, "skip_or_select_blind", select_blind_args
        )

        # Verify we get a valid game state response
        assert game_state["state"] == State.SELECTING_HAND.value

        # Assert that there are 8 cards in the hand
        assert len(game_state["hand"]) == 8

    def test_skip_blind(self, udp_client: socket.socket) -> None:
        """Test skipping a blind during the blind selection phase."""
        # Skip the blind
        skip_blind_args = {"action": "skip"}
        game_state = send_and_receive_api_message(
            udp_client, "skip_or_select_blind", skip_blind_args
        )

        # Verify we get a valid game state response
        assert game_state["state"] == State.BLIND_SELECT.value

        # Assert that the current blind is "Big", the "Small" blind was skipped
        assert game_state["game"]["blind_on_deck"] == "Big"

    def test_invalid_blind_action(self, udp_client: socket.socket) -> None:
        """Test that invalid blind action arguments are handled properly."""
        # Should receive error response
        error_response = send_and_receive_api_message(
            udp_client, "skip_or_select_blind", {"action": "invalid_action"}
        )

        # Verify error response
        assert isinstance(error_response, dict)
        assert "error" in error_response
        assert "Invalid action arg" in error_response["error"]


class TestPlayHandOrDiscard:
    """Tests for the play_hand_or_discard API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, udp_client: socket.socket
    ) -> Generator[dict, None, None]:
        """Set up and tear down each test method."""
        send_and_receive_api_message(
            udp_client,
            "start_run",
            {
                "deck": "Red Deck",
                "stake": 1,
                "challenge": None,
                "seed": "OOOO155",  # four of a kind in first hand
            },
        )
        game_state = send_and_receive_api_message(
            udp_client,
            "skip_or_select_blind",
            {"action": "select"},
        )
        assert game_state["state"] == State.SELECTING_HAND.value
        yield game_state
        send_and_receive_api_message(udp_client, "go_to_menu", {})

    @pytest.mark.parametrize(
        "cards,expected_new_cards",
        [
            ([7, 6, 5, 4, 3], 5),  # Test playing five cards
            ([0], 1),  # Test playing one card
        ],
    )
    def test_play_hand(
        self,
        udp_client: socket.socket,
        setup_and_teardown: dict,
        cards: list[int],
        expected_new_cards: int,
    ) -> None:
        """Test playing a hand with different numbers of cards."""
        initial_game_state = setup_and_teardown
        play_hand_args = {"action": "play_hand", "cards": cards}

        init_card_keys = [
            card["config"]["card"]["card_key"] for card in initial_game_state["hand"]
        ]
        played_hand_keys = [
            initial_game_state["hand"][i]["config"]["card"]["card_key"]
            for i in play_hand_args["cards"]
        ]
        game_state = send_and_receive_api_message(
            udp_client, "play_hand_or_discard", play_hand_args
        )
        final_card_keys = [
            card["config"]["card"]["card_key"] for card in game_state["hand"]
        ]
        assert game_state["state"] == State.SELECTING_HAND.value
        assert game_state["game"]["hands_played"] == 1
        assert len(set(final_card_keys) - set(init_card_keys)) == expected_new_cards
        assert set(final_card_keys) & set(played_hand_keys) == set()

    def test_play_hand_winning(self, udp_client: socket.socket) -> None:
        """Test playing a winning hand (four of a kind)"""
        play_hand_args = {"action": "play_hand", "cards": [0, 1, 2, 3]}
        game_state = send_and_receive_api_message(
            udp_client, "play_hand_or_discard", play_hand_args
        )
        assert game_state["state"] == State.ROUND_EVAL.value

    def test_play_hands_losing(self, udp_client: socket.socket) -> None:
        """Test playing a series of losing hands and reach Main menu again."""
        for _ in range(4):
            game_state = send_and_receive_api_message(
                udp_client,
                "play_hand_or_discard",
                {"action": "play_hand", "cards": [0]},
            )
        assert game_state["state"] == State.GAME_OVER.value

    def test_play_hand_or_discard_invalid_cards(
        self, udp_client: socket.socket
    ) -> None:
        """Test playing a hand with invalid card indices returns error."""
        play_hand_args = {"action": "play_hand", "cards": [10, 11, 12, 13, 14]}
        response = send_and_receive_api_message(
            udp_client, "play_hand_or_discard", play_hand_args
        )

        # Should receive error response for invalid card index
        assert isinstance(response, dict)
        assert "error" in response
        assert "Invalid card index" in response["error"]

    def test_play_hand_invalid_action(self, udp_client: socket.socket) -> None:
        """Test playing a hand with invalid action returns error."""
        play_hand_args = {"action": "invalid_action", "cards": [0, 1, 2, 3, 4]}
        response = send_and_receive_api_message(
            udp_client, "play_hand_or_discard", play_hand_args
        )

        # Should receive error response for invalid action
        assert isinstance(response, dict)
        assert "error" in response
        assert "Invalid action arg" in response["error"]

    @pytest.mark.parametrize(
        "cards,expected_new_cards",
        [
            ([0, 1, 2, 3, 4], 5),  # Test discarding five cards
            ([0], 1),  # Test discarding one card
        ],
    )
    def test_discard(
        self,
        udp_client: socket.socket,
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
            card["config"]["card"]["card_key"] for card in initial_game_state["hand"]
        ]
        discarded_hand_keys = [
            initial_game_state["hand"][i]["config"]["card"]["card_key"]
            for i in discard_hand_args["cards"]
        ]
        game_state = send_and_receive_api_message(
            udp_client, "play_hand_or_discard", discard_hand_args
        )
        final_card_keys = [
            card["config"]["card"]["card_key"] for card in game_state["hand"]
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
        self, udp_client: socket.socket
    ) -> None:
        """Test trying to discard when no discards are left."""
        for _ in range(4):
            game_state = send_and_receive_api_message(
                udp_client,
                "play_hand_or_discard",
                {"action": "discard", "cards": [0]},
            )
        assert game_state["state"] == State.SELECTING_HAND.value
        assert game_state["game"]["hands_played"] == 0
        assert game_state["game"]["current_round"]["discards_left"] == 0

        response = send_and_receive_api_message(
            udp_client,
            "play_hand_or_discard",
            {"action": "discard", "cards": [0]},
        )

        # Should receive error response for no discards left
        assert isinstance(response, dict)
        assert "error" in response
        assert "No discards left" in response["error"]


class TestCashOut:
    """Tests for the cash_out API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, udp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        # Start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "OOOO155",  # four of a kind in first hand
        }
        send_and_receive_api_message(udp_client, "start_run", start_run_args)

        # Select blind
        send_and_receive_api_message(
            udp_client, "skip_or_select_blind", {"action": "select"}
        )

        # Play a winning hand (four of a kind) to reach shop
        game_state = send_and_receive_api_message(
            udp_client,
            "play_hand_or_discard",
            {"action": "play_hand", "cards": [0, 1, 2, 3]},
        )
        assert game_state["state"] == State.ROUND_EVAL.value
        yield
        send_and_receive_api_message(udp_client, "go_to_menu", {})

    def test_cash_out_success(self, udp_client: socket.socket) -> None:
        """Test successful cash out returns to shop state."""
        # Cash out should transition to shop state
        game_state = send_and_receive_api_message(udp_client, "cash_out", {})

        # Verify we're in shop state after cash out
        assert game_state["state"] == State.SHOP.value

    def test_cash_out_invalid_state_error(self, udp_client: socket.socket) -> None:
        """Test cash out returns error when not in shop state."""
        # Go to menu first to ensure we're not in shop state
        send_and_receive_api_message(udp_client, "go_to_menu", {})

        # Try to cash out when not in shop - should return error
        response = send_and_receive_api_message(udp_client, "cash_out", {})

        # Verify error response
        assert isinstance(response, dict)
        assert "error" in response
        assert "Cannot cash out when not in shop" in response["error"]
        assert "state" in response
