#!/usr/bin/env python3

"""
Test script for the new mechanics snapshot and rehydration system.
This demonstrates how to use the new functionality to expedite testing.

Usage:
    python test_snapshot_system.py

This script will:
1. Connect to a running Balatro instance
2. Create a mechanics snapshot
3. Show the difference in size vs full game state
4. Create a restore point
5. Demonstrate rehydration functionality
"""

import json

from balatrobot import BalatroClient


def main():
    """Test the new mechanics snapshot and rehydration system."""
    print("Testing Mechanics Snapshot and Rehydration System")
    print("=" * 50)

    # Connect to Balatro
    try:
        with BalatroClient(port=12346) as client:
            print("✓ Connected to Balatro")

            # Test 1: Compare mechanics snapshot vs full game state
            print("\n1. Comparing mechanics snapshot vs full game state...")

            # Get full game state
            full_state = client.send_message("get_game_state")
            full_state_size = len(json.dumps(full_state))

            # Get mechanics-only snapshot
            mechanics_snapshot = client.get_mechanics_snapshot()
            mechanics_size = len(json.dumps(mechanics_snapshot))

            print(f"   Full game state size: {full_state_size:,} characters")
            print(f"   Mechanics snapshot size: {mechanics_size:,} characters")
            print(
                f"   Size reduction: {((full_state_size - mechanics_size) / full_state_size * 100):.1f}%"
            )

            # Show what's included vs excluded
            full_keys = set(full_state.keys())
            mechanics_keys = set(mechanics_snapshot.keys())

            print(f"   Keys in full state: {sorted(full_keys)}")
            print(f"   Keys in mechanics snapshot: {sorted(mechanics_keys)}")

            if mechanics_snapshot.get("game"):
                game_keys = set(mechanics_snapshot["game"].keys())
                print(f"   Game mechanics keys: {len(game_keys)} keys captured")

            # Test 2: Create a restore point
            print("\n2. Creating restore point...")
            restore_point = client.create_restore_point("test_snapshot_demo")

            print(
                f"   ✓ Created restore point: {restore_point.get('label', 'unnamed')}"
            )
            print(f"   ✓ Timestamp: {restore_point.get('timestamp')}")
            print(f"   ✓ Deck: {restore_point.get('deck_key', 'unknown')}")
            print(f"   ✓ Stake: {restore_point.get('stake', 'unknown')}")

            # Test 3: Show mechanics snapshot structure (limited)
            print("\n3. Mechanics snapshot structure preview:")

            if mechanics_snapshot.get("state"):
                print(f"   Current state: {mechanics_snapshot['state']}")

            if mechanics_snapshot.get("game"):
                game = mechanics_snapshot["game"]
                print(f"   Current round: {game.get('round', 'unknown')}")
                print(f"   Current ante: {game.get('ante', 'unknown')}")
                print(f"   Dollars: {game.get('dollars', 'unknown')}")

                if game.get("current_round"):
                    curr_round = game["current_round"]
                    print(f"   Hands left: {curr_round.get('hands_left', 'unknown')}")
                    print(
                        f"   Discards left: {curr_round.get('discards_left', 'unknown')}"
                    )

            if mechanics_snapshot.get("hand", {}).get("cards"):
                hand_count = len(mechanics_snapshot["hand"]["cards"])
                print(f"   Cards in hand: {hand_count}")

            if mechanics_snapshot.get("jokers", {}).get("cards"):
                joker_count = len(mechanics_snapshot["jokers"]["cards"])
                print(f"   Jokers: {joker_count}")

            # Test 4: Test rehydration (caution: this affects game state)
            user_input = input(
                "\n4. Test rehydration? This will start a new run (y/N): "
            )
            if user_input.lower().startswith("y"):
                print("   Testing rehydration...")

                # Use the restore point we created
                success = client.restore_from_point(restore_point)

                if success:
                    print("   ✓ Rehydration successful!")

                    # Verify the state was restored
                    new_state = client.get_mechanics_snapshot()

                    if new_state.get("game", {}).get(
                        "dollars"
                    ) == mechanics_snapshot.get("game", {}).get("dollars"):
                        print("   ✓ Dollar amount matches - state appears restored")
                    else:
                        print(
                            f"   ⚠ Dollar mismatch: expected {mechanics_snapshot.get('game', {}).get('dollars')}, got {new_state.get('game', {}).get('dollars')}"
                        )

                else:
                    print("   ✗ Rehydration failed")
            else:
                print("   Skipped rehydration test")

            # Test 5: Demonstrate usage for testing
            print("\n5. Usage for expedited testing:")
            print("   # Save a snapshot before a test sequence")
            print("   snapshot = client.get_mechanics_snapshot()")
            print("   ")
            print("   # Run your test...")
            print("   # ... test code ...")
            print("   ")
            print("   # Restore to original state for next test")
            print("   client.rehydrate_game_state(snapshot)")
            print("   ")
            print("   This allows rapid state reset without full game restart!")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure Balatro is running with BalatroBot mod loaded")
        print("and listening on port 12346")
        return 1

    print(f"\n{'=' * 50}")
    print("Test completed successfully!")
    print("\nThe new system provides:")
    print("• Automatic mechanics-only serialization")
    print("• Efficient state snapshots (smaller size)")
    print("• Robust rehydration via baseline patching")
    print("• Easy test state management")
    return 0


if __name__ == "__main__":
    exit(main())
