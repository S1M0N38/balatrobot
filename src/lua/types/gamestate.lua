---@meta balatrobot-gamestate-types
---Type definitions for game state including the main game object and all card types

-- =============================================================================
-- Root Game State Response (G object)
-- =============================================================================

---@class G
---@field state any Current game state enum value
---@field game? G.Game Game information (null if not in game)
---@field hand? G.Hand Hand information (null if not available)
---@field jokers G.Jokers Jokers area object (with sub-field `cards`)
---@field consumables G.Consumables Consumables area object
---@field shop_jokers? G.ShopJokers Shop jokers area
---@field shop_vouchers? G.ShopVouchers Shop vouchers area
---@field shop_booster? G.ShopBooster Shop booster packs area
---@field deck? G.Deck Deck area (when available)
---@field discard? G.Discard Discard pile (when available)
---@field blind? G.Blind Current blind information (when in blind state)
---@field SPEEDFACTOR? number Current game speed factor

-- =============================================================================
-- Game State (G.GAME)
-- =============================================================================

---@class G.Game
---@field ante number Current ante level (boss blind level)
---@field bankrupt_at number Money threshold for bankruptcy
---@field base_reroll_cost number Base cost for rerolling shop
---@field blind_on_deck string Current blind type ("Small", "Big", "Boss")
---@field bosses_used G.Game.BossesUsed Bosses used in run (bl_<boss_name> = 1|0)
---@field chips number Current chip count
---@field current_round G.Game.CurrentRound Current round information
---@field discount_percent number Shop discount percentage
---@field dollars number Current money amount
---@field hands number Base hands per round
---@field discards number Base discards per round
---@field hands_played number Total hands played in the run
---@field inflation number Current inflation rate
---@field interest_amount number Interest amount per dollar
---@field interest_cap number Maximum interest that can be earned
---@field last_blind G.Game.LastBlind Last blind information
---@field max_jokers number Maximum number of jokers in card area
---@field mult number Current multiplier count
---@field planet_rate number Probability for planet cards in shop
---@field playing_card_rate number Probability for playing cards in shop
---@field previous_round G.Game.PreviousRound Previous round information
---@field probabilities G.Game.Probabilities Various game probabilities
---@field pseudorandom G.Game.Pseudorandom Pseudorandom seed data
---@field round number Current round number
---@field round_resets number Number of times the round has been reset
---@field round_bonus G.Game.RoundBonus Round bonus information
---@field round_scores G.Game.RoundScores Round scoring data
---@field seeded boolean Whether the run uses a seed
---@field selected_back G.Game.SelectedBack Selected deck information
---@field shop G.Game.Shop Shop configuration
---@field skips number Number of skips used
---@field smods_version string SMODS version
---@field stake number Current stake level
---@field starting_params G.Game.StartingParams Starting parameters
---@field tags G.Game.Tags[] Array of tags
---@field tarot_rate number Probability for tarot cards in shop
---@field uncommon_mod number Modifier for uncommon joker probability
---@field unused_discards number Unused discards from previous round
---@field used_vouchers table<string, boolean> Vouchers used in run
---@field voucher_text string Voucher text display
---@field win_ante number Ante required to win
---@field won boolean Whether the run is won

-- =============================================================================
-- Game Sub-types
-- =============================================================================

-- Game tags (G.GAME.tags[])
---@class G.Game.Tags
---@field key string Tag ID (e.g., "tag_foil")
---@field name string Tag display name (e.g., "Foil Tag")

-- Last blind info (G.GAME.last_blind)
---@class G.Game.LastBlind
---@field boss boolean Whether the last blind was a boss
---@field name string Name of the last blind

-- Current round info (G.GAME.current_round)
---@class G.Game.CurrentRound
---@field discards_left number Number of discards remaining
---@field discards_used number Number of discards used
---@field hands_left number Number of hands remaining
---@field hands_played number Number of hands played
---@field reroll_cost number Current dollar cost to reroll the shop offer
---@field free_rerolls number Free rerolls remaining this round
---@field voucher G.Game.CurrentRound.Voucher Vouchers for this round

-- Round voucher (G.GAME.current_round.voucher)
---@class G.Game.CurrentRound.Voucher
-- This is intentionally empty as the voucher table structure varies

-- Selected deck info (G.GAME.selected_back)
---@class G.Game.SelectedBack
---@field name string Name of the selected deck

