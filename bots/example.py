"""Example usage of the BalatroBot API."""

import logging

from balatrobot.client import BalatroClient
from balatrobot.exceptions import BalatroError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    """Example of using the new BalatroBot API."""
    logger.info("BalatroBot API Example")

    with BalatroClient() as client:
        try:
            client.send_message("go_to_menu", {})
            client.send_message(
                "start_run",
                {"deck": "Red Deck", "stake": 1, "seed": "OOOO155"},
            )
            client.send_message(
                "skip_or_select_blind",
                {"action": "select"},
            )
            client.send_message(
                "play_hand_or_discard",
                {"action": "play_hand", "cards": [0, 1, 2, 3]},
            )
            client.send_message("cash_out", {})
            client.send_message("shop", {"action": "next_round"})
            client.send_message("go_to_menu", {})
            logger.info("All actions executed successfully")

        except BalatroError as e:
            logger.error(f"API Error: {e}")
            logger.error(f"Error code: {e.error_code}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
