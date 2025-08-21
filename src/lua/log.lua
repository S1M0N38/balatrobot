local json = require("json")
local socket = require("socket")

LOG = {
  mod_path = nil,
  current_run_file = nil,
  pending_logs = {},
  game_state_before = {},
}

-- =============================================================================
-- Utility Functions
-- =============================================================================

---Writes a log entry to the JSONL file
---@param log_entry LogEntry The log entry to write
function LOG.write(log_entry)
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
      -- Update the log entry with after function call info
      pending_log.log_entry["timestamp_ms_after"] = math.floor(socket.gettime() * 1000)
      pending_log.log_entry["game_state_after"] = utils.get_game_state()
      LOG.write(pending_log.log_entry)
      -- Prepare for the next log entry
      LOG.game_state_before = pending_log.log_entry.game_state_after
      LOG.pending_logs[key] = nil
    end
  end
end

--- Schedules a log entry to be written when the condition is met
---@param function_call FunctionCall The function call to log
function LOG.schedule_write(function_call)
  sendInfoMessage(function_call.name .. "(" .. json.encode(function_call.arguments) .. ")", "LOG")

  local log_entry = {
    ["function"] = function_call,
    -- before function call
    timestamp_ms_before = math.floor(socket.gettime() * 1000),
    game_state_before = LOG.game_state_before,
    -- after function call (will be filled in by LOG.write)
    timestamp_ms_after = nil,
    game_state_after = nil,
  }

  local pending_key = function_call.name .. "_" .. tostring(socket.gettime())
  LOG.pending_logs[pending_key] = {
    log_entry = log_entry,
    condition = utils.COMPLETION_CONDITIONS[function_call.name][function_call.arguments.action or ""],
  }
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
    LOG.schedule_write(function_call)
    return original_function(...)
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
    LOG.schedule_write(function_call)
    return original_function(game_state, args)
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
    LOG.schedule_write(function_call)
    return original_function(args)
  end
  sendDebugMessage("Hooked into G.FUNCS.select_blind for logging", "LOG")
end