-- Shop configuration (G.GAME.shop)
---@class G.Game.Shop
---@field joker_max number Maximum jokers that can appear in shop
---@field consumeable_max number Maximum consumables that can appear in shop
---@field booster_max number Maximum booster packs that can appear in shop
---@field voucher_max number Maximum vouchers that can appear in shop

-- Starting parameters (G.GAME.starting_params)
---@class G.Game.StartingParams
---@field ante_scaling number Ante scaling multiplier
---@field boosters_in_shop number Number of booster packs in shop
---@field consumable_slots number Number of consumable slots
---@field deck_cards number Starting deck size
---@field discards number Starting discards per round
---@field dollars number Starting money amount
---@field hand_size number Starting hand size
---@field hands number Starting hands per round
---@field interest_amount number Interest earned per dollar
---@field interest_cap number Maximum interest that can be earned
---@field joker_slots number Number of joker slots
---@field reroll_cost number Base cost to reroll shop
---@field vouchers_in_shop number Number of vouchers in shop

-- Previous round info (G.GAME.previous_round)
---@class G.Game.PreviousRound
---@field dollars number Dollars earned from previous round
---@field hands_played number Hands played in previous round
---@field discards_used number Discards used in previous round

-- Game probabilities (G.GAME.probabilities)
---@class G.Game.Probabilities
---@field normal number Base probability modifier
---@field legendary number Legendary rarity modifier
---@field rare number Rare rarity modifier
---@field uncommon number Uncommon rarity modifier

-- Pseudorandom data (G.GAME.pseudorandom)
---@class G.Game.Pseudorandom
---@field seed string Current pseudorandom seed
---@field index number Current seed index

-- Round bonus (G.GAME.round_bonus)
---@class G.Game.RoundBonus
---@field next_hands number Additional hands for next round
---@field discards number Additional discards for current/next round
---@field mult number Bonus multiplier for round

-- Round scores (G.GAME.round_scores)
---@class G.Game.RoundScores
---@field cards_played table<string, number> Statistics of cards played
---@field cards_discarded table<string, number> Statistics of cards discarded
---@field furthest_ante table<string, number> Furthest ante reached stats
---@field furthest_round table<string, number> Furthest round reached stats
---@field times_played table<string, number> Times specific elements were played

-- Bosses used (G.GAME.bosses_used)
---@class G.Game.BossesUsed
-- Dynamic table with boss name keys mapping to 1|0

-- =============================================================================
-- Blind Information Types
-- =============================================================================

-- Current blind (G.blind)
---@class G.Blind
---@field name string Blind name (e.g., "Small Blind", "Big Blind", "The Hook")
---@field chips number Chip requirement to beat the blind
---@field dollars number Dollar reward for beating the blind
---@field mult number Score multiplier for the blind
---@field boss? boolean Whether this is a boss blind
---@field pos table Position information for blind display
---@field config? table Blind-specific configuration
---@field ability? table Blind ability information (for boss blinds)
---@field discovered? boolean Whether blind is discovered in collection
---@field debuff table<string, boolean> Cards/suits debuffed by this blind
---@field played_cards number Number of cards played this blind
---@field discarded_cards number Number of cards discarded this blind

-- =============================================================================
-- Card Area Configuration
-- =============================================================================

---@class G.CardArea.Config
---@field card_count number Number of cards currently present in the area
---@field card_limit number Maximum cards allowed in the area
---@field highlighted_limit number Maximum cards that can be highlighted in area
---@field type string Area type ("hand", "joker", "consumable", "deck", "discard", "shop")
---@field offset number Position offset for card arrangement

-- =============================================================================
-- Hand Structure and Hand Cards
-- =============================================================================

-- Hand structure (G.hand)
---@class G.Hand
---@field cards G.Hand.Cards[] Array of cards in hand
---@field config G.Hand.Config Hand configuration

-- Hand configuration (G.hand.config)
---@class G.Hand.Config
---@field card_count number Number of cards in hand
---@field card_limit number Maximum cards allowed in hand
---@field highlighted_limit number Maximum cards that can be highlighted
---@field sort string Sort order of the hand. "desc" (rank) | "suit"
---@field temp_limit number Temporary hand limit, used by the skip tag Juggler and some jokers.

