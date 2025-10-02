#!/usr/bin/env python3
"""Test script for the enhanced use_consumable endpoint with cards parameter."""

import time

from balatrobot import BalatroClient
from balatrobot.enums import Actions


def test_use_consumable():
    """Test the use_consumable functionality with and without cards parameter."""
    with BalatroClient() as client:
        print("Connected to Balatro")

        # Get initial game state
        state = client.send_message("get_game_state")
        print(f"Current state: {state['G']['STATE']}")

        # Start a new run if needed
        if state["G"]["STATE"] == Actions.MENU:
            print("Starting new run...")
            state = client.send_message("start_run", {"stake": "white", "deck": "red"})
            print(f"Run started, new state: {state['G']['STATE']}")

        # Navigate to a state where we can test consumables
        if state["G"]["STATE"] == Actions.BLIND_SELECT:
            print("Selecting blind...")
            state = client.send_message("skip_or_select_blind", {"action": "select"})
            time.sleep(1)

        # Check if we have consumables
        consumables = state["G"].get("consumeables", {}).get("cards", [])
        print(f"Consumables available: {len(consumables)}")

        if consumables:
            # Try using first consumable without cards (e.g., planet cards)
            print(f"Using consumable at index 0 (no cards)...")
            try:
                result = client.use_consumable(0)
                print("Successfully used consumable without cards")
            except Exception as e:
                print(f"Error using consumable without cards: {e}")

        # Check hand cards
        hand_cards = state["G"].get("hand", {}).get("cards", [])
        print(f"Hand cards available: {len(hand_cards)}")

        if consumables and len(hand_cards) >= 3:
            # Try using a consumable with specific cards selected
            print(f"Using consumable at index 0 with cards [0, 1, 2]...")
            try:
                result = client.use_consumable(0, cards=[0, 1, 2])
                print("Successfully used consumable with selected cards")
            except Exception as e:
                print(f"Error using consumable with cards: {e}")

        # Test error cases
        print("\nTesting error cases...")

        # Test invalid index
        try:
            print("Testing invalid consumable index...")
            result = client.use_consumable(99)
            print("Unexpected success with invalid index")
        except Exception as e:
            print(f"Expected error with invalid index: {e}")

        # Test invalid card indices
        if consumables:
            try:
                print("Testing invalid card indices...")
                result = client.use_consumable(0, cards=[99, 100])
                print("Unexpected success with invalid card indices")
            except Exception as e:
                print(f"Expected error with invalid card indices: {e}")

        print("\nTest completed!")


if __name__ == "__main__":
    test_use_consumable()
