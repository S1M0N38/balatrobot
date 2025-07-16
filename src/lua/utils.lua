---Utility functions for game state extraction and data processing
utils = {}
local json = require("json")

-- ==========================================================================
-- Game State Extraction
-- ==========================================================================

---Extracts the current game state including game info, hand, and jokers
---@return GameStateResponse The complete game state
function utils.get_game_state()
  local game = nil
  if G.GAME then
    game = {
      hands_played = G.GAME.hands_played,
      skips = G.GAME.skips,
      round = G.GAME.round,
      discount_percent = G.GAME.discount_percent,
      interest_cap = G.GAME.interest_cap,
      inflation = G.GAME.inflation,
      dollars = G.GAME.dollars,
      max_jokers = G.GAME.max_jokers,
      bankrupt_at = G.GAME.bankrupt_at,
      chips = G.GAME.chips,
      blind_on_deck = G.GAME.blind_on_deck,
      current_round = {
        discards_left = G.GAME.current_round.discards_left,
        hands_left = G.GAME.current_round.hands_left,
      },
    }
  end

  local hand = nil
  if G.hand then
    hand = {}
    for i, card in pairs(G.hand.cards) do
      hand[i] = {
        label = card.label,
        config = {
          card = {
            name = card.config.card.name,
            suit = card.config.card.suit,
            value = card.config.card.value,
            card_key = card.config.card_key,
          },
        },
      }
    end
  end

  local jokers = {}
  if G.jokers and G.jokers.cards then
    for i, card in pairs(G.jokers.cards) do
      jokers[i] = {
        label = card.label,
        config = {
          center = card.config.center,
        },
      }
    end
  end

  -- TODO: add consumables, ante, and shop

  return {
    state = G.STATE,
    game = game,
    hand = hand,
    jokers = jokers,
  }
end

-- ==========================================================================
-- Debugging Utilities
-- ==========================================================================

---Converts a Lua table to JSON string with depth limiting to prevent infinite recursion
---@param obj any The object to convert to JSON
---@param depth? number Maximum depth to traverse (default: 3)
---@return string JSON string representation of the object
function utils.table_to_json(obj, depth)
  depth = depth or 3

  local function sanitize_for_json(value, current_depth)
    if current_depth <= 0 then
      return "..."
    end

    local value_type = type(value)

    if value_type == "nil" then
      return nil
    elseif value_type == "string" or value_type == "number" or value_type == "boolean" then
      return value
    elseif value_type == "function" then
      return "function"
    elseif value_type == "userdata" then
      return "userdata"
    elseif value_type == "table" then
      local sanitized = {}
      for k, v in pairs(value) do
        local key = type(k) == "string" and k or tostring(k)
        sanitized[key] = sanitize_for_json(v, current_depth - 1)
      end
      return sanitized
    else
      return tostring(value)
    end
  end

  local sanitized = sanitize_for_json(obj, depth)
  return json.encode(sanitized)
end

-- Load DebugPlus integration
-- Attempt to load the optional DebugPlus mod (https://github.com/WilsontheWolf/DebugPlus/tree/master).
-- DebugPlus is a Balatro mod that provides additional debugging utilities for mod development,
-- such as custom debug commands and structured logging. It is not required for core functionality
-- and is primarily intended for development and debugging purposes. If the module is unavailable
-- or incompatible, the program will continue to function without it.
local success, dpAPI = pcall(require, "debugplus-api")

if success and dpAPI.isVersionCompatible(1) then
  local debugplus = dpAPI.registerID("balatrobot")
  debugplus.addCommand({
    name = "env",
    shortDesc = "Get game state",
    desc = "Get the current game state, useful for debugging",
    exec = function(args, _, _)
      debugplus.logger.log('{"name": "' .. args[1] .. '", "G": ' .. utils.table_to_json(G.GAME, 2) .. "}")
    end,
  })
end

return utils