-- Hand card (G.hand.cards[])
---@class G.Hand.Cards
---@field label string Display label of the card
---@field sort_id number Unique identifier for this card instance
---@field base G.Hand.Cards.Base Base card properties
---@field config G.Hand.Cards.Config Card configuration
---@field debuff boolean Whether card is debuffed
---@field facing string Card facing direction ("front", "back")
---@field highlighted boolean Whether card is highlighted
---@field ability G.PlayingCard.Ability Card ability information
---@field edition? G.Card.Edition Card edition (Foil, Holographic, Polychrome, Negative)
---@field seal? G.Card.Seal Card seal (Gold, Red, Blue, Purple)
---@field enhancement? G.Card.Enhancement Card enhancement (Bonus, Mult, Wild, Glass, Steel, Stone, Lucky, etc.)
---@field area? table Reference to the card area containing this card
---@field unique_val number Unique value for this card instance
---@field cost number Current cost of the card
---@field sell_cost number Current sell value of the card
---@field rank? number Card rank for sorting and organization

-- Hand card base properties (G.hand.cards[].base)
---@class G.Hand.Cards.Base
---@field id number Card ID (2-14, where J=11, Q=12, K=13, A=14)
---@field name string Base card name (e.g., "2 of Spades", "King of Hearts")
---@field suit string Card suit ("Spades", "Hearts", "Diamonds", "Clubs")
---@field value string Current card value ("2", "3", ..., "10", "Jack", "Queen", "King", "Ace")
---@field nominal number Numeric value for scoring (2-11, face cards = 10, Ace = 11)
---@field original_value string Original card value before modifications
---@field times_played number Times this specific card has been played
---@field colour table Color information for the suit
---@field suit_nominal number Small numeric value for suit identification
---@field suit_nominal_original number Original suit nominal value
---@field face_nominal number Additional value for face cards (0.1-0.4)

-- Hand card configuration (G.hand.cards[].config)
---@class G.Hand.Cards.Config
---@field card_key string Unique card identifier
---@field card G.Hand.Cards.Config.Card Card-specific data

-- Hand card config card data (G.hand.cards[].config.card)
---@class G.Hand.Cards.Config.Card
---@field name string Card name
---@field suit string Card suit
---@field value string Card value

-- =============================================================================
-- Jokers Area and Joker Cards
-- =============================================================================

---@class G.Jokers
---@field config G.CardArea.Config Config for jokers card area
---@field cards G.Jokers.Card[] Array of joker card objects

-- Joker card (G.jokers.cards[])
---@class G.Jokers.Card
---@field label string Display label of the joker
---@field cost number Purchase cost of the joker
---@field sell_cost number Sell value of the joker
---@field sort_id number Unique identifier for this card instance
---@field config G.Jokers.Card.Config Joker card configuration
---@field debuff boolean Whether joker is debuffed
---@field facing string Card facing direction ("front", "back")
---@field highlighted boolean Whether joker is highlighted
---@field ability G.Joker.Ability Joker-specific ability data
---@field edition? G.Card.Edition Card edition (Foil, Holographic, Polychrome, Negative)
---@field area? table Reference to the card area containing this joker
---@field unique_val number Unique value for this joker instance
---@field rank? number Joker rank for sorting

-- Joker card configuration (G.jokers.cards[].config)
---@class G.Jokers.Card.Config
---@field center_key string Key identifier for the joker center

-- =============================================================================
-- Consumables Area and Consumable Cards
-- =============================================================================

---@class G.Consumables
---@field config G.CardArea.Config Configuration for the consumables slot
---@field cards? G.Consumables.Card[] Array of consumable card objects

-- Consumable card (G.consumables.cards[])
---@class G.Consumables.Card
---@field label string Display label of the consumable
---@field cost number Purchase cost of the consumable
---@field sell_cost number Sell value of the consumable
---@field sort_id number Unique identifier for this consumable instance
---@field config G.Consumables.Card.Config Consumable configuration
---@field debuff boolean Whether consumable is debuffed
---@field facing string Card facing direction ("front", "back")
---@field highlighted boolean Whether consumable is highlighted
---@field ability G.Consumable.Ability Consumable-specific ability data
---@field edition? G.Card.Edition Card edition (Only Negative for consumables)
---@field area? table Reference to the card area containing this consumable
---@field unique_val number Unique value for this consumable instance

-- Consumable card configuration (G.consumables.cards[].config)
---@class G.Consumables.Card.Config
---@field center_key string Key identifier for the consumable center

-- =============================================================================
-- Shop Areas and Shop Cards
-- =============================================================================

-- Shop jokers area
---@class G.ShopJokers
---@field config G.CardArea.Config Configuration for the shop jokers area
---@field cards? G.Shop.Card[] Array of shop card objects

