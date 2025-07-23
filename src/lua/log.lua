local json = require("json")
local socket = require("socket")

LOG = {}
LOG.mod_path = nil
LOG.current_run_file = nil

-- =============================================================================
-- Utility Functions
-- =============================================================================

---Generates an ISO 8601 timestamp for filename
---@return string ISO 8601 timestamp in format YYYYMMDDTHHMMSS
function LOG.generate_iso8601_timestamp()
  return tostring(os.date("!%Y%m%dT%H%M%S"))
end

---Logs a function call to the JSONL file
---@param function_name string The name of the function being called
---@param arguments table The parameters passed to the function
function LOG.write(function_name, arguments)
  ---@type LogEntry
  local log_entry = {
    timestamp_ms = math.floor(socket.gettime() * 1000),
    ["function"] = {
      name = function_name,
      arguments = arguments,
    },
    -- game_state before the function call
    game_state = utils.get_game_state(),
  }
  sendDebugMessage("Writing log entry: " .. utils.table_to_json(log_entry, 4), "LOG")
  local log_line = json.encode(log_entry) .. "\n"

  local log_file_path
  if LOG.current_run_file then
    log_file_path = LOG.current_run_file
    local file = io.open(log_file_path, "a")
    if file then
      file:write(log_line)
      file:close()
    else
      sendErrorMessage("Failed to open log file for writing: " .. log_file_path, "LOG")
    end
  end
end

-- =============================================================================
-- Hooks
-- =============================================================================

