---@meta balatrobot-types
---Type definitions for the BalatroBot Lua mod

-- =============================================================================
-- TCP Socket Types
-- =============================================================================

---@class TCPSocket
---@field settimeout fun(self: TCPSocket, timeout: number)
---@field setsockname fun(self: TCPSocket, address: string, port: number): boolean, string?
---@field receivefrom fun(self: TCPSocket, size: number): string?, string?, number?
---@field sendto fun(self: TCPSocket, data: string, address: string, port: number): number?, string?

-- =============================================================================
-- API Request Types (used in api.lua)
-- =============================================================================

---@class PendingRequest
---@field condition fun(): boolean Function that returns true when the request condition is met
---@field action fun() Function to execute when condition is met
---@field args? table Optional arguments passed to the request

---@class APIRequest
---@field name string The name of the API function to call
---@field arguments table The arguments to pass to the function

---@class ErrorResponse
---@field error string The error message
---@field error_code string Standardized error code (e.g., "E001")
---@field state any The current game state
---@field context? table Optional additional context about the error

---@class SaveInfoResponse
---@field profile_path string|nil Current profile path (e.g., "3")
---@field save_directory string|nil Full path to Love2D save directory
---@field save_file_path string|nil Full OS-specific path to save.jkr file
---@field has_active_run boolean Whether a run is currently active
---@field save_exists boolean Whether a save file exists

---@class StartRunArgs
---@field deck string The deck name to use
---@field stake? number The stake level (optional)
---@field seed? string The seed for the run (optional)
---@field challenge? string The challenge name (optional)
---@field log_path? string The full file path for the run log (optional, must include .jsonl extension)

-- =============================================================================
-- Game Action Argument Types (used in api.lua)
-- =============================================================================

---@class BlindActionArgs
---@field action "select" | "skip" The action to perform on the blind

---@class HandActionArgs
---@field action "play_hand" | "discard" The action to perform
---@field cards number[] Array of card indices (0-based)

---@class RearrangeHandArgs
---@field action "rearrange" The action to perform
---@field cards number[] Array of card indices for every card in hand (0-based)

---@class RearrangeJokersArgs
---@field jokers number[] Array of joker indices for every joker (0-based)

---@class RearrangeConsumablesArgs
---@field consumables number[] Array of consumable indices for every consumable (0-based)

---@class ShopActionArgs
---@field action "next_round" | "buy_card" | "reroll" | "redeem_voucher" | "buy_and_use_card" The action to perform
---@field index? number The index of the card to act on (buy, buy_and_use, redeem, open) (0-based)

-- TODO: add the other action "open_pack"

---@class SellJokerArgs
---@field index number The index of the joker to sell (0-based)

---@class SellConsumableArgs
---@field index number The index of the consumable to sell (0-based)

---@class LoadSaveArgs
---@field save_path string Path to the save file relative to Love2D save directory (e.g., "3/save.jkr")

-- =============================================================================
-- Main API Module (defined in api.lua)
-- =============================================================================

---Main API module for handling TCP communication with bots
---@class API
---@field socket? TCPSocket TCP socket instance
---@field functions table<string, fun(args: table)> Map of API function names to their implementations
---@field pending_requests table<string, PendingRequest> Map of pending async requests
---@field last_client_ip? string IP address of the last client that sent a message
---@field last_client_port? number Port of the last client that sent a message

-- =============================================================================
-- Game Entity Types
-- =============================================================================

-- Root game state response (G object)
---@class G
---@field state any Current game state enum value
---@field game? GGame Game information (null if not in game)
---@field hand? GHand Hand information (null if not available)
---@field jokers GJokers Jokers area object (with sub-field `cards`)
---@field consumables GConsumables Consumables area object
---@field shop_jokers? GShopJokers Shop jokers area
---@field shop_vouchers? GShopVouchers Shop vouchers area
---@field shop_booster? GShopBooster Shop booster packs area

