local json = require("json")
local socket = require("socket")

LOG = {
  mod_path = nil,
  current_run_file = nil,
  pending_logs = {},
  previous_game_state = nil,
}

-- =============================================================================
-- Utility Functions
-- =============================================================================

---Writes a log entry to the JSONL file
---@param log_entry table The log entry to write
local function write_log_entry(log_entry)
  if LOG.current_run_file then
    local log_line = json.encode(log_entry) .. "\n"
    local file = io.open(LOG.current_run_file, "a")
    if file then
      file:write(log_line)
      file:close()
    else
      sendErrorMessage("Failed to open log file for writing: " .. LOG.current_run_file, "LOG")
    end
  end
end

---Processes pending logs by checking completion conditions
function LOG.update()
  for key, pending_log in pairs(LOG.pending_logs) do
    if pending_log.condition() then
      pending_log.log_entry["game_state_after"] = utils.get_game_state()
      write_log_entry(pending_log.log_entry)
      LOG.previous_game_state = pending_log.log_entry.game_state_after
      LOG.pending_logs[key] = nil
    end
  end
end

---Logs a function call to the JSONL file with completion waiting
---@param original_function function The original function being called
---@param function_call FunctionCall The function call to log
function LOG.write(original_function, function_call, ...)
  local log_entry = {
    timestamp_ms = math.floor(socket.gettime() * 1000),
    ["function"] = function_call,
    game_state_before = LOG.previous_game_state,
  }

  local result = original_function(...)
  sendInfoMessage(function_call.name .. "(" .. json.encode(function_call.arguments) .. ")", "LOG")

  -- Get completion condition by function name
  local condition = utils.COMPLETION_CONDITIONS[function_call.name]
  if condition then
    -- Create a unique key for the pending log
    local pending_key = function_call.name .. "_" .. tostring(socket.gettime())
    LOG.pending_logs[pending_key] = {
      log_entry = log_entry,
      condition = condition,
    }
  else
    -- Immediate logging if no condition found
    log_entry["game_state_after"] = utils.get_game_state()
    write_log_entry(log_entry)
    LOG.previous_game_state = log_entry.game_state_after
  end

  return result
end

-- =============================================================================
-- Hooks
-- =============================================================================

