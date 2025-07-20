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

---@class StartRunArgs
---@field deck string The deck name to use
---@field stake? number The stake level (optional)
---@field seed? string The seed for the run (optional)
---@field challenge? string The challenge name (optional)

-- =============================================================================
-- Game Action Argument Types (used in api.lua)
-- =============================================================================

---@class BlindActionArgs
---@field action "select" | "skip" The action to perform on the blind

---@class HandActionArgs
---@field action "play_hand" | "discard" The action to perform
---@field cards number[] Array of card indices (0-based)

---@class ShopActionArgs
---@field action "next_round" The action to perform

-- TODO: add the other actions "reroll" | "buy" | "buy_and_use" | "redeem" | "open"
--@field item number? The item to buy/buy_and_use/redeem/open (0-based)

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
-- Game Entity Types (used in utils.lua for state extraction)
-- =============================================================================

---@class CardConfig
---@field name string The name of the card
---@field suit string The suit of the card
---@field value string The value/rank of the card
---@field card_key string Unique identifier for the card

---@class Card
---@field label string The display label of the card
---@field config table Card configuration data

---@class HandCard : Card
---@field config.card CardConfig Card-specific configuration

---@class JokerCard : Card
---@field config.center table Center configuration for joker cards

---@class GameRound
---@field discards_left number Number of discards remaining in the current round
---@field hands_left number Number of hands remaining in the current round

---@class RoundResets
---@field hands number Number of hands before round modifiers
---@field discards number Number of discards before round modifiers
---@field reroll_cost number Base reroll cost as of this round
---@field temp_reroll_cost number Temporary reroll cost, effected by some jokers
---@field temp_handsize number Temporary hand size
---@field ante number Ante
---@field blind_ante number Blind ante
---@field blind_states any Blind states
---@field loc_blind_states any Local blind states
---@field blind_choices any Blind choices
---@field boss_rerolled boolean Whether the boss has been rerolled

---@class HandStatistics
---@field visible boolean Whether this hand type is visible to the player
---@field order integer Display order in the UI
---@field mult number Base multiplier for the hand
---@field chips number Base chip value for the hand
---@field s_mult number Scored multiplier (used for scoring?)
---@field s_chips number Scored chips value
---@field level number Current level of the hand upgrade
---@field l_mult number Multiplier increase on level up
---@field l_chips number Chip increase on level up
---@field played integer Times this hand has been played overall
---@field played_this_round integer Times this hand has been played in the current round
---@field example table Example representation of the hand (array of `{string, boolean}` tuples)

---@class GameState
---@field hands_played number Total hands played in the run
---@field skips number Number of skips used
---@field round number Current round number
---@field discount_percent number Shop discount percentage
---@field interest_cap number Maximum interest that can be earned
---@field inflation number Current inflation rate
---@field dollars number Current money amount
---@field max_jokers number Maximum number of jokers allowed
---@field bankrupt_at number Money threshold for bankruptcy
---@field chips number Current chip count
---@field blind_on_deck string Current blind type ("Small", "Large", "Boss")
---@field won boolean Whether the player has won the run
---@field win_ante number Ante required to win the run
---@field round_resets RoundResets Round reset information
---@field hands table<string, HandStatistics> Statistics for each poker hand type
---@field current_round GameRound Current round information

---@class GameStateResponse
---@field state any Current game state enum value
---@field game? GameState Game information (null if not in game)
---@field hand? HandCard[] Array of cards in hand (null if not available)
---@field jokers JokerCard[] Array of joker cards

-- =============================================================================
-- Utility Module (implemented in utils.lua)
-- =============================================================================

---Utility functions for game state extraction and data processing
---@class utils
---@field get_game_state fun(): GameStateResponse Extracts the current game state
---@field table_to_json fun(obj: any, depth?: number): string Converts a Lua table to JSON string

-- =============================================================================
-- Log Types (used in log.lua)
-- =============================================================================

---@class LogEntry
---@field timestamp_ms number Timestamp in milliseconds since epoch
---@field function {name: string, arguments: table} Function call information
---@field game_state GameStateResponse Game state at time of logging

-- =============================================================================
-- Configuration Types (used in balatrobot.lua)
-- =============================================================================

---@class BalatrobotConfig
---@field port string Port for the bot to listen on
---@field dt number Tells the game that every update is dt seconds long
---@field max_fps integer? Maximum frames per second
---@field vsync_enabled boolean Whether vertical sync is enabled