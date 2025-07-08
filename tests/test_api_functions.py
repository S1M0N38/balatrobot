"""Tests for BalatroBot UDP API game functions."""

import socket

import pytest
from conftest import HOST, PORT, receive_api_message, send_api_message, teardown_test

from balatrobot.enums import State


def test_get_game_state_response(udp_client: socket.socket) -> None:
    """Test get_game_state message returns valid JSON game state."""
    send_api_message(udp_client, "get_game_state", {})

    game_state = receive_api_message(udp_client)
    assert isinstance(game_state, dict)


def test_game_state_structure(udp_client: socket.socket) -> None:
    """Test that game state contains expected top-level fields."""
    send_api_message(udp_client, "get_game_state", {})

    game_state = receive_api_message(udp_client)

    assert isinstance(game_state, dict)

    expected_keys = {"state", "game"}
    assert expected_keys.issubset(game_state.keys())
    assert isinstance(game_state["state"], int)
    assert isinstance(game_state["game"], (dict, type(None)))


def test_start_run(udp_client: socket.socket) -> None:
    """Test starting a run and verifying the state."""
    start_run_args = {
        "deck": "Red Deck",
        "stake": 1,
        "challenge": None,
        "seed": "EXAMPLE",
    }
    send_api_message(udp_client, "start_run", start_run_args)
    game_state = receive_api_message(udp_client)

    assert game_state["state"] == State.BLIND_SELECT.value

    teardown_test(udp_client)


def test_start_run_with_challenge(udp_client: socket.socket) -> None:
    """Test starting a run with a challenge."""
    start_run_args = {
        "deck": "Red Deck",
        "stake": 1,
        "challenge": "The Omelette",
        "seed": "CHALLENGE_TEST",
    }
    send_api_message(udp_client, "start_run", start_run_args)
    game_state = receive_api_message(udp_client)

    assert game_state["state"] == State.BLIND_SELECT.value
    assert len(game_state["jokers"]) == 5  # jokers in The Omelette challenge

    teardown_test(udp_client)


def test_start_run_different_stakes(udp_client: socket.socket) -> None:
    """Test starting runs with different stake levels."""
    for stake in [1, 2, 3]:
        start_run_args = {
            "deck": "Red Deck",
            "stake": stake,
            "challenge": None,
            "seed": f"STAKE_{stake}",
        }
        send_api_message(udp_client, "start_run", start_run_args)

        game_state = receive_api_message(udp_client)

        assert game_state["state"] == State.BLIND_SELECT.value

        # Go back to menu
        teardown_test(udp_client)


def test_select_blind(udp_client: socket.socket) -> None:
    """Test selecting a blind during the blind selection phase."""
    # First start a run to get to blind select state
    start_run_args = {
        "deck": "Red Deck",
        "stake": 1,
        "challenge": None,
        "seed": "SELECT_BLIND",
    }
    send_api_message(udp_client, "start_run", start_run_args)

    # Wait for the run to start and reach blind select state
    game_state = receive_api_message(udp_client)
    assert game_state["state"] == State.BLIND_SELECT.value

    # Now select the blind
    select_blind_args = {"action": "select"}
    send_api_message(udp_client, "skip_or_select_blind", select_blind_args)

    # Wait for response after blind selection
    game_state = receive_api_message(udp_client)

    # Verify we get a valid game state response
    assert game_state["state"] == State.SELECTING_HAND.value

    # Assert that there are 8 cards in the hand
    assert len(game_state["hand"]) == 8

    # Go back to menu
    teardown_test(udp_client)


def test_skip_blind(udp_client: socket.socket) -> None:
    """Test skipping a blind during the blind selection phase."""
    # First start a run to get to blind select state
    start_run_args = {
        "deck": "Red Deck",
        "stake": 1,
        "challenge": None,
        "seed": "SKIP_BLIND",
    }
    send_api_message(udp_client, "start_run", start_run_args)

    # Wait for the run to start and reach blind select state
    game_state = receive_api_message(udp_client)
    assert game_state["state"] == State.BLIND_SELECT.value

    # Now skip the blind
    skip_blind_args = {"action": "skip"}
    send_api_message(udp_client, "skip_or_select_blind", skip_blind_args)

    # Wait for response after blind skip
    game_state = receive_api_message(udp_client)

    # # Verify we get a valid game state response
    # assert game_state["state"] == State.BLIND_SELECT.value

    # Go back to menu
    teardown_test(udp_client)


