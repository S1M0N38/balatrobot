import socket
from pathlib import Path
from typing import Generator

import pytest

from balatrobot.enums import ErrorCode

from ..conftest import (
    assert_error_response,
    prepare_checkpoint,
    send_and_receive_api_message,
)


class TestLoadSave:
    """Tests for the load_save API endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, tcp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Ensure we return to menu after each test."""
        yield
        send_and_receive_api_message(tcp_client, "go_to_menu", {})

    def test_load_save_success(self, tcp_client: socket.socket) -> None:
        """Successfully load a checkpoint and verify a run is active."""
        checkpoint_path = Path(__file__).parent / "checkpoints" / "plasma_deck.jkr"
        game_state = prepare_checkpoint(tcp_client, checkpoint_path)

        # Basic structure validations
        assert isinstance(game_state, dict)
        assert "state" in game_state
        assert isinstance(game_state["state"], int)
        assert "game" in game_state
        assert isinstance(game_state["game"], dict)

    def test_load_save_missing_required_arg(self, tcp_client: socket.socket) -> None:
        """Missing save_path should return an error response."""
        response = send_and_receive_api_message(tcp_client, "load_save", {})
        assert_error_response(
            response,
            "Missing required field: save_path",
            expected_error_code=ErrorCode.INVALID_PARAMETER.value,
        )

    def test_load_save_invalid_path(self, tcp_client: socket.socket) -> None:
        """Invalid path should return error with MISSING_GAME_OBJECT code."""
        response = send_and_receive_api_message(
            tcp_client, "load_save", {"save_path": "nonexistent/save.jkr"}
        )
        assert_error_response(
            response,
            "Failed to load save file",
            expected_context_keys=["save_path"],
            expected_error_code=ErrorCode.MISSING_GAME_OBJECT.value,
        )
