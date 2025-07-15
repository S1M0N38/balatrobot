"""Example usage of the BalatroBot API."""

import logging

from balatrobot import BalatroClient, BalatroError, State

logger = logging.getLogger(__name__)


def main():
    """Example of using the new BalatroBot API."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    logger.info("BalatroBot API Example")
    logger.info("=" * 50)

    # Create client and connect
    with BalatroClient() as client:
        try:
            # Get initial game state
            logger.info("Getting initial game state...")
            game_state = client.get_game_state()
            logger.info(f"Current state: {game_state.state_enum.name}")

            # Go to menu if not already there
            if game_state.state_enum != State.MENU:
                logger.info("Going to menu...")
                game_state = client.go_to_menu()
                logger.info(f"Now in state: {game_state.state_enum.name}")

            # Start a new run
            logger.info("Starting new run...")
            game_state = client.start_run(deck="Red Deck", stake=1, seed="EXAMPLE")
            logger.info(f"Run started, state: {game_state.state_enum.name}")

            # Select the blind
            logger.info("Selecting blind...")
            game_state = client.skip_or_select_blind("select")
            logger.info(f"Blind selected, state: {game_state.state_enum.name}")
            logger.info(f"Hand size: {len(game_state.hand)}")

            # Play a hand (first 4 cards)
            if len(game_state.hand) >= 4:
                logger.info("Playing hand with first 4 cards...")
                game_state = client.play_hand_or_discard("play_hand", [0, 1, 2, 3])
                logger.info(f"Hand played, state: {game_state.state_enum.name}")

                # If we won the round, cash out
                if game_state.state_enum == State.ROUND_EVAL:
                    logger.info("Cashing out...")
                    game_state = client.cash_out()
                    logger.info(f"Cashed out, state: {game_state.state_enum.name}")

                    # Go to next round
                    logger.info("Going to next round...")
                    game_state = client.shop("next_round")
                    logger.info(f"Next round, state: {game_state.state_enum.name}")

            # Go back to menu at the end
            logger.info("Going back to menu...")
            game_state = client.go_to_menu()
            logger.info(f"Back to menu, state: {game_state.state_enum.name}")

        except BalatroError as e:
            logger.error(f"API Error: {e}")
            logger.error(f"Error code: {e.error_code}")
            logger.error(f"Context: {e.context}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
