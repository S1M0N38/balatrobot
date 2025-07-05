from enum import Enum, unique


@unique
class State(Enum):
    """Represents the current state of the game."""

    SELECTING_HAND = 1
    HAND_PLAYED = 2
    DRAW_TO_HAND = 3
    GAME_OVER = 4
    SHOP = 5
    PLAY_TAROT = 6
    BLIND_SELECT = 7
    ROUND_EVAL = 8
    TAROT_PACK = 9
    PLANET_PACK = 10
    MENU = 11
    TUTORIAL = 12
    SPLASH = 13
    SANDBOX = 14
    SPECTRAL_PACK = 15
    DEMO_CTA = 16
    STANDARD_PACK = 17
    BUFFOON_PACK = 18
    NEW_ROUND = 19


@unique
class Actions(Enum):
    """Represents the available actions that can be performed."""

    SELECT_BLIND = 1
    SKIP_BLIND = 2
    PLAY_HAND = 3
    DISCARD_HAND = 4
    END_SHOP = 5
    REROLL_SHOP = 6
    BUY_CARD = 7
    BUY_VOUCHER = 8
    BUY_BOOSTER = 9
    SELECT_BOOSTER_CARD = 10
    SKIP_BOOSTER_PACK = 11
    SELL_JOKER = 12
    USE_CONSUMABLE = 13
    SELL_CONSUMABLE = 14
    REARRANGE_JOKERS = 15
    REARRANGE_CONSUMABLES = 16
    REARRANGE_HAND = 17
    PASS = 18
    START_RUN = 19
    SEND_GAMESTATE = 20


@unique
class Decks(Enum):
    """Represents the available decks that can be used."""

    RED = "Red Deck"
    BLUE = "Blue Deck"
    YELLOW = "Yellow Deck"
    GREEN = "Green Deck"
    BLACK = "Black Deck"
    MAGIC = "Magic Deck"
    NEBULA = "Nebula Deck"
    GHOST = "Ghost Deck"
    ABANDONED = "Abandoned Deck"
    CHECKERED = "Checkered Deck"
    ZODIAC = "Zodiac Deck"
    PAINTED = "Painted Deck"
    ANAGLYPH = "Anaglyph Deck"
    PLASMA = "Plasma Deck"
    ERRATIC = "Erratic Deck"


@unique
class Stakes(Enum):
    """Represents the available stakes that can be used."""

    WHITE = 1
    RED = 2
    GREEN = 3
    BLACK = 4
    BLUE = 5
    PURPLE = 6
    ORANGE = 7
    GOLD = 8