-- Game state (G.GAME)
---@class GGame
---@field bankrupt_at number Money threshold for bankruptcy
---@field base_reroll_cost number Base cost for rerolling shop
---@field blind_on_deck string Current blind type ("Small", "Big", "Boss")
---@field bosses_used GGameBossesUsed Bosses used in run (bl_<boss_name> = 1|0)
---@field chips number Current chip count
---@field current_round GGameCurrentRound Current round information
---@field discount_percent number Shop discount percentage
---@field dollars number Current money amount
---@field hands_played number Total hands played in the run
---@field inflation number Current inflation rate
---@field interest_amount number Interest amount per dollar
---@field interest_cap number Maximum interest that can be earned
---@field last_blind GGameLastBlind Last blind information
---@field max_jokers number Maximum number of jokers in card area
---@field planet_rate number Probability for planet cards in shop
---@field playing_card_rate number Probability for playing cards in shop
---@field previous_round GGamePreviousRound Previous round information
---@field probabilities GGameProbabilities Various game probabilities
---@field pseudorandom GGamePseudorandom Pseudorandom seed data
---@field round number Current round number
---@field round_bonus GGameRoundBonus Round bonus information
---@field round_scores GGameRoundScores Round scoring data
---@field seeded boolean Whether the run uses a seed
---@field selected_back GGameSelectedBack Selected deck information
---@field shop GGameShop Shop configuration
---@field skips number Number of skips used
---@field smods_version string SMODS version
---@field stake number Current stake level
---@field starting_params GGameStartingParams Starting parameters
---@field tags GGameTags[] Array of tags
---@field tarot_rate number Probability for tarot cards in shop
---@field uncommon_mod number Modifier for uncommon joker probability
---@field unused_discards number Unused discards from previous round
---@field used_vouchers table<string, boolean> Vouchers used in run
---@field voucher_text string Voucher text display
---@field win_ante number Ante required to win
---@field won boolean Whether the run is won

-- Game tags (G.GAME.tags[])
---@class GGameTags
---@field key string Tag ID (e.g., "tag_foil")
---@field name string Tag display name (e.g., "Foil Tag")

-- Last blind info (G.GAME.last_blind)
---@class GGameLastBlind
---@field boss boolean Whether the last blind was a boss
---@field name string Name of the last blind

-- Current round info (G.GAME.current_round)
---@class GGameCurrentRound
---@field discards_left number Number of discards remaining
---@field discards_used number Number of discards used
---@field hands_left number Number of hands remaining
---@field hands_played number Number of hands played
---@field reroll_cost number Current dollar cost to reroll the shop offer
---@field free_rerolls number Free rerolls remaining this round
---@field voucher GGameCurrentRoundVoucher Vouchers for this round

-- Selected deck info (G.GAME.selected_back)
---@class GGameSelectedBack
---@field name string Name of the selected deck

-- Shop configuration (G.GAME.shop)
---@class GGameShop

-- Starting parameters (G.GAME.starting_params)
---@class GGameStartingParams

-- Previous round info (G.GAME.previous_round)
---@class GGamePreviousRound

-- Game probabilities (G.GAME.probabilities)
---@class GGameProbabilities

-- Pseudorandom data (G.GAME.pseudorandom)
---@class GGamePseudorandom

-- Round bonus (G.GAME.round_bonus)
---@class GGameRoundBonus

-- Round scores (G.GAME.round_scores)
---@class GGameRoundScores

-- Hand structure (G.hand)
---@class GHand
---@field cards GHandCards[] Array of cards in hand
---@field config GHandConfig Hand configuration

-- Hand configuration (G.hand.config)
---@class GHandConfig
---@field card_count number Number of cards in hand
---@field card_limit number Maximum cards allowed in hand
---@field highlighted_limit number Maximum cards that can be highlighted

-- Hand card (G.hand.cards[])
---@class GHandCards
---@field label string Display label of the card
---@field sort_id number Unique identifier for this card instance
---@field base GHandCardsBase Base card properties
---@field config GHandCardsConfig Card configuration
---@field debuff boolean Whether card is debuffed
---@field facing string Card facing direction ("front", etc.)
---@field highlighted boolean Whether card is highlighted

-- Hand card base properties (G.hand.cards[].base)
---@class GHandCardsBase
---@field id any Card ID
---@field name string Base card name
---@field nominal string Nominal value
---@field original_value string Original card value
---@field suit string Card suit
---@field times_played number Times this card has been played
---@field value string Current card value

-- Hand card configuration (G.hand.cards[].config)
---@class GHandCardsConfig
---@field card_key string Unique card identifier
---@field card GHandCardsConfigCard Card-specific data

-- Hand card config card data (G.hand.cards[].config.card)
---@class GHandCardsConfigCard
---@field name string Card name
---@field suit string Card suit
---@field value string Card value

---@class GCardAreaConfig
---@field card_count number Number of cards currently present in the area
---@field card_limit number Maximum cards allowed in the area

---@class GJokers
---@field config GCardAreaConfig Config for jokers card area
---@field cards GJokersCard[] Array of joker card objects