-- -----------------------------------------------------------------------------
-- go_to_menu Hook
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.go_to_menu
function hook_go_to_menu()
  local original_function = G.FUNCS.go_to_menu
  G.FUNCS.go_to_menu = function(...)
    local function_call = {
      name = "go_to_menu",
      arguments = {},
    }
    return LOG.write(original_function, function_call, ...)
  end
  sendDebugMessage("Hooked into G.FUNCS.go_to_menu for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- start_run Hook
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.start_run
function hook_start_run()
  local original_function = G.FUNCS.start_run
  G.FUNCS.start_run = function(game_state, args)
    -- Generate new log file for this run
    if args.log_path then
      local file = io.open(args.log_path, "r")
      if file then
        file:close()
        sendErrorMessage("Log file already exists, refusing to overwrite: " .. args.log_path, "LOG")
        return
      end
      LOG.current_run_file = args.log_path
      sendInfoMessage("Starting new run log: " .. args.log_path, "LOG")
    else
      local timestamp = tostring(os.date("!%Y%m%dT%H%M%S"))
      LOG.current_run_file = LOG.mod_path .. "runs/" .. timestamp .. ".jsonl"
      sendInfoMessage("Starting new run log: " .. timestamp .. ".jsonl", "LOG")
    end
    local function_call = {
      name = "start_run",
      arguments = {
        deck = G.GAME.selected_back.name,
        stake = args.stake,
        seed = args.seed,
        challenge = args.challenge and args.challenge.name,
      },
    }
    return LOG.write(original_function, function_call, game_state, args)
  end
  sendDebugMessage("Hooked into G.FUNCS.start_run for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- skip_or_select_blind Hooks
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.select_blind
function hook_select_blind()
  local original_function = G.FUNCS.select_blind
  G.FUNCS.select_blind = function(args)
    local function_call = { name = "skip_or_select_blind", arguments = { action = "select" } }
    return LOG.write(original_function, function_call, args)
  end
  sendDebugMessage("Hooked into G.FUNCS.select_blind for logging", "LOG")
end

---Hooks into G.FUNCS.skip_blind
function hook_skip_blind()
  local original_function = G.FUNCS.skip_blind
  G.FUNCS.skip_blind = function(args)
    local function_call = { name = "skip_or_select_blind", arguments = { action = "skip" } }
    return LOG.write(original_function, function_call, args)
  end
  sendDebugMessage("Hooked into G.FUNCS.skip_blind for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- play_hand_or_discard Hooks
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.play_cards_from_highlighted
function hook_play_cards_from_highlighted()
  local original_function = G.FUNCS.play_cards_from_highlighted
  G.FUNCS.play_cards_from_highlighted = function(...)
    local cards = {}
    for i, card in ipairs(G.hand.cards) do
      if card.highlighted then
        table.insert(cards, i - 1) -- Adjust for 0-based indexing
      end
    end
    local function_call = { name = "play_hand_or_discard", arguments = { action = "play_hand", cards = cards } }
    return LOG.write(original_function, function_call, ...)
  end
  sendDebugMessage("Hooked into G.FUNCS.play_cards_from_highlighted for logging", "LOG")
end

---Hooks into G.FUNCS.discard_cards_from_highlighted
function hook_discard_cards_from_highlighted()
  local original_function = G.FUNCS.discard_cards_from_highlighted
  G.FUNCS.discard_cards_from_highlighted = function(...)
    local cards = {}
    for i, card in ipairs(G.hand.cards) do
      if card.highlighted then
        table.insert(cards, i - 1) -- Adjust for 0-based indexing
      end
    end
    local function_call = { name = "play_hand_or_discard", arguments = { action = "discard", cards = cards } }
    return LOG.write(original_function, function_call, ...)
  end
  sendDebugMessage("Hooked into G.FUNCS.discard_cards_from_highlighted for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- cash_out Hook
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.cash_out
function hook_cash_out()
  local original_function = G.FUNCS.cash_out
  G.FUNCS.cash_out = function(...)
    local function_call = { name = "cash_out", arguments = {} }
    return LOG.write(original_function, function_call, ...)
  end
  sendDebugMessage("Hooked into G.FUNCS.cash_out for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- shop Hook
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.toggle_shop
function hook_toggle_shop()
  local original_function = G.FUNCS.toggle_shop
  G.FUNCS.toggle_shop = function(...)
    local function_call = { name = "shop", arguments = { action = "next_round" } }
    return LOG.write(original_function, function_call, ...)
  end
  sendDebugMessage("Hooked into G.FUNCS.toggle_shop for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- hand_rearrange Hook
-- -----------------------------------------------------------------------------

---Hooks into CardArea:align_cards for hand reordering detection
function hook_hand_rearrange()
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
          -- Compute rearrangement to interpret the action
          -- Map every card-id → its position in the old list
          local lookup = {}
          for pos, card_id in ipairs(previous_order) do
            lookup[card_id] = pos - 1 -- zero-based for the API
          end

          -- Walk the new order and translate
          local cards = {}
          for pos, card_id in ipairs(current_order) do
            cards[pos] = lookup[card_id]
          end

          local function_call = {
            name = "rearrange_hand",
            arguments = { cards = cards },
          }

          --- NOTE: we cannot use LOG.write because we do not have access to game_state_before. We need to recreate it.
          --- The following lines corresponds to LOG.write

          local log_entry = {
            timestamp_ms = math.floor(socket.gettime() * 1000),
            ["function"] = function_call,
            game_state_before = previous_game_state,
            game_state_after = utils.get_game_state(),
          }
          LOG.previous_game_state = log_entry.game_state_after

          sendInfoMessage(function_call.name .. "(" .. json.encode(function_call.arguments) .. ")", "LOG")

          if LOG.current_run_file then
            local log_line = json.encode(log_entry) .. "\n"
            local file = io.open(LOG.current_run_file, "a")
            if file then
              file:write(log_line)
              file:close()
            else
              sendErrorMessage("Failed to open log file for writing: " .. LOG.current_run_file, "LOG")
            end
          end
        end
      end

      previous_order = current_order
      previous_game_state = utils.get_game_state()
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

  -- Hook into the API update loop to process pending logs
  if API and API.update then
    local original_api_update = API.update
    ---@diagnostic disable-next-line: duplicate-set-field
    API.update = function(dt)
      original_api_update(dt)
      LOG.update()
    end
    sendDebugMessage("Hooked into API.update for pending log processing", "LOG")
  else
    sendErrorMessage("API not available - pending log processing disabled", "LOG")
  end

  -- Init hooks
  hook_go_to_menu()
  hook_start_run()
  hook_select_blind()
  hook_skip_blind()
  hook_play_cards_from_highlighted()
  hook_discard_cards_from_highlighted()
  hook_cash_out()
  hook_toggle_shop()
  hook_hand_rearrange()

  sendInfoMessage("Logger initialized", "LOG")
end

---@type Log
return LOG