---Hooks into G.FUNCS.skip_blind
function hook_skip_blind()
  local original_function = G.FUNCS.skip_blind
  G.FUNCS.skip_blind = function(args)
    local function_call = { name = "skip_or_select_blind", arguments = { action = "skip" } }
    LOG.schedule_write(function_call)
    return original_function(args)
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
    LOG.schedule_write(function_call)
    return original_function(...)
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
    LOG.schedule_write(function_call)
    return original_function(...)
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
    LOG.schedule_write(function_call)
    return original_function(...)
  end
  sendDebugMessage("Hooked into G.FUNCS.cash_out for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- shop Hooks
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.toggle_shop
function hook_toggle_shop()
  local original_function = G.FUNCS.toggle_shop
  G.FUNCS.toggle_shop = function(...)
    local function_call = { name = "shop", arguments = { action = "next_round" } }
    LOG.schedule_write(function_call)
    return original_function(...)
  end
  sendDebugMessage("Hooked into G.FUNCS.toggle_shop for logging", "LOG")
end

-- Hooks into G.FUNCS.buy_from_shop for buy_card and buy_and_use_card
function hook_buy_card()
  local original_function = G.FUNCS.buy_from_shop
  -- e is the UI element for buy_card button on the targeted card.

  G.FUNCS.buy_from_shop = function(e)
    local card_id = e.config.ref_table.sort_id
    -- If e.config.id is present, it is the buy_and_use_card button.
    local action = (e.config and e.config.id) or "buy_card"
    -- Normalize internal button id to API action name
    if action == "buy_and_use" then
      action = "buy_and_use_card"
    end
    for i, card in ipairs(G.shop_jokers.cards) do
      if card.sort_id == card_id then
        local function_call = { name = "shop", arguments = { action = action, index = i - 1 } }
        LOG.schedule_write(function_call)
        break
      end
    end
    return original_function(e)
  end
  sendDebugMessage("Hooked into G.FUNCS.buy_from_shop for logging", "LOG")
end

---Hooks into G.FUNCS.use_card for voucher redemption and consumable usage logging
function hook_use_card()
  local original_function = G.FUNCS.use_card
  -- e is the UI element for use_card button on the targeted card.
  G.FUNCS.use_card = function(e)
    local card = e.config.ref_table

    if card.ability.set == "Voucher" then
      for i, shop_card in ipairs(G.shop_vouchers.cards) do
        if shop_card.sort_id == card.sort_id then
          local function_call = { name = "shop", arguments = { action = "redeem_voucher", index = i - 1 } }
          LOG.schedule_write(function_call)
          break
        end
      end
    elseif
      (card.ability.set == "Planet" or card.ability.set == "Tarot" or card.ability.set == "Spectral")
      and card.area == G.consumeables
    then
      -- Only log consumables used from consumables area
      for i, consumable_card in ipairs(G.consumeables.cards) do
        if consumable_card.sort_id == card.sort_id then
          local function_call = { name = "use_consumable", arguments = { index = i - 1 } }
          LOG.schedule_write(function_call)
          break
        end
      end
    end

    return original_function(e)
  end
  sendDebugMessage("Hooked into G.FUNCS.use_card for voucher and consumable logging", "LOG")
end

---Hooks into G.FUNCS.reroll_shop
function hook_reroll_shop()
  local original_function = G.FUNCS.reroll_shop
  G.FUNCS.reroll_shop = function(...)
    local function_call = { name = "shop", arguments = { action = "reroll" } }
    LOG.schedule_write(function_call)
    return original_function(...)
  end
  sendDebugMessage("Hooked into G.FUNCS.reroll_shop for logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- hand_rearrange Hook (also handles joker and consumenables rearrange)
-- -----------------------------------------------------------------------------

---Hooks into CardArea:align_cards for hand and joker reordering detection
function hook_hand_rearrange()
  local original_function = CardArea.align_cards
  local previous_orders = {
    hand = {},
    joker = {},
    consumables = {},
  }
  -- local previous_hand_order = {}
  -- local previous_joker_order = {}
  CardArea.align_cards = function(self, ...)
    -- Monitor hand, joker, and consumable card areas
    if
      ---@diagnostic disable-next-line: undefined-field
      self.config
      ---@diagnostic disable-next-line: undefined-field
      and (self.config.type == "hand" or self.config.type == "joker")
      -- consumables are type "joker"
      ---@diagnostic disable-next-line: undefined-field
      and self.cards
      ---@diagnostic disable-next-line: undefined-field
      and #self.cards > 0
    then
      -- Call the original function with all arguments
      local result = original_function(self, ...)

      ---@diagnostic disable-next-line: undefined-field
      if self.config.card_count ~= #self.cards then
        -- We're adding/removing cards
        return result
      end

      local current_order = {}
      -- Capture current card order after alignment
      ---@diagnostic disable-next-line: undefined-field
      for i, card in ipairs(self.cards) do
        current_order[i] = card.sort_id
      end

      ---@diagnostic disable-next-line: undefined-field
      previous_order = previous_orders[self.config.type]

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

          local function_call

          if self.config.type == "hand" then ---@diagnostic disable-line: undefined-field
            function_call = {
              name = "rearrange_hand",
              arguments = { cards = cards },
            }
          elseif self.config.type == "joker" then ---@diagnostic disable-line: undefined-field
            -- Need to distinguish between actual jokers and consumables
            -- Check if any cards in this area are consumables
            local are_jokers = false
            local are_consumables = false

            ---@diagnostic disable-next-line: undefined-field
            for _, card in ipairs(self.cards) do
              if card.ability and card.ability.set == "Joker" then
                are_jokers = true
              elseif card.ability and card.ability.consumeable then
                are_consumables = true
              end
            end

            if are_consumables and not are_jokers then
              function_call = {
                name = "rearrange_consumables",
                arguments = { consumables = cards },
              }
            elseif are_jokers and not are_consumables then
              function_call = {
                name = "rearrange_jokers",
                arguments = { jokers = cards },
              }
            else
              function_call = {
                name = "unknown_rearrange",
                arguments = {},
              }
              sendErrorMessage("Unknown card type for rearrange: " .. tostring(self.config.type), "LOG") ---@diagnostic disable-line: undefined-field
            end
          end

          -- NOTE: We cannot schedule a log write at this point because we do not have
          -- access to the game state before the function call. The game state is only
          -- available after the function executes, so we need to recreate the "before"
          -- state manually by using the most recent known state (LOG.game_state_before).

          -- HACK: The timestamp for the log entry is problematic because this hook runs
          -- within the game loop, and we cannot accurately compute the "before" timestamp
          -- at the time of the function call. To address this, we use the same timestamp
          -- for both "before" and "after" states. This approach ensures that the log entry
          -- is consistent, but it may slightly reduce the accuracy of the timing information.

          local timestamp_ms = math.floor(socket.gettime() * 1000)

          local log_entry = {
            ["function"] = function_call,
            timestamp_ms_before = timestamp_ms,
            game_state_before = LOG.game_state_before,
            timestamp_ms_after = timestamp_ms,
            game_state_after = utils.get_game_state(),
          }

          sendInfoMessage(function_call.name .. "(" .. json.encode(function_call.arguments) .. ")", "LOG")
          LOG.write(log_entry)
          LOG.game_state_before = log_entry.game_state_after
        end
      end

      ---@diagnostic disable-next-line: undefined-field
      previous_orders[self.config.type] = current_order

      return result
    else
      -- For non-hand/joker card areas, just call the original function
      return original_function(self, ...)
    end
  end
  sendInfoMessage("Hooked into CardArea:align_cards for card rearrange logging", "LOG")
end

-- -----------------------------------------------------------------------------
-- sell_joker Hook
-- -----------------------------------------------------------------------------

---Hooks into G.FUNCS.sell_card to detect sell_joker and sell_consumable actions
function hook_sell_card()
  local original_function = G.FUNCS.sell_card
  G.FUNCS.sell_card = function(e)
    local card = e.config.ref_table
    if card then
      -- Check if the card being sold is a joker from G.jokers
      if card.area == G.jokers then
        -- Find the joker index in G.jokers.cards
        for i, joker in ipairs(G.jokers.cards) do
          if joker == card then
            local function_call = { name = "sell_joker", arguments = { index = i - 1 } } -- 0-based index
            LOG.schedule_write(function_call)
            break
          end
        end
      -- Check if the card being sold is a consumable from G.consumeables
      elseif card.area == G.consumeables then
        -- Find the consumable index in G.consumeables.cards
        for i, consumable in ipairs(G.consumeables.cards) do
          if consumable == card then
            local function_call = { name = "sell_consumable", arguments = { index = i - 1 } } -- 0-based index
            LOG.schedule_write(function_call)
            break
          end
        end
      end
    end
    return original_function(e)
  end
  sendDebugMessage("Hooked into G.FUNCS.sell_card for sell_joker and sell_consumable logging", "LOG")
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
  hook_buy_card()
  hook_use_card()
  hook_reroll_shop()
  hook_hand_rearrange()
  hook_sell_card()

  sendInfoMessage("Logger initialized", "LOG")
end

---@type Log
return LOG
