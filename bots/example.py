#!/usr/bin/env python3
"""Example usage of the new BalatroBot API."""

from balatrobot import BalatroError, BalatroClient, State


def main():
    """Example of using the new BalatroBot API."""
    print("BalatroBot API Example")
    print("=" * 50)

    # Create client and connect
    with BalatroClient() as client:
        try:
            # Get initial game state
            print("Getting initial game state...")
            game_state = client.get_game_state()
            print(f"Current state: {game_state.state_enum.name}")

            # Go to menu if not already there
            if game_state.state_enum != State.MENU:
                print("Going to menu...")
                game_state = client.go_to_menu()
                print(f"Now in state: {game_state.state_enum.name}")

            # Start a new run
            print("Starting new run...")
            game_state = client.start_run(deck="Red Deck", stake=1, seed="EXAMPLE")
            print(f"Run started, state: {game_state.state_enum.name}")

            # Select the blind
            print("Selecting blind...")
            game_state = client.skip_or_select_blind("select")
            print(f"Blind selected, state: {game_state.state_enum.name}")
            print(f"Hand size: {len(game_state.hand)}")

            # Play a hand (first 4 cards)
            if len(game_state.hand) >= 4:
                print("Playing hand with first 4 cards...")
                game_state = client.play_hand_or_discard("play_hand", [0, 1, 2, 3])
                print(f"Hand played, state: {game_state.state_enum.name}")

                # If we won the round, cash out
                if game_state.state_enum == State.ROUND_EVAL:
                    print("Cashing out...")
                    game_state = client.cash_out()
                    print(f"Cashed out, state: {game_state.state_enum.name}")

                    # Go to next round
                    print("Going to next round...")
                    game_state = client.shop("next_round")
                    print(f"Next round, state: {game_state.state_enum.name}")

            # Go back to menu at the end
            print("Going back to menu...")
            game_state = client.go_to_menu()
            print(f"Back to menu, state: {game_state.state_enum.name}")

        except BalatroError as e:
            print(f"API Error: {e}")
            print(f"Error code: {e.error_code}")
            print(f"Context: {e.context}")

        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
