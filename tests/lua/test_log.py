"""Tests logging of game states to JSONL files."""

import copy
import json
import time
from pathlib import Path
from typing import Any

import pytest
from deepdiff import DeepDiff

from balatrobot.client import BalatroClient


def get_jsonl_files() -> list[Path]:
    """Get all JSONL files from the runs directory."""
    runs_dir = Path(__file__).parent.parent / "runs"
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


def normalize_step(step: dict[str, Any]) -> dict[str, Any]:
    """Normalize a step by removing non-deterministic fields."""
    normalized = copy.deepcopy(step)

    # Remove timestamp as it's non-deterministic
    normalized.pop("timestamp_ms", None)

    # Remove log_path from start_run function arguments as it's non-deterministic
    if "function" in normalized and normalized["function"]["name"] == "start_run":
        if "arguments" in normalized["function"]:
            normalized["function"]["arguments"].pop("log_path", None)

    # Remove non-deterministic fields from game states
    for state_key in ["game_state_before", "game_state_after"]:
        if state_key in normalized:
            game_state = normalized[state_key]
            if "hand" in game_state and "cards" in game_state["hand"]:
                for card in game_state["hand"]["cards"]:
                    card.pop("highlighted", None)
                    card.pop("sort_id", None)

    # we don't care about the game_state_before when starting a run
    if step.get("function", {}).get("name") == "start_run":
        normalized.pop("game_state_before", None)

    return normalized


def assert_steps_equal(
    actual: dict[str, Any], expected: dict[str, Any], context: str = ""
):
    """Assert two steps are equal with clear diff output."""
    normalized_actual = normalize_step(actual)
    normalized_expected = normalize_step(expected)

    diff = DeepDiff(
        normalized_actual,
        normalized_expected,
        ignore_order=True,
        verbose_level=2,
    )

    if diff:
        error_msg = "Steps are not equal"
        if context:
            error_msg += f" ({context})"
        error_msg += f"\n\n{diff.pretty()}"
        pytest.fail(error_msg)


class TestLog:
    """Tests for the log module."""

    @pytest.fixture(scope="session", params=get_jsonl_files())
    def replay_logs(self, request, tmp_path_factory) -> tuple[Path, Path, Path]:
        """Fixture that replays a run and generates two JSONL log files.

        Returns:
            Tuple of (original_jsonl_path, lua_generated_path, python_generated_path)
        """
        original_jsonl: Path = request.param

        # Create temporary file paths
        tmp_path = tmp_path_factory.mktemp("replay_logs")
        base_name = original_jsonl.stem
        lua_log_path = tmp_path / f"{base_name}_lua.jsonl"
        python_log_path = tmp_path / f"{base_name}_python.jsonl"

        print(
            "\nJSONL files:\n"
            f"- original: {original_jsonl}\n"
            f"- lua: {lua_log_path}\n"
            f"- python: {python_log_path}\n"
        )

        # Load original steps
        original_steps = load_jsonl_run(original_jsonl)

        with BalatroClient() as client:
            # Initialize game state
            current_state = client.send_message("go_to_menu", {})

            python_log_entries = []

            # Process all steps
            for step in original_steps:
                function_call = step["function"]

                # The current state becomes the "before" state for this function call
                game_state_before = current_state

                # For start_run, we need to add the log_path parameter to trigger Lua logging
                if function_call["name"] == "start_run":
                    call_args = function_call["arguments"].copy()
                    call_args["log_path"] = str(lua_log_path)
                else:
                    call_args = function_call["arguments"]

                # Call the function and get the new state
                current_state = client.send_message(function_call["name"], call_args)

                # Create Python log entry (use original arguments, not modified ones)
                log_entry = {
                    "timestamp_ms": int(time.time_ns() // 1_000_000),
                    "function": function_call,
                    "game_state_before": game_state_before,
                    "game_state_after": current_state,
                }
                python_log_entries.append(log_entry)

            # Write Python log file
            with open(python_log_path, "w") as f:
                for entry in python_log_entries:
                    f.write(json.dumps(entry, sort_keys=True) + "\n")

        return original_jsonl, lua_log_path, python_log_path

    def test_compare_lua_logs_with_original_run(
        self, replay_logs: tuple[Path, Path, Path]
    ) -> None:
        """Test that Lua-generated and Python-generated logs are equivalent.

        This test the log file "writing" (lua_log_path) and compare with the
        original jsonl file (original_jsonl).
        """
        original_jsonl, lua_log_path, _ = replay_logs

        # Load both generated log files
        lua_steps = load_jsonl_run(lua_log_path)
        orig_steps = load_jsonl_run(original_jsonl)

        assert len(lua_steps) == len(orig_steps), (
            f"Different number of steps: Lua={len(lua_steps)}, Python={len(orig_steps)}"
        )

        # Compare each step
        for i, (original_step, lua_step) in enumerate(zip(orig_steps, lua_steps)):
            context = f"step {i} in {original_jsonl.name} (Origianl vs Lua logs)"
            assert_steps_equal(lua_step, original_step, context)

    def test_compare_python_logs_with_original_run(
        self, replay_logs: tuple[Path, Path, Path]
    ) -> None:
        """Test that generated logs match the original run game states.

        This test the log file "reading" (original_jsonl) and test the ability
        to replicate the run (python_log_path).
        """
        original_jsonl, _, python_log_path = replay_logs

        # Load original and generated logs
        orig_steps = load_jsonl_run(original_jsonl)
        python_steps = load_jsonl_run(python_log_path)

        assert len(orig_steps) == len(python_steps), (
            f"Different number of steps: Original={len(orig_steps)}, Generated={len(python_steps)}"
        )

        # Compare each step
        for i, (original_step, python_step) in enumerate(zip(orig_steps, python_steps)):
            context = f"step {i} in {original_jsonl.name} (Original vs Python logs)"
            assert_steps_equal(python_step, original_step, context)
