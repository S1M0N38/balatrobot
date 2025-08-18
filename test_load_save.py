#!/usr/bin/env python3
"""Test the load_save functionality."""

import logging
from pathlib import Path

from src.balatrobot.client import BalatroClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_load_save():
    """Test loading a save file directly."""
    with BalatroClient() as client:
        # First, prepare the test save by copying it to Love2D's save directory
        checkpoint_file = Path("dump/checkpoints/test_checkpoint.jkr")

        if not checkpoint_file.exists():
            logger.error(f"Checkpoint file not found: {checkpoint_file}")
            return

        logger.info(f"Preparing test save from: {checkpoint_file}")

        # This copies the file to Love2D's save directory and returns the relative path
        save_path = client.prepare_test_save(checkpoint_file)
        logger.info(f"Save prepared at Love2D path: {save_path}")

        # Now load the save directly (no restart needed!)
        logger.info("Loading save file...")
        game_state = client.load_save(save_path)

        logger.info(
            f"Successfully loaded save! Current state: {game_state.get('state')}"
        )
        if game_state.get("game", {}).get("round"):
            logger.info(f"Round: {game_state['game']['round']}")
            logger.info(f"Ante: {game_state['game']['round']['ante']}")
            logger.info(f"Money: ${game_state['game']['dollars']}")


if __name__ == "__main__":
    test_load_save()