def test_invalid_blind_action(udp_client: socket.socket) -> None:
    """Test that invalid blind action arguments are handled properly."""
    # First start a run to get to blind select state
    start_run_args = {
        "deck": "Red Deck",
        "stake": 1,
        "challenge": None,
        "seed": "INVALID_ACTION",
    }
    send_api_message(udp_client, "start_run", start_run_args)

    # Wait for the run to start and reach blind select state
    game_state = receive_api_message(udp_client)
    assert game_state["state"] == State.BLIND_SELECT.value

    # Send invalid action
    invalid_args = {"action": "invalid_action"}
    send_api_message(udp_client, "skip_or_select_blind", invalid_args)

    # Should receive error response
    error_response = receive_api_message(udp_client)

    # Verify error response
    assert isinstance(error_response, dict)
    assert "error" in error_response
    assert "Invalid action arg" in error_response["error"]

    # Go back to menu
    teardown_test(udp_client)


def test_game_state_during_run(udp_client: socket.socket) -> None:
    """Test getting game state at different points during a run."""
    # Start a run
    start_run_args = {
        "deck": "Red Deck",
        "stake": 1,
        "challenge": None,
        "seed": "STATE_TEST",
    }
    send_api_message(udp_client, "start_run", start_run_args)

    # Get initial state
    initial_state = receive_api_message(udp_client)
    assert initial_state["state"] == State.BLIND_SELECT.value

    # Get game state again to ensure it's consistent
    send_api_message(udp_client, "get_game_state", {})
    current_state = receive_api_message(udp_client)

    assert current_state["state"] == State.BLIND_SELECT.value
    assert current_state["state"] == initial_state["state"]

    # Go back to menu
    teardown_test(udp_client)


def test_start_run_missing_required_args(udp_client: socket.socket) -> None:
    """Test start_run with missing required arguments."""
    # Missing deck
    incomplete_args = {
        "stake": 1,
        "challenge": None,
        "seed": "EXAMPLE",
    }
    send_api_message(udp_client, "start_run", incomplete_args)

    # Should receive error response
    response = receive_api_message(udp_client)
    assert isinstance(response, dict)
    assert "error" in response
    assert "Invalid deck arg" in response["error"]


def test_start_run_invalid_deck(udp_client: socket.socket) -> None:
    """Test start_run with invalid deck name."""
    invalid_args = {
        "deck": "Nonexistent Deck",
        "stake": 1,
        "challenge": None,
        "seed": "EXAMPLE",
    }
    send_api_message(udp_client, "start_run", invalid_args)

    # Should receive error response
    response = receive_api_message(udp_client)
    assert isinstance(response, dict)
    assert "error" in response
    assert "Invalid deck arg" in response["error"]


def test_go_to_menu(udp_client: socket.socket) -> None:
    """Test going to the main menu."""
    send_api_message(udp_client, "go_to_menu", {})

    game_state = receive_api_message(udp_client)
    assert game_state["state"] == State.MENU.value


def test_go_to_menu_from_run(udp_client: socket.socket) -> None:
    """Test going to menu from within a run."""
    # First start a run
    start_run_args = {
        "deck": "Red Deck",
        "stake": 1,
        "challenge": None,
        "seed": "MENU_TEST",
    }
    send_api_message(udp_client, "start_run", start_run_args)

    # Wait for the run to start
    initial_state = receive_api_message(udp_client)
    assert initial_state["state"] == State.BLIND_SELECT.value

    # Now go to menu
    send_api_message(udp_client, "go_to_menu", {})

    # Wait for the game to confirm we've reached the menu
    menu_state = receive_api_message(udp_client)

    assert menu_state["state"] == State.MENU.value
