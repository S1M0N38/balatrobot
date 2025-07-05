import itertools

from balatrobot import Actions, Bot, Decks, Stakes

plays = itertools.cycle(
    [
        # This sequence of plays is winning for the first round
        # for the seed "EXAMPLE" and the deck "Red Deck" with stake 1.
        [Actions.DISCARD_HAND, [2, 3, 4, 6]],
        [Actions.DISCARD_HAND, [1, 2, 6, 8]],
        [Actions.PLAY_HAND, [2, 3, 5, 6, 7]],
        [Actions.PLAY_HAND, [3, 4, 7, 8]],
    ]
)


class MyFirstBot(Bot):
    def __init__(self, deck=Decks.RED, stake=Stakes.WHITE, seed="EXAMPLE"):
        super().__init__(deck=deck, stake=stake, seed=seed)
        self.round_count = 0

    def skip_or_select_blind(self, G):
        """Always select blinds to play them"""
        return [Actions.SELECT_BLIND]

    def select_cards_from_hand(self, G):
        """Simple strategy: play the first card"""
        return next(plays)

    def select_shop_action(self, G):
        """Always leave the shop immediately"""
        return [Actions.END_SHOP]

    def select_booster_action(self, G):
        """Skip all booster packs"""
        return [Actions.SKIP_BOOSTER_PACK]

    def sell_jokers(self, G):
        """Don't sell any jokers"""
        return [Actions.SELL_JOKER, []]

    def rearrange_jokers(self, G):
        """Don't rearrange jokers"""
        return [Actions.REARRANGE_JOKERS, []]

    def use_or_sell_consumables(self, G):
        """Don't use consumables"""
        return [Actions.USE_CONSUMABLE, []]

    def rearrange_consumables(self, G):
        """Don't rearrange consumables"""
        return [Actions.REARRANGE_CONSUMABLES, []]

    def rearrange_hand(self, G):
        """Don't rearrange hand"""
        return [Actions.REARRANGE_HAND, []]


# Run the bot
if __name__ == "__main__":
    bot = MyFirstBot()
    bot.running = True
    bot.run()