-- Shop vouchers area
---@class G.ShopVouchers
---@field config G.CardArea.Config Configuration for the shop vouchers area
---@field cards? G.Shop.Card[] Array of shop voucher objects

-- Shop booster area
---@class G.ShopBooster
---@field config G.CardArea.Config Configuration for the shop booster area
---@field cards? G.Shop.Card[] Array of shop booster objects

-- Shop card
---@class G.Shop.Card
---@field label string Display label of the shop card
---@field cost number Purchase cost of the card
---@field sell_cost number Sell cost of the card
---@field sort_id number Unique identifier for this shop card instance
---@field debuff boolean Whether card is debuffed
---@field facing string Card facing direction ("front", "back")
---@field highlighted boolean Whether card is highlighted
---@field ability G.Shop.Card.Ability Card ability information
---@field config G.Shop.Card.Config Shop card configuration
---@field edition? G.Card.Edition Card edition (Foil, Holographic, Polychrome, Negative)
---@field enhancement? G.Card.Enhancement Card enhancement (for playing cards in shop)
---@field seal? G.Card.Seal Card seal (for playing cards in shop)
---@field area? table Reference to the shop area containing this card
---@field unique_val number Unique value for this card instance

-- Shop card ability (G.shop_*.cards[].ability)
---@class G.Shop.Card.Ability
---@field set string The set of the card: "Joker", "Planet", "Tarot", "Spectral", "Voucher", "Booster", or "Consumable"

-- Shop card configuration (G.shop_*.cards[].config)
---@class G.Shop.Card.Config
---@field center_key string Key identifier for the card center

-- =============================================================================
-- Additional Card Areas
-- =============================================================================

-- Deck area (G.deck)
---@class G.Deck
---@field config G.CardArea.Config Configuration for the deck
---@field cards G.Hand.Cards[] Array of cards in deck (when accessible)

-- Discard pile (G.discard)
---@class G.Discard
---@field config G.CardArea.Config Configuration for the discard pile
---@field cards G.Hand.Cards[] Array of cards in discard pile (when accessible)

-- =============================================================================
-- Card Ability and Enhancement Types
-- =============================================================================

-- Base card ability interface (shared by all card types)
---@class G.Card.Ability
---@field set string The set/category of the card
---@field name? string Name of the ability
---@field consumeable? boolean Whether this is a consumable card
---@field extra? table Additional ability-specific data

-- Playing card ability (for G.hand.cards[].ability)
---@class G.PlayingCard.Ability : G.Card.Ability
---@field name string Playing card name (e.g., "2 of Spades")
---@field suit string Card suit
---@field value string Card value
---@field effect string Current effect applied to card ("Base", "Mult", "Bonus", "Wild", etc.)

-- Joker ability (for G.jokers.cards[].ability)
---@class G.Joker.Ability : G.Card.Ability
---@field name string Joker name (e.g., "Joker", "Greedy Joker", "Lusty Joker")
---@field set string Always "Joker"
---@field order number Display order in collection
---@field extra table Joker-specific data (varies by joker type)
---@field extra_value number Current extra value (for stacking jokers)
---@field mult number Multiplier contribution
---@field h_mult number Hand multiplier contribution
---@field t_mult number Type multiplier contribution
---@field h_size number Hand size modifier
---@field consumeable boolean Whether joker consumes on use

-- Consumable ability (for G.consumables.cards[].ability)
---@class G.Consumable.Ability : G.Card.Ability
---@field name string Consumable name (e.g., "The Fool", "The Magician")
---@field set string The set ("Tarot", "Planet", "Spectral")
---@field order number Display order in collection
---@field consumeable boolean Always true for consumables
---@field extra? table Consumable-specific data

-- Card edition types
---@class G.Card.Edition
---@field type string Edition type ("foil", "holo", "polychrome", "negative")
---@field chip_mod? number Chip modifier for this edition
---@field mult_mod? number Multiplier modifier for this edition

-- Card seal types
---@class G.Card.Seal
---@field type string Seal type ("Red", "Blue", "Gold", "Purple")
---@field color table Color information for rendering

-- Card enhancement types
---@class G.Card.Enhancement
---@field type string Enhancement type ("m_bonus", "m_mult", "m_wild", "m_glass", "m_steel", "m_stone", "m_gold", "m_lucky")
---@field chip_mod? number Chip modifier
---@field mult_mod? number Multiplier modifier
---@field effect? string Special effect description
