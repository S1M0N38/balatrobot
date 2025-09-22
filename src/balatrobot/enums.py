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


@unique
class Jokers(Enum):
    """Joker cards available in Balatro with their effects."""

    # Common Jokers (Rarity 1)
    j_joker = "+4 Mult"
    j_greedy_joker = "+3 Mult if played hand contains a Diamond"
    j_lusty_joker = "+3 Mult if played hand contains a Heart"
    j_wrathful_joker = "+3 Mult if played hand contains a Spade"
    j_gluttenous_joker = "+3 Mult if played hand contains a Club"
    j_jolly = "+8 Mult if played hand contains a Pair"
    j_zany = "+12 Mult if played hand contains a Three of a Kind"
    j_mad = "+10 Mult if played hand contains a Two Pair"
    j_crazy = "+12 Mult if played hand contains a Straight"
    j_droll = "+10 Mult if played hand contains a Flush"
    j_sly = "+50 Chips if played hand contains a Pair"
    j_wily = "+100 Chips if played hand contains a Three of a Kind"
    j_clever = "+80 Chips if played hand contains a Two Pair"
    j_devious = "+100 Chips if played hand contains a Straight"
    j_crafty = "+80 Chips if played hand contains a Flush"
    j_half = "+20 Mult if played hand contains 3 or fewer cards"
    j_stencil = "×1 Mult for each empty Joker slot"
    j_four_fingers = "All Flushes and Straights can be made with 4 cards"
    j_mime = "Retrigger all card held in hand abilities"
    j_credit_card = "Go up to -$20 in debt"
    j_ceremonial = "When Blind is selected, destroy Joker to the right and permanently add double its sell value to this Mult"
    j_banner = "+30 Chips for each remaining discard"
    j_mystic_summit = "+15 Mult when 0 discards remaining"
    j_marble = "Adds one Stone card to deck when Blind is selected"
    j_loyalty_card = "×4 Mult every 6 hands played, ×1 Mult every 3 hands played"
    j_8_ball = "1 in 4 chance for each 8 played to create a Tarot card when scored"
    j_misprint = "+0 to +23 Mult"
    j_dusk = "Retrigger all played cards in final hand of round"
    j_raised_fist = "Adds double the rank of lowest ranked card held in hand to Mult"
    j_chaos = "1 free Reroll per shop"
    j_fibonacci = "Each played Ace, 2, 3, 5, or 8 gives +8 Mult when scored"
    j_steel_joker = "Gives ×1.5 Mult for each Steel Card in your full deck"
    j_scary_face = "Played face cards give +30 Chips when scored"
    j_abstract = "+3 Mult for each Joker card"
    j_delayed_grat = "Earn $2 per discard if no discards are used by end of round"
    j_hack = "Retrigger each played 2, 3, 4, or 5"
    j_pareidolia = "All cards are considered face cards"
    j_gros_michel = "+15 Mult, 1 in 4 chance this card is destroyed at end of round"
    j_even_steven = "Played cards with even rank give +4 Mult when scored"
    j_odd_todd = "Played cards with odd rank give +31 Chips when scored"
    j_scholar = "Played Aces give +20 Chips and +4 Mult when scored"
    j_business = "Played face cards have a 1 in 2 chance to give $2 when scored"
    j_supernova = "Adds the number of times poker hand has been played this run to Mult"
    j_ride_the_bus = "This Joker gains +1 Mult per consecutive hand played without a face card, resets when face card is played"
    j_space = "1 in 4 chance to upgrade level of played poker hand"
    j_egg = "Gains $3 of sell value at end of round"
    j_burglar = "When Blind is selected, gain +3 hands and lose all discards"
    j_blackboard = "×3 Mult if all cards held in hand are Spades or Clubs"
    j_runner = "Gains +15 Chips if played hand contains a Straight"
    j_ice_cream = "+100 Chips, -5 Chips for every hand played"
    j_dna = "If first hand of round has only 1 card, add a permanent copy to deck and draw it to hand"
    j_splash = "Every played card counts in scoring"
    j_blue_joker = "+2 Chips for each remaining card in deck"
    j_sixth_sense = (
        "If first hand of round is a single 6, destroy it and create a Spectral card"
    )
    j_constellation = "This Joker gains ×0.1 Mult every time a Planet card is used"
    j_hiker = "Every played card permanently gains +5 Chips when scored"
    j_faceless = "Earn $5 if 3 or more face cards are discarded at the same time"
    j_green_joker = "+1 Mult per hand played, -1 Mult per discard"
    j_superposition = "Create a Tarot card if poker hand contains an Ace and a Straight"
    j_todo_list = "Earn $4 if poker hand is a Pair, poker hand changes at end of round"
    j_cavendish = "×3 Mult, 1 in 1000 chance this card is destroyed at end of round"
    j_card_sharp = "×3 Mult if played poker hand has already been played this round"
    j_red_card = "This Joker gains +3 Mult when any Booster Pack is skipped"
    j_madness = "When Small Blind or Big Blind is selected, gain ×0.5 Mult and destroy a random Joker"
    j_square = "This Joker gains +4 Chips if played hand has exactly 4 cards"
    j_seance = "If poker hand is a Straight Flush, create a random Spectral card"
    j_riff_raff = "When Blind is selected, create 2 Common Jokers"
    j_vampire = (
        "This Joker gains ×0.1 Mult per Enhanced card played, removes card Enhancement"
    )
    j_shortcut = "Allows Straights to be made with gaps of 1 rank"
    j_hologram = (
        "This Joker gains ×0.25 Mult every time a playing card is added to your deck"
    )
    j_vagabond = "Create a Tarot card if hand is played with $4 or less"
    j_baron = "Each King held in hand gives ×1.5 Mult"
    j_cloud_9 = "Earn $1 for each 9 in your full deck at end of round"
    j_rocket = (
        "Earn $1 at end of round, payout increases by $2 when Boss Blind is defeated"
    )
    j_obelisk = "This Joker gains ×0.2 Mult per consecutive hand played without playing your most played poker hand"
    j_midas_mask = "All played face cards become Gold cards when scored"
    j_luchador = "Sell this card to disable the current Boss Blind"
    j_photograph = "First played face card gives ×2 Mult"
    j_gift = "Add $1 of sell value to every Joker and Consumable card at end of round"
    j_turtle_bean = "+5 hand size, reduces by 1 each round"
    j_erosion = "+4 Mult for each card below 52 in your full deck"
    j_reserved_parking = "Each face card held in hand has a 1 in 3 chance to give $1"
    j_mail = "Earn $3 for each discarded rank, rank changes every round"
    j_to_the_moon = "Earn an extra $1 of interest for every $5 you have at end of round"
    j_hallucination = (
        "1 in 2 chance to create a Tarot card when any Booster Pack is opened"
    )
    j_fortune_teller = "+1 Mult per Tarot card used this run"
    j_juggler = "+1 hand size"
    j_drunkard = "+1 discard"
    j_stone = "Gives +25 Chips for each Stone Card in your full deck"
    j_golden = "Earn $4 at end of round"
    j_lucky_cat = (
        "This Joker gains ×0.25 Mult every time a Lucky card successfully triggers"
    )
    j_baseball = "Uncommon Jokers each give ×1.5 Mult"
    j_bull = "+2 Chips for each dollar you have"
    j_diet_cola = "Sell this card to create a free Double Tag"
    j_trading = "If first discard of round has only 1 card, destroy it and earn $3"
    j_flash = "This Joker gains +2 Mult per reroll in the shop"
    j_popcorn = "+20 Mult, -4 Mult per round played"
    j_ramen = "×2 Mult, loses ×0.01 Mult per card discarded"
    j_trousers = "This Joker gains +2 Mult if played hand contains a Two Pair"
    j_ancient = "Each played card with suit gives ×1.5 Mult when scored, suit changes at end of round"
    j_walkie_talkie = "Each played 10 or 4 gives +10 Chips and +4 Mult when scored"
    j_selzer = "Retrigger all cards played for the next 10 hands"
    j_castle = "This Joker gains +3 Chips per discarded card, suit changes every round"
    j_smiley = "Played face cards give +5 Mult when scored"
    j_campfire = "This Joker gains ×0.5 Mult for each card sold, resets when Boss Blind is defeated"
    j_golden_ticket = "Played Gold cards earn $4 when scored"
    j_mr_bones = "Prevents death if chips scored are at least 25% of required chips"
    j_acrobat = "×3 Mult on final hand of round"
    j_sock_and_buskin = "Retrigger all played face cards"
    j_swashbuckler = "Adds the sell value of all other owned Jokers to Mult"
    j_troubadour = "+2 hand size, -1 hand per round"
    j_certificate = (
        "When round begins, add a random playing card with a random seal to your hand"
    )
    j_smeared = "Hearts and Diamonds count as the same suit, Spades and Clubs count as the same suit"
    j_throwback = "×0.25 Mult for each skipped Blind this run"
    j_hanging_chad = "Retrigger first played card 2 additional times"
    j_rough_gem = "Played cards with Diamond suit earn $1 when scored"
    j_bloodstone = (
        "1 in 3 chance for played cards with Heart suit to give ×1.5 Mult when scored"
    )
    j_arrowhead = "Played cards with Spade suit give +50 Chips when scored"
    j_onyx_agate = "Played cards with Club suit give +7 Mult when scored"
    j_glass = "Gives ×2 Mult for each Glass Card in your full deck"
    j_ring_master = "Joker, Tarot, Planet, and Spectral cards may appear multiple times"
    j_flower_pot = "×3 Mult if poker hand contains a Diamond card, a Club card, a Heart card, and a Spade card"
    j_blueprint = "Copies ability of Joker to the right"
    j_wee = "This Joker gains +8 Chips when each played 2 is scored"
    j_merry_andy = "+3 discards, -1 hand size"
    j_oops = "All number cards are 6s"
    j_idol = (
        "Each played card of rank gives ×2 Mult when scored, rank changes every round"
    )
    j_seeing_double = "×2 Mult if played hand has a scoring Club card and a scoring card of any other suit"
    j_matador = "Earn $8 if played hand triggers the Boss Blind ability"
    j_hit_the_road = "This Joker gains ×0.5 Mult for every Jack discarded this round"
    j_duo = "×2 Mult if played hand contains a Pair"
    j_trio = "×3 Mult if played hand contains a Three of a Kind"
    j_family = "×4 Mult if played hand contains a Four of a Kind"
    j_order = "×3 Mult if played hand contains a Straight"
    j_tribe = "×2 Mult if played hand contains a Flush"
    j_stuntman = "+250 Chips, -2 hand size"
    j_invisible = "After 2 rounds, sell this card to Duplicate a random Joker"
    j_brainstorm = "Copies the ability of leftmost Joker"
    j_satellite = "Earn $1 at end of round per unique Planet card used this run"
    j_shoot_the_moon = "Each Queen held in hand gives +13 Mult"
    j_drivers_license = (
        "×3 Mult if you have at least 16 Enhanced cards in your full deck"
    )
    j_cartomancer = "Create a Tarot card when Blind is selected"
    j_astronomer = "All Planet cards and Celestial Packs in the shop are free"
    j_burnt = "Upgrade the level of the first discarded poker hand each round"
    j_bootstraps = "+2 Mult for every $5 you have"
    j_canio = "This Joker gains ×1 Mult when a face card is destroyed"
    j_triboulet = "Played Kings and Queens each give ×2 Mult when scored"
    j_yorick = "This Joker gains ×1 Mult every 23 cards discarded"
    j_chicot = "Disables effect of every Boss Blind"
    j_perkeo = "Creates a Negative copy of 1 random Consumable card in your possession at the end of the shop"


