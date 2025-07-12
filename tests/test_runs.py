"""Tests for replaying recorded game runs from JSONL files."""

import json
import socket
from pathlib import Path
from typing import Any, Generator

import pytest
from conftest import send_and_receive_api_message


def get_jsonl_files() -> list[Path]:
    """Get all JSONL files from the runs directory."""
    runs_dir = Path(__file__).parent / "runs"
    return list(runs_dir.glob("*.jsonl"))


def load_jsonl_run(file_path: Path) -> list[dict[str, Any]]:
    """Load a JSONL file and return list of run steps."""
    steps = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                steps.append(json.loads(line))
    return steps


class TestRunReplays:
    """Tests for replaying recorded game runs."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(
        self, udp_client: socket.socket
    ) -> Generator[None, None, None]:
        """Set up and tear down each test method."""
        yield
        send_and_receive_api_message(udp_client, "go_to_menu", {})

    @pytest.mark.parametrize("jsonl_file", get_jsonl_files())
    def test_replay_run(self, udp_client: socket.socket, jsonl_file: Path) -> None:
        """Test replaying a complete run from JSONL file.

        Args:
            udp_client: UDP socket for API communication
            jsonl_file: Path to JSONL file containing recorded run
        """
        steps = load_jsonl_run(jsonl_file)

        for step_num in range(len(steps)):
            current_step = steps[step_num]
            function_call = current_step["function"]

            # Call the API function with recorded parameters
            actual_game_state = send_and_receive_api_message(
                udp_client, function_call["name"], function_call["params"]
            )

            # Compare with the game_state from the next step (if it exists)
            if step_num + 1 < len(steps):
                next_step = steps[step_num + 1]
                expected_game_state = next_step["game_state"]

                # Assert complete game state equality
                assert actual_game_state == expected_game_state, (
                    f"Game state mismatch at step {step_num + 1} in {jsonl_file.name}\n"
                    f"Function: {function_call['name']}({function_call['params']})\n"
                    f"Expected: {expected_game_state}\n"
                    f"Actual: {actual_game_state}"
                )
