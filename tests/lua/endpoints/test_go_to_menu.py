import socket

from balatrobot.enums import State

from ..conftest import send_and_receive_api_message


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
