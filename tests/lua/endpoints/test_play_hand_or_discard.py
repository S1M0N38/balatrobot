import socket
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode, State

from ..conftest import assert_error_response, send_and_receive_api_message


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
