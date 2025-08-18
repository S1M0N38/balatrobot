#!/usr/bin/env python3
"""Test the new checkpoint system."""

from src.balatrobot.client import BalatroClient


def test_checkpoints():
    """Test checkpoint functionality."""
    client = BalatroClient()

    try:
        # Connect to the game
        client.connect()
        print("Connected to game")

        # Get save info
        save_info = client.get_save_info()
        print(f"Save info: {save_info}")

        if save_info.get("save_exists"):
            # Save a checkpoint
            checkpoint_path = client.save_checkpoint("test_checkpoint")
            print(f"Created checkpoint: {checkpoint_path}")

            # List checkpoints
            checkpoints = client.list_checkpoints()
            print(f"Available checkpoints: {len(checkpoints)}")
            for cp in checkpoints[:3]:  # Show first 3
                print(f"  - {cp['name']}: {cp['modified']}")

            # Test loading (commented out to avoid disrupting current game)
            # client.load_checkpoint("test_checkpoint")
            # print("Loaded checkpoint")

            # Clean up test checkpoint
            if any(cp["name"] == "test_checkpoint" for cp in checkpoints):
                client.delete_checkpoint("test_checkpoint")
                print("Deleted test checkpoint")
        else:
            print("No save file exists - start a game first")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    test_checkpoints()