@unique
class Consumables(Enum):
    """Consumable cards available in Balatro with their effects."""

    # Tarot consumable cards and their effects.

    c_fool = (
        "Creates the last Tarot or Planet Card used during this run (The Fool excluded)"
    )
    c_magician = "Enhances 2 selected cards to Lucky Cards"
    c_high_priestess = "Creates up to 2 random Planet cards (Must have room)"
    c_empress = "Enhances 2 selected cards to Mult Cards"
    c_emperor = "Creates up to 2 random Tarot cards (Must have room)"
    c_hierophant = "Enhances 2 selected cards to Bonus Cards"
    c_lovers = "Enhances 1 selected card to a Wild Card"
    c_chariot = "Enhances 1 selected card to a Steel Card"
    c_justice = "Enhances 1 selected card to a Glass Card"
    c_hermit = "Doubles money (max of $20)"
    c_wheel_of_fortune = "1 in 4 chance to add Foil, Holographic, or Polychrome edition to a random Joker"
    c_strength = "Increases rank of up to 2 selected cards by 1"
    c_hanged_man = "Destroys up to 2 selected cards"
    c_death = "Select 2 cards, convert the left into the right"
    c_temperance = "Gives the total sell value of all current Jokers (Max of $50)"
    c_devil = "Enhances 1 selected card to a Gold Card"
    c_tower = "Enhances 1 selected card to a Stone Card"
    c_star = "Converts up to 3 selected cards to Diamonds"
    c_moon = "Converts up to 3 selected cards to Clubs"
    c_sun = "Converts up to 3 selected cards to Hearts"
    c_judgement = "Creates a random Joker card (Must have room)"
    c_world = "Converts up to 3 selected cards to Spades"

    # Planet consumable cards that level up poker hands.

    c_mercury = "Levels up Pair"
    c_venus = "Levels up Three of a Kind"
    c_earth = "Levels up Full House"
    c_mars = "Levels up Four of a Kind"
    c_jupiter = "Levels up Flush"
    c_saturn = "Levels up Straight"
    c_uranus = "Levels up Two Pair"
    c_neptune = "Levels up Straight Flush"
    c_pluto = "Levels up High Card"
    c_planet_x = "Levels up Flush House"
    c_ceres = "Levels up Five of a Kind"
    c_eris = "Levels up High Card"

    # Spectral consumable cards with powerful effects.

    c_familiar = "Destroy 1 random card in your hand, add 3 random Enhanced face cards to your hand"
    c_grim = (
        "Destroy 1 random card in your hand, add 2 random Enhanced Aces to your hand"
    )
    c_incantation = "Destroy 1 random card in your hand, add 4 random Enhanced numbered cards to your hand"
    c_talisman = "Add a Gold Seal to 1 selected card"
    c_aura = "Add Foil, Holographic, or Polychrome effect to 1 selected card"
    c_wraith = "Creates a random Rare Joker, sets money to $0"
    c_sigil = "Converts all cards in hand to a single random suit"
    c_ouija = "Converts all cards in hand to a single random rank, -1 hand size"
    c_ectoplasm = "Add Negative to a random Joker, -1 hand size for rest of run"
    c_immolate = "Destroys 5 random cards in hand, gain $20"
    c_ankh = "Create a copy of a random Joker, destroy all other Jokers"
    c_deja_vu = "Add a Red Seal to 1 selected card"
    c_hex = "Add Polychrome to a random Joker, destroy all other Jokers"
    c_trance = "Add a Blue Seal to 1 selected card"
    c_medium = "Add a Purple Seal to 1 selected card"
    c_cryptid = "Create 2 copies of 1 selected card"
    c_soul = "Creates a Legendary Joker (Must have room)"
    c_black_hole = "Upgrade every poker hand by 1 level"