---@class GConsumables
---@field config GCardAreaConfig Configuration for the consumables slot
---@field cards? GConsumablesCard[] Array of consumable card objects

-- Joker card (G.jokers.cards[])
---@class GJokersCard
---@field label string Display label of the joker
---@field cost number Purchase cost of the joker
---@field sort_id number Unique identifier for this card instance
---@field config GJokersCardConfig Joker card configuration
---@field debuff boolean Whether joker is debuffed
---@field facing string Card facing direction ("front", "back")
---@field highlighted boolean Whether joker is highlighted

-- Joker card configuration (G.jokers.cards[].config)
---@class GJokersCardConfig
---@field center_key string Key identifier for the joker center

-- Consumable card (G.consumables.cards[])
---@class GConsumablesCard
---@field label string Display label of the consumable
---@field cost number Purchase cost of the consumable
---@field config GConsumablesCardConfig Consumable configuration

-- Consumable card configuration (G.consumables.cards[].config)
---@class GConsumablesCardConfig
---@field center_key string Key identifier for the consumable center

-- =============================================================================
-- Utility Module
-- =============================================================================

---Utility functions for game state extraction and data processing
---@class utils
---@field get_game_state fun(): G Extracts the current game state
---@field table_to_json fun(obj: any, depth?: number): string Converts a Lua table to JSON string

-- =============================================================================
-- Log Types (used in log.lua)
-- =============================================================================

---@class Log
---@field mod_path string? Path to the mod directory for log file storage
---@field current_run_file string? Path to the current run's log file
---@field pending_logs table<string, PendingLog> Map of pending log entries awaiting conditions
---@field game_state_before G Game state before function call
---@field init fun() Initializes the logger by setting up hooks
---@field write fun(log_entry: LogEntry) Writes a log entry to the JSONL file
---@field update fun() Processes pending logs by checking completion conditions
---@field schedule_write fun(function_call: FunctionCall) Schedules a log entry to be written when condition is met

---@class PendingLog
---@field log_entry table The log entry data to be written when condition is met
---@field condition function Function that returns true when the log should be written

---@class FunctionCall
---@field name string The name of the function being called
---@field arguments table The parameters passed to the function

---@class LogEntry
---@field timestamp_ms_before number Timestamp in milliseconds since epoch before function call
---@field timestamp_ms_after number? Timestamp in milliseconds since epoch after function call
---@field function FunctionCall Function call information
---@field game_state_before G Game state before function call
---@field game_state_after G? Game state after function call

-- =============================================================================
-- Configuration Types (used in balatrobot.lua)
-- =============================================================================

---@class BalatrobotConfig
---@field port string Port for the bot to listen on
---@field dt number Tells the game that every update is dt seconds long
---@field max_fps integer? Maximum frames per second
---@field vsync_enabled boolean Whether vertical sync is enabled

-- =============================================================================
-- Shop Area Types
-- =============================================================================

-- Shop jokers area
---@class GShopJokers
---@field config GCardAreaConfig Configuration for the shop jokers area
---@field cards? GShopCard[] Array of shop card objects

-- Shop vouchers area
---@class GShopVouchers
---@field config GCardAreaConfig Configuration for the shop vouchers area
---@field cards? GShopCard[] Array of shop voucher objects

-- Shop booster area
---@class GShopBooster
---@field config GCardAreaConfig Configuration for the shop booster area
---@field cards? GShopCard[] Array of shop booster objects

-- Shop card
---@class GShopCard
---@field label string Display label of the shop card
---@field cost number Purchase cost of the card
---@field sell_cost number Sell cost of the card
---@field debuff boolean Whether card is debuffed
---@field facing string Card facing direction ("front", "back")
---@field highlighted boolean Whether card is highlighted
---@field ability GShopCardAbility Card ability information
---@field config GShopCardConfig Shop card configuration

-- Shop card ability (G.shop_*.cards[].ability)
---@class GShopCardAbility
---@field set string The set of the card: "Joker", "Planet", "Tarot", "Spectral", "Voucher", "Booster", or "Consumable"

-- Shop card configuration (G.shop_*.cards[].config)
---@class GShopCardConfig
---@field center_key string Key identifier for the card center

-- =============================================================================
-- Additional Game State Types
-- =============================================================================

-- Round voucher (G.GAME.current_round.voucher)
---@class GGameCurrentRoundVoucher
-- This is intentionally empty as the voucher table structure varies

-- Bosses used (G.GAME.bosses_used)
---@class GGameBossesUsed
-- Dynamic table with boss name keys mapping to 1|0
