"""Simple bot example demonstrating the balatrobot API.

This example shows how to create a basic bot that plays Balatro using
a predefined sequence of actions.
"""

import argparse
import itertools
from typing import Any, Iterator

from balatrobot import Actions, ActionSchema, Bot, Decks, Stakes, configure_bot_logging

# Predefined sequence of actions using the ActionCall format
plays: Iterator[ActionSchema] = itertools.cycle(
    [
        # This sequence of plays is winning for the first round
        # for the seed "EXAMPLE" and the deck "Red Deck" with stake 1.
        {"action": Actions.DISCARD_HAND, "args": [[2, 3, 4, 6]]},
        {"action": Actions.DISCARD_HAND, "args": [[1, 2, 6, 8]]},
        {"action": Actions.PLAY_HAND, "args": [[2, 3, 5, 6, 7]]},
        {"action": Actions.PLAY_HAND, "args": [[3, 4, 7, 8]]},
    ]
)


class ExampleBot(Bot):
    """Example bot implementation using the ActionCall API.

    This bot demonstrates a simple strategy using predefined actions.
    It always selects blinds, uses a fixed sequence of plays, and
    skips most optional actions.

    Attributes:
        round_count (int): The current round number.
    """

    def __init__(
        self,
        deck: Decks = Decks.RED,
        stake: Stakes = Stakes.WHITE,
        seed: str = "EXAMPLE",
    ) -> None:
        """Initialize the bot with default settings.

        Args:
            deck: The deck type to use.
            stake: The stake level to play at.
            seed: The random seed for the game.
        """
        super().__init__(deck=deck, stake=stake, seed=seed)
        self.round_count: int = 0

    def skip_or_select_blind(self, env: dict[str, Any]) -> ActionSchema:
        """Always select blinds to play them.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionCall: Action to select blind.
        """
        return {"action": Actions.SELECT_BLIND, "args": None}

    def select_cards_from_hand(self, env: dict[str, Any]) -> ActionSchema:
        """Simple strategy: use predefined card selection sequence.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionCall: Action with card selection from predefined sequence.
        """
        return next(plays)

    def select_shop_action(self, env: dict[str, Any]) -> ActionSchema:
        """Always leave the shop immediately.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionCall: Action to end shop.
        """
        return {"action": Actions.END_SHOP, "args": None}

    def select_booster_action(self, env: dict[str, Any]) -> ActionSchema:
        """Skip all booster packs.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionCall: Action to skip booster pack.
        """
        return {"action": Actions.SKIP_BOOSTER_PACK, "args": None}

    def sell_jokers(self, env: dict[str, Any]) -> ActionSchema:
        """Don't sell any jokers.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionCall: Action to sell jokers with empty list.
        """
        return {"action": Actions.SELL_JOKER, "args": [[]]}

    def rearrange_jokers(self, env: dict[str, Any]) -> ActionSchema:
        """Don't rearrange jokers.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionCall: Action to rearrange jokers with empty list.
        """
        return {"action": Actions.REARRANGE_JOKERS, "args": [[]]}

    def use_or_sell_consumables(self, env: dict[str, Any]) -> ActionSchema:
        """Don't use consumables.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionCall: Action to use consumables with empty list.
        """
        return {"action": Actions.USE_CONSUMABLE, "args": [[]]}

    def rearrange_consumables(self, env: dict[str, Any]) -> ActionSchema:
        """Don't rearrange consumables.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionCall: Action to rearrange consumables with empty list.
        """
        return {"action": Actions.REARRANGE_CONSUMABLES, "args": [[]]}

    def rearrange_hand(self, env: dict[str, Any]) -> ActionSchema:
        """Don't rearrange hand.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionCall: Action to rearrange hand with empty list.
        """
        return {"action": Actions.REARRANGE_HAND, "args": [[]]}


def main() -> None:
    """Main function to run the example bot with command-line argument support."""
    parser = argparse.ArgumentParser(description="Run the example Balatro bot")
    parser.add_argument(
        "--log",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="DEBUG",
        help="Set the console logging level (default: DEBUG)",
    )

    args = parser.parse_args()

    # Configure logging with the specified level
    configure_bot_logging(args.log)

    bot = ExampleBot(deck=Decks.BLUE, stake=Stakes.WHITE, seed="EXAMPLE")
    bot.running = True
    bot.run()


if __name__ == "__main__":
    main()