@unique
class Vouchers(Enum):
    """Voucher cards that provide permanent upgrades."""

    v_overstock_norm = "+1 card slot available in shop (to 3 slots)"
    v_clearance_sale = "All cards and packs in shop are 25% off"
    v_hone = "Foil, Holographic, and Polychrome cards appear 2X more frequently"
    v_reroll_surplus = "Rerolls cost $2 less"
    v_crystal_ball = "+1 consumable slot"
    v_telescope = (
        "Celestial Packs always contain the Planet card for your most played poker hand"
    )
    v_grabber = "Permanently gain +1 hand per round"
    v_wasteful = "Permanently gain +1 discard per round"
    v_tarot_merchant = "Tarot cards appear 2X more frequently in the shop"
    v_planet_merchant = "Planet cards appear 2X more frequently in the shop"
    v_seed_money = "Raise the cap on interest earned in each round to $10"
    v_blank = "Does nothing"
    v_magic_trick = "Playing cards are available for purchase in the shop"
    v_hieroglyph = "-1 Ante, -1 hand each round"
    v_directors_cut = "Reroll Boss Blind 1 time per Ante, $10 per roll"
    v_paint_brush = "+1 hand size"
    v_overstock_plus = "+1 card slot available in shop (to 4 slots)"
    v_liquidation = "All cards and packs in shop are 50% off"
    v_glow_up = "Foil, Holographic, and Polychrome cards appear 4X more frequently"
    v_reroll_glut = "Rerolls cost an additional $2 less"
    v_omen_globe = "Spectral cards may appear in any of the Arcana Packs"
    v_observatory = "Planet cards in your consumable area give ×1.5 Mult for their specific poker hand"
    v_nacho_tong = "Permanently gain an additional +1 hand per round"
    v_recyclomancy = "Permanently gain an additional +1 discard per round"
    v_tarot_tycoon = "Tarot cards appear 4X more frequently in the shop"
    v_planet_tycoon = "Planet cards appear 4X more frequently in the shop"
    v_money_tree = "Raise the cap on interest earned in each round to $20"
    v_antimatter = "+1 Joker slot"
    v_illusion = "Playing cards in shop may have an Enhancement, Edition, or Seal"
    v_petroglyph = "-1 Ante again, -1 discard each round"
    v_retcon = "Reroll Boss Blind unlimited times, $10 per roll"
    v_palette = "+1 hand size again"


