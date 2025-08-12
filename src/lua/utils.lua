---Utility functions for game state extraction and data processing
utils = {}
local json = require("json")
local socket = require("socket")

-- ==========================================================================
-- Utility Functions
-- ==========================================================================

---Checks if two lists contain the same elements (regardless of order)
---@param list1 any[] First list to compare
---@param list2 any[] Second list to compare
---@return boolean equal True if both lists contain the same elements
function utils.sets_equal(list1, list2)
  if #list1 ~= #list2 then
    return false
  end

  local set = {}
  for _, v in ipairs(list1) do
    set[v] = true
  end

  for _, v in ipairs(list2) do
    if not set[v] then
      return false
    end
  end

  return true
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

  -- Fields to skip during serialization to avoid circular references and large data
  local skip_fields = {
    children = true,
    parent = true,
    velocity = true,
    area = true,
    alignment = true,
    container = true,
    h_popup = true,
    role = true,
    colour = true,
    back_overlay = true,
    center = true,
  }

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
        -- Skip keys that start with capital letters (UI-related)
        -- Skip predefined fields to avoid circular references and large data
        if not (type(key) == "string" and string.sub(key, 1, 1):match("[A-Z]")) and not skip_fields[key] then
          sanitized[key] = sanitize_for_json(v, current_depth - 1)
        end
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

-- ==========================================================================
-- Completion Conditions
-- ==========================================================================

-- The threshold for determining when game state transitions are complete.
-- This value represents the maximum number of events allowed in the game's event queue
-- to consider the game idle and waiting for user action. When the queue has fewer than
-- 3 events, the game is considered stable enough to process API responses. This is a
-- heuristic based on empirical testing to ensure smooth gameplay without delays.
local EVENT_QUEUE_THRESHOLD = 3

-- Timestamp storage for delayed conditions
local condition_timestamps = {}

---Completion conditions for different game actions to determine when action execution is complete
---These are shared between API and LOG systems to ensure consistent timing
---@type table<string, table>
utils.COMPLETION_CONDITIONS = {
  get_game_state = {
    [""] = function()
      return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
    end,
  },

  go_to_menu = {
    [""] = function()
      return G.STATE == G.STATES.MENU and G.MAIN_MENU_UI
    end,
  },

  start_run = {
    [""] = function()
      return G.STATE == G.STATES.BLIND_SELECT
        and G.GAME.blind_on_deck
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
    end,
  },

  skip_or_select_blind = {
    ["select"] = function()
      if G.GAME and G.GAME.facing_blind and G.STATE == G.STATES.SELECTING_HAND then
        return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
      end
    end,
    ["skip"] = function()
      if G.prev_small_state == "Skipped" or G.prev_large_state == "Skipped" or G.prev_boss_state == "Skipped" then
        return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
      end
      return false
    end,
  },

  play_hand_or_discard = {
    -- TODO: refine condition for be specific about the action
    ["play_hand"] = function()
      if #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE then
        -- round still going
        if G.buttons and G.STATE == G.STATES.SELECTING_HAND then
          return true
        -- round won and entering cash out state (ROUND_EVAL state)
        elseif G.STATE == G.STATES.ROUND_EVAL then
          return true
        -- game over state
        elseif G.STATE == G.STATES.GAME_OVER then
          return true
        end
      end
      return false
    end,
    ["discard"] = function()
      if #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE then
        -- round still going
        if G.buttons and G.STATE == G.STATES.SELECTING_HAND then
          return true
        -- round won and entering cash out state (ROUND_EVAL state)
        elseif G.STATE == G.STATES.ROUND_EVAL then
          return true
        -- game over state
        elseif G.STATE == G.STATES.GAME_OVER then
          return true
        end
      end
      return false
    end,
  },

  rearrange_hand = {
    [""] = function()
      return G.STATE == G.STATES.SELECTING_HAND
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
        and G.STATE_COMPLETE
    end,
  },

  rearrange_jokers = {
    [""] = function()
      return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE
    end,
  },

  rearrange_consumables = {
    [""] = function()
      return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE
    end,
  },

  cash_out = {
    [""] = function()
      return G.STATE == G.STATES.SHOP and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE
    end,
  },

  shop = {
    buy_card = function()
      local base_condition = G.STATE == G.STATES.SHOP
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduve the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.shop_buy_card = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.shop_buy_card then
        condition_timestamps.shop_buy_card = socket.gettime()
      end

      -- Check if 0.1 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.shop_buy_card
      return elapsed > 0.1
    end,
    next_round = function()
      return G.STATE == G.STATES.BLIND_SELECT and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE
    end,
    reroll = function()
      local base_condition = G.STATE == G.STATES.SHOP
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduve the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.shop_reroll = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.shop_reroll then
        condition_timestamps.shop_reroll = socket.gettime()
      end

      -- Check if 0.3 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.shop_reroll
      return elapsed > 0.30
    end,
    redeem_voucher = function()
      local base_condition = G.STATE == G.STATES.SHOP
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduve the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.shop_redeem_voucher = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.shop_redeem_voucher then
        condition_timestamps.shop_redeem_voucher = socket.gettime()
      end

      -- Check if 0.3 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.shop_redeem_voucher
      return elapsed > 0.10
    end,
  },
  sell_joker = {
    [""] = function()
      local base_condition = #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduce the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.sell_joker = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.sell_joker then
        condition_timestamps.sell_joker = socket.gettime()
      end

      -- Check if 0.2 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.sell_joker
      return elapsed > 0.30
    end,
  },
  sell_consumable = {
    [""] = function()
      local base_condition = #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduce the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.sell_consumable = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.sell_consumable then
        condition_timestamps.sell_consumable = socket.gettime()
      end

      -- Check if 0.3 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.sell_consumable
      return elapsed > 0.30
    end,
  },
  use_consumable = {
    [""] = function()
      local base_condition = #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduce the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.use_consumable = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.use_consumable then
        condition_timestamps.use_consumable = socket.gettime()
      end

      -- Check if 0.2 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.use_consumable
      return elapsed > 0.20
    end,
  },
}

return utils
