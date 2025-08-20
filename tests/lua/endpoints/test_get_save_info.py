import socket
from typing import Generator

import pytest

from ..conftest import send_and_receive_api_message


class TestGetSaveInfo:
    """Tests for the get_save_info API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Ensure we return to menu after each test."""
        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_get_save_info_response(self, tcp_client: socket.socket) -> None:
        """Basic sanity check that the endpoint returns a dict."""
        save_info = send_and_receive_api_message(tcp_client, "get_save_info", {})
        assert isinstance(save_info, dict)

    def test_save_info_structure(self, tcp_client: socket.socket) -> None:
        """Validate expected keys and types are present in the response."""
        save_info = send_and_receive_api_message(tcp_client, "get_save_info", {})

        # Required top-level keys
        expected_keys = {
            "profile_path",
            "save_directory",
            "save_file_path",
            "has_active_run",
            "save_exists",
        }
        assert expected_keys.issubset(save_info.keys())

        # Types
        assert isinstance(save_info["has_active_run"], bool)
        assert isinstance(save_info["save_exists"], bool)
        assert (
            # The save profile is always an index (1-3)
            isinstance(save_info.get("profile_path"), (int, type(None)))
            and isinstance(save_info.get("save_directory"), (str, type(None)))
            and isinstance(save_info.get("save_file_path"), (str, type(None)))
        )

        # If a path is present, it should reference the save file
        if save_info.get("save_file_path"):
            assert "save.jkr" in save_info["save_file_path"]

    def test_has_active_run_flag(self, tcp_client: socket.socket) -> None:
        """has_active_run should be False at menu and True after starting a run."""
        info_before = send_and_receive_api_message(tcp_client, "get_save_info", {})
        assert isinstance(info_before["has_active_run"], bool)

        # Start a run
        start_run_args = {
            "deck": "Red Deck",
            "stake": 1,
            "challenge": None,
            "seed": "EXAMPLE",
        }
        send_and_receive_api_message(tcp_client, "start_run", start_run_args)

        info_during = send_and_receive_api_message(tcp_client, "get_save_info", {})
        assert info_during["has_active_run"] is True
