from enum import Enum, unique


@unique
class State(Enum):
    """Game state values representing different phases of gameplay in Balatro,
    from menu navigation to active card play and shop interactions."""

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
    """Bot action values corresponding to user interactions available in
    different game states, from card play to shop purchases and inventory
    management."""

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
    """Starting deck types in Balatro, each providing unique starting
    conditions, card modifications, or special abilities that affect gameplay
    throughout the run."""

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
    """Difficulty stake levels in Balatro that increase game difficulty through
    various modifiers and restrictions, with higher stakes providing greater
    challenges and rewards."""

    WHITE = 1
    RED = 2
    GREEN = 3
    BLACK = 4
    BLUE = 5
    PURPLE = 6
    ORANGE = 7
    GOLD = 8


@unique
class ErrorCode(Enum):
    """Standardized error codes used in BalatroBot API that match those defined in src/lua/api.lua for consistent error handling across the entire system."""

    # Protocol errors (E001-E005)
    INVALID_JSON = "E001"
    MISSING_NAME = "E002"
    MISSING_ARGUMENTS = "E003"
    UNKNOWN_FUNCTION = "E004"
    INVALID_ARGUMENTS = "E005"

    # Network errors (E006-E008)
    SOCKET_CREATE_FAILED = "E006"
    SOCKET_BIND_FAILED = "E007"
    CONNECTION_FAILED = "E008"

    # Validation errors (E009-E012)
    INVALID_GAME_STATE = "E009"
    INVALID_PARAMETER = "E010"
    PARAMETER_OUT_OF_RANGE = "E011"
    MISSING_GAME_OBJECT = "E012"

    # Game logic errors (E013-E016)
    DECK_NOT_FOUND = "E013"
    INVALID_CARD_INDEX = "E014"
    NO_DISCARDS_LEFT = "E015"
    INVALID_ACTION = "E016"