@unique
class Tags(Enum):
    """Tag rewards that provide various benefits."""

    tag_uncommon = "Shop has a free Uncommon Joker"
    tag_rare = "Shop has a free Rare Joker"
    tag_negative = "Next base edition shop Joker becomes Negative"
    tag_foil = "Next base edition shop Joker becomes Foil"
    tag_holo = "Next base edition shop Joker becomes Holographic"
    tag_polychrome = "Next base edition shop Joker becomes Polychrome"
    tag_investment = "After defeating this Boss Blind, gain $25"
    tag_voucher = "Adds one Voucher to the next shop"
    tag_boss = "Rerolls the Boss Blind"
    tag_standard = "Gives a free Mega Standard Pack"
    tag_charm = "Gives a free Mega Arcana Pack"
    tag_meteor = "Gives a free Mega Celestial Pack"
    tag_buffoon = "Gives a free Mega Buffoon Pack"
    tag_handy = "Gain $1 for each hand played this run"
    tag_garbage = "Gain $1 for each unused discard this run"
    tag_ethereal = "Gives a free Spectral Pack"
    tag_coupon = "Initial cards and booster packs in next shop are free"
    tag_double = (
        "Gives a copy of the next selected Tag, excluding subsequent Double Tags"
    )
    tag_juggle = "+3 Hand Size for the next round only"
    tag_d_six = "In the next Shop, Rerolls start at $0"
    tag_top_up = "Create up to 2 Common Jokers (if you have space)"
    tag_speed = "Gives $5 for each Blind you've skipped this run"
    tag_orbital = "Upgrade poker hand by 3 levels"
    tag_economy = "Doubles your money (max of $40)"
    tag_rush = "+1 Boss Blind reward"
    tag_skip = "Gives $5 plus $1 for every skipped Blind this run"


@unique
class Editions(Enum):
    """Special editions that can be applied to cards."""

    e_foil = "+50 Chips"
    e_holo = "+10 Mult"
    e_polychrome = "×1.5 Mult"
    e_negative = "+1 Joker slot"


@unique
class Enhancements(Enum):
    """Enhancements that can be applied to playing cards."""

    m_bonus = "+30 Chips when scored"
    m_mult = "+4 Mult when scored"
    m_wild = "Can be used as any suit"
    m_glass = "×2 Mult, 1 in 4 chance to destroy when scored"
    m_steel = "×1.5 Mult when this card stays in hand"
    m_stone = "+50 Chips when scored, no rank or suit"
    m_gold = "$3 when this card is held in hand at end of round"
    m_lucky = "1 in 5 chance for +20 Mult and 1 in 15 chance for $20 when scored"


@unique
class Seals(Enum):
    """Seals that can be applied to playing cards."""

    Red = "Retrigger this card 1 time. Retriggering means that the effect of the cards is applied again including counting again in the score calculation"
    Blue = "Creates the Planet card for the final poker hand played if held in hand at end of round (Must have room)"
    Gold = "$3 when this card is played and scores"
    Purple = "Creates a Tarot card when discarded (Must have room)"
