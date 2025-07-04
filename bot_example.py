from bot import Bot, Actions


def skip_or_select_blind(self, G):
    if (
        G["ante"]["blinds"]["ondeck"] == "Small"
        or G["ante"]["blinds"]["ondeck"] == "Big"
    ):
        return [Actions.SKIP_BLIND]
    else:
        return [Actions.SELECT_BLIND]


def select_cards_from_hand(self, G):
    # G["hand"] is a list of cards in the hand

    # Cards have:
    # a label e.g. base_card
    # a name e.g. 3 of Hearts
    # a suit e.g. Hearts
    # a value e.g. 3
    # a card_key e.g. H_3

    # Example of playing the first card in the hand
    # return [Actions.PLAY_HAND, [1]]

    # Example of discarding the first card in the hand
    # return [Actions.DISCARD_HAND, [1]]

    if "hands_played" not in self.state:
        self.state["hands_played"] = 0

    self.state["hands_played"] += 1

    if self.state["hands_played"] == 1:
        return [Actions.DISCARD_HAND, [2, 3, 6, 7]]
    elif self.state["hands_played"] == 2:
        return [Actions.PLAY_HAND, [1, 3, 4, 5, 8]]

    return [Actions.PLAY_HAND, [1]]


def select_shop_action(self, G):
    if "num_shops" not in self.state:
        self.state["num_shops"] = 0

    self.state["num_shops"] += 1

    if self.state["num_shops"] == 1:
        return [Actions.BUY_CARD, [2]]
    elif self.state["num_shops"] == 5:
        return [Actions.BUY_CARD, [2]]

    return [Actions.END_SHOP]


def select_booster_action(self, G):
    return [Actions.SKIP_BOOSTER_PACK]


def sell_jokers(self, G):
    if len(G["jokers"]) > 1:
        return [Actions.SELL_JOKER, [2]]

    return [Actions.SELL_JOKER, []]


def rearrange_jokers(self, G):
    return [Actions.REARRANGE_JOKERS, []]


def use_or_sell_consumables(self, G):
    return [Actions.USE_CONSUMABLE, []]


def rearrange_consumables(self, G):
    return [Actions.REARRANGE_CONSUMABLES, []]


def rearrange_hand(self, G):
    return [Actions.REARRANGE_HAND, []]


if __name__ == "__main__":
    mybot = Bot(deck="Plasma Deck", stake=1, seed="1OGB5WO")

    mybot.skip_or_select_blind = skip_or_select_blind
    mybot.select_cards_from_hand = select_cards_from_hand
    mybot.select_shop_action = select_shop_action
    mybot.select_booster_action = select_booster_action
    mybot.sell_jokers = sell_jokers
    mybot.rearrange_jokers = rearrange_jokers
    mybot.use_or_sell_consumables = use_or_sell_consumables
    mybot.rearrange_consumables = rearrange_consumables
    mybot.rearrange_hand = rearrange_hand

    mybot.running = True
    mybot.run()
