---@meta balatrobot-api-types
---Type definitions for API communication and TCP socket handling

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
---@field action "next_round" | "buy_card" | "reroll" | "redeem_voucher" The action to perform
---@field index? number The index of the card to act on (buy, buy_and_use, redeem, open) (0-based)

-- TODO: add the other actions | "buy_and_use" | "open_pack"

---@class SellJokerArgs
---@field index number The index of the joker to sell (0-based)

---@class SellConsumableArgs
---@field index number The index of the consumable to sell (0-based)

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