-- -----------------------------------------------------------------------------
-- go_to_menu Hook
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.go_to_menu
function LOG.hook_go_to_menu()
  local original_function = G.FUNCS.go_to_menu
  G.FUNCS.go_to_menu = function(args)
    local arguments = {}
    local name = "go_to_menu"
    LOG.write(name, arguments)
    return original_function(args)
  end
  sendDebugMessage("Hooked into G.FUNCS.go_to_menu for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- start_run Hook
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.start_run
function LOG.hook_start_run()
  local original_function = G.FUNCS.start_run
  G.FUNCS.start_run = function(game_state, args)
    -- Generate new log file for this run
    local timestamp = LOG.generate_iso8601_timestamp()
    LOG.current_run_file = LOG.mod_path .. "runs/" .. timestamp .. ".jsonl"
    sendInfoMessage("Starting new run log: " .. timestamp .. ".jsonl", "LOG")
    local arguments = {
      deck = G.GAME.selected_back.name,
      stake = args.stake,
      seed = args.seed,
      challenge = args.challenge and args.challenge.name,
    }
    local name = "start_run"
    LOG.write(name, arguments)
    return original_function(game_state, args)
  end
  sendDebugMessage("Hooked into G.FUNCS.start_run for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- skip_or_select_blind Hooks
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.select_blind
function LOG.hook_select_blind()
  local original_function = G.FUNCS.select_blind
  G.FUNCS.select_blind = function(args)
    local arguments = { action = "select" }
    local name = "skip_or_select_blind"
    LOG.write(name, arguments)
    return original_function(args)
  end
  sendDebugMessage("Hooked into G.FUNCS.select_blind for logging", "LOG")
end

---Hooks into G.FUNCS.skip_blind
function LOG.hook_skip_blind()
  local original_function = G.FUNCS.skip_blind
  G.FUNCS.skip_blind = function(args)
    local arguments = { action = "skip" }
    local name = "skip_or_select_blind"
    LOG.write(name, arguments)
    return original_function(args)
  end
  sendDebugMessage("Hooked into G.FUNCS.skip_blind for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- play_hand_or_discard Hooks
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.play_cards_from_highlighted
function LOG.hook_play_cards_from_highlighted()
  local original_function = G.FUNCS.play_cards_from_highlighted
  G.FUNCS.play_cards_from_highlighted = function(args)
    local cards = {}
    for i, card in ipairs(G.hand.cards) do
      if card.highlighted then
        table.insert(cards, i - 1) -- Adjust for 0-based indexing
      end
    end
    local arguments = { action = "play_hand", cards = cards }
    local name = "play_hand_or_discard"
    LOG.write(name, arguments)
    return original_function(args)
  end
  sendDebugMessage("Hooked into G.FUNCS.play_cards_from_highlighted for logging", "LOG")
end

---Hooks into G.FUNCS.discard_cards_from_highlighted
function LOG.hook_discard_cards_from_highlighted()
  local original_function = G.FUNCS.discard_cards_from_highlighted
  G.FUNCS.discard_cards_from_highlighted = function(args)
    local cards = {}
    for i, card in ipairs(G.hand.cards) do
      if card.highlighted then
        table.insert(cards, i - 1) -- Adjust for 0-based indexing
      end
    end
    local arguments = { action = "discard", cards = cards }
    local name = "play_hand_or_discard"
    LOG.write(name, arguments)
    return original_function(args)
  end
  sendDebugMessage("Hooked into G.FUNCS.discard_cards_from_highlighted for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- cash_out Hook
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.cash_out
function LOG.hook_cash_out()
  local original_function = G.FUNCS.cash_out
  G.FUNCS.cash_out = function(args)
    local arguments = {}
    local name = "cash_out"
    LOG.write(name, arguments)
    return original_function(args)
  end
  sendDebugMessage("Hooked into G.FUNCS.cash_out for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- shop Hook
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.toggle_shop
function LOG.hook_toggle_shop()
  local original_function = G.FUNCS.toggle_shop
  G.FUNCS.toggle_shop = function(args)
    local arguments = { action = "next_round" }
    local name = "shop"
    LOG.write(name, arguments)
    return original_function(args)
  end
  sendDebugMessage("Hooked into G.FUNCS.toggle_shop for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- hand_rearrange Hook
-- -----------------------------------------------------------------------------

---Hooks into CardArea:align_cards for hand reordering detection
function LOG.hook_hand_rearrange()
  local original_function = CardArea.align_cards
  local previous_order = {}
  CardArea.align_cards = function(self, ...)
    -- Only monitor hand cards
    ---@diagnostic disable-next-line: undefined-field
    if self.config and self.config.type == "hand" and self.cards then
      -- Call the original function with all arguments
      local result = original_function(self, ...)

      ---@diagnostic disable-next-line: undefined-field
      if self.config.card_count ~= #self.cards then
        -- We're drawing cards from the deck
        return result
      end

      -- Capture current card order after alignment
      local current_order = {}
      ---@diagnostic disable-next-line: undefined-field
      for i, card in ipairs(self.cards) do
        current_order[i] = card.sort_id
      end

      if utils.sets_equal(previous_order, current_order) then
        local order_changed = false
        for i = 1, #current_order do
          if previous_order[i] ~= current_order[i] then
            order_changed = true
            break
          end
        end

        if order_changed then
          -- TODO: compute the rearrangement from previous_order and current_order
          -- and use as the arguments to the rearrange_hand API call
          -- So remove previous_order and current_order and use cards
          -- Then remove sendInfoMessage calls
          local arguments = {
            previous_order = previous_order,
            current_order = current_order,
          }
          local name = "rearrange_hand"
          sendInfoMessage("Hand rearranged - cards reordered", "LOG")
          sendInfoMessage("Before: " .. json.encode(previous_order), "LOG")
          sendInfoMessage("After: " .. json.encode(current_order), "LOG")
          LOG.write(name, arguments)
        end
      end

      previous_order = current_order
      return result
    else
      -- For non-hand card areas, just call the original function
      return original_function(self, ...)
    end
  end
  sendInfoMessage("Hooked into CardArea:align_cards for hand rearrange logging", "LOG")
end

-- TODO: add hooks for other shop functions

-- =============================================================================
-- Initializer
-- =============================================================================

---Initializes the logger by setting up hooks
function LOG.init()
  -- Get mod path (required)
  if SMODS.current_mod and SMODS.current_mod.path then
    LOG.mod_path = SMODS.current_mod.path
    sendInfoMessage("Using mod path: " .. LOG.mod_path, "LOG")
  else
    sendErrorMessage("SMODS.current_mod.path not available - LOG disabled", "LOG")
    return
  end

  -- Init hooks
  LOG.hook_go_to_menu()
  LOG.hook_start_run()
  LOG.hook_select_blind()
  LOG.hook_skip_blind()
  LOG.hook_play_cards_from_highlighted()
  LOG.hook_discard_cards_from_highlighted()
  LOG.hook_cash_out()
  LOG.hook_toggle_shop()
  LOG.hook_hand_rearrange()

  sendInfoMessage("Logger initialized", "LOG")
end

return LOG
