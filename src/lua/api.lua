local socket = require("socket")
local json = require("json")

-- Constants
local SOCKET_TIMEOUT = 0
-- The threshold for determining when game state transitions are complete.
-- This value represents the maximum number of events allowed in the game's event queue
-- to consider the game idle and waiting for user action. When the queue has fewer than
-- 3 events, the game is considered stable enough to process API responses. This is a
-- heuristic based on empirical testing to ensure smooth gameplay without delays.
local EVENT_QUEUE_THRESHOLD = 3

-- Error codes for standardized error handling
local ERROR_CODES = {
  -- Protocol errors
  INVALID_JSON = "E001",
  MISSING_NAME = "E002",
  MISSING_ARGUMENTS = "E003",
  UNKNOWN_FUNCTION = "E004",
  INVALID_ARGUMENTS = "E005",

  -- Network errors
  SOCKET_CREATE_FAILED = "E006",
  SOCKET_BIND_FAILED = "E007",
  CONNECTION_FAILED = "E008",

  -- Validation errors
  INVALID_GAME_STATE = "E009",
  INVALID_PARAMETER = "E010",
  PARAMETER_OUT_OF_RANGE = "E011",
  MISSING_GAME_OBJECT = "E012",

  -- Game logic errors
  DECK_NOT_FOUND = "E013",
  INVALID_CARD_INDEX = "E014",
  NO_DISCARDS_LEFT = "E015",
  INVALID_ACTION = "E016",
}

---Validates request parameters and returns validation result
---@param args table The arguments to validate
---@param required_fields string[] List of required field names
---@return boolean success True if validation passed
---@return string? error_message Error message if validation failed
---@return string? error_code Error code if validation failed
---@return table? context Additional context about the error
local function validate_request(args, required_fields)
  if type(args) ~= "table" then
    return false, "Arguments must be a table", ERROR_CODES.INVALID_ARGUMENTS, { received_type = type(args) }
  end

  for _, field in ipairs(required_fields) do
    if args[field] == nil then
      return false, "Missing required field: " .. field, ERROR_CODES.INVALID_PARAMETER, { field = field }
    end
  end

  return true, nil, nil, nil
end

API = {}
API.server_socket = nil
API.client_socket = nil
API.functions = {}
API.pending_requests = {}

--------------------------------------------------------------------------------
-- Update Loop
--------------------------------------------------------------------------------

---Updates the API by processing TCP messages and pending requests
---@param _ number Delta time (not used)
---@diagnostic disable-next-line: duplicate-set-field
function API.update(_)
  -- Create server socket if it doesn't exist
  if not API.server_socket then
    API.server_socket = socket.tcp()
    if not API.server_socket then
      sendErrorMessage("Failed to create TCP socket", "API")
      return
    end

    API.server_socket:settimeout(SOCKET_TIMEOUT)
    local port = G.BALATROBOT_PORT
    local success, err = API.server_socket:bind("127.0.0.1", tonumber(port) or 12346)
    if not success then
      sendErrorMessage("Failed to bind to port " .. port .. ": " .. tostring(err), "API")
      API.server_socket = nil
      return
    end

    API.server_socket:listen(1)
    sendDebugMessage("TCP server socket created on port " .. port, "API")
  end

  -- Accept client connection if we don't have one
  if not API.client_socket then
    local client = API.server_socket:accept()
    if client then
      client:settimeout(SOCKET_TIMEOUT)
      API.client_socket = client
      sendDebugMessage("Client connected", "API")
    end
  end

  -- Process pending requests
  for key, request in pairs(API.pending_requests) do
    ---@cast request PendingRequest
    if request.condition() then
      request.action()
      API.pending_requests[key] = nil
    end
  end

  -- Parse received data and run the appropriate function
  if API.client_socket then
    local raw_data, err = API.client_socket:receive("*l")
    if raw_data then
      local ok, data = pcall(json.decode, raw_data)
      if not ok then
        API.send_error_response("Invalid JSON", ERROR_CODES.INVALID_JSON)
        return
      end
      ---@cast data APIRequest
      if data.name == nil then
        API.send_error_response("Message must contain a name", ERROR_CODES.MISSING_NAME)
      elseif data.arguments == nil then
        API.send_error_response("Message must contain arguments", ERROR_CODES.MISSING_ARGUMENTS)
      else
        local func = API.functions[data.name]
        local args = data.arguments
        if func == nil then
          API.send_error_response("Unknown function name", ERROR_CODES.UNKNOWN_FUNCTION, { name = data.name })
        elseif type(args) ~= "table" then
          API.send_error_response(
            "Arguments must be a table",
            ERROR_CODES.INVALID_ARGUMENTS,
            { received_type = type(args) }
          )
        else
          sendDebugMessage(data.name .. "(" .. json.encode(args) .. ")", "API")
          func(args)
        end
      end
    elseif err == "closed" then
      sendDebugMessage("Client disconnected", "API")
      API.client_socket = nil
    elseif err ~= "timeout" then
      sendDebugMessage("TCP receive error: " .. tostring(err), "API")
      API.client_socket = nil
    end
  end
end

---Sends a response back to the connected client
---@param response table The response data to send
function API.send_response(response)
  if API.client_socket then
    local success, err = API.client_socket:send(json.encode(response) .. "\n")
    if not success then
      sendErrorMessage("Failed to send response: " .. tostring(err), "API")
      API.client_socket = nil
    end
  end
end

---Sends an error response to the client with optional context
---@param message string The error message
---@param error_code string The standardized error code
---@param context? table Optional additional context about the error
function API.send_error_response(message, error_code, context)
  sendErrorMessage(message, "API")
  ---@type ErrorResponse
  local response = {
    error = message,
    error_code = error_code,
    state = G.STATE,
    context = context,
  }
  API.send_response(response)
end

---Initializes the API by setting up the update timer
function API.init()
  -- Hook API.update into the existing love.update that's managed by settings.lua
  local original_update = love.update
  ---@diagnostic disable-next-line: duplicate-set-field
  love.update = function(dt)
    original_update(dt)
    API.update(dt)
  end

  sendInfoMessage("BalatrobotAPI initialized", "API")
end

--------------------------------------------------------------------------------
-- API Functions
--------------------------------------------------------------------------------

---Gets the current game state
---@param _ table Arguments (not used)
API.functions["get_game_state"] = function(_)
  ---@type PendingRequest
  API.pending_requests["get_game_state"] = {
    condition = utils.COMPLETION_CONDITIONS.get_game_state,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Navigates to the main menu.
---Call G.FUNCS.go_to_menu() to navigate to the main menu.
---@param _ table Arguments (not used)
API.functions["go_to_menu"] = function(_)
  if G.STATE == G.STATES.MENU and G.MAIN_MENU_UI then
    sendDebugMessage("go_to_menu called but already in menu", "API")
    local game_state = utils.get_game_state()
    API.send_response(game_state)
    return
  end

  G.FUNCS.go_to_menu({})
  API.pending_requests["go_to_menu"] = {
    condition = utils.COMPLETION_CONDITIONS.go_to_menu,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Starts a new game run with specified parameters
---Call G.FUNCS.start_run() to start a new game run with specified parameters.
---If log_path is provided, the run log will be saved to the specified full path (must include .jsonl extension), otherwise uses runs/timestamp.jsonl.
---@param args StartRunArgs The run configuration
API.functions["start_run"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "deck" })
  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Reset the game
  G.FUNCS.setup_run({ config = {} })
  G.FUNCS.exit_overlay_menu()

  -- Set the deck
  local deck_found = false
  for _, v in pairs(G.P_CENTER_POOLS.Back) do
    if v.name == args.deck then
      sendDebugMessage("Changing to deck: " .. v.name, "API")
      G.GAME.selected_back:change_to(v)
      G.GAME.viewed_back:change_to(v)
      deck_found = true
      break
    end
  end
  if not deck_found then
    API.send_error_response("Invalid deck name", ERROR_CODES.DECK_NOT_FOUND, { deck = args.deck })
    return
  end

  -- Set the challenge
  local challenge_obj = nil
  if args.challenge then
    for i = 1, #G.CHALLENGES do
      if G.CHALLENGES[i].name == args.challenge then
        challenge_obj = G.CHALLENGES[i]
        break
      end
    end
  end
  G.GAME.challenge_name = args.challenge

  -- Start the run
  G.FUNCS.start_run(nil, { stake = args.stake, seed = args.seed, challenge = challenge_obj, log_path = args.log_path })

  -- Defer sending response until the run has started
  ---@type PendingRequest
  API.pending_requests["start_run"] = {
    condition = utils.COMPLETION_CONDITIONS.start_run,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Skips or selects the current blind
---Call G.FUNCS.select_blind(button) or G.FUNCS.skip_blind(button)
---@param args BlindActionArgs The blind action to perform
API.functions["skip_or_select_blind"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "action" })
  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Validate current game state is appropriate for blind selection
  if G.STATE ~= G.STATES.BLIND_SELECT then
    API.send_error_response(
      "Cannot skip or select blind when not in blind selection",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE }
    )
    return
  end

  -- Get the current blind pane
  local current_blind = G.GAME.blind_on_deck
  if not current_blind then
    API.send_error_response(
      "No blind currently on deck",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { blind_on_deck = current_blind }
    )
    return
  end
  local blind_pane = G.blind_select_opts[string.lower(current_blind)]

  if G.GAME.blind_on_deck == "Boss" and args.action == "skip" then
    API.send_error_response(
      "Cannot skip Boss blind. Use select instead",
      ERROR_CODES.INVALID_PARAMETER,
      { current_state = G.STATE }
    )
    return
  end

  if args.action == "select" then
    local button = blind_pane:get_UIE_by_ID("select_blind_button")
    G.FUNCS.select_blind(button)
    ---@type PendingRequest
    API.pending_requests["skip_or_select_blind"] = {
      condition = utils.COMPLETION_CONDITIONS.skip_or_select_blind,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
      args = args,
    }
  elseif args.action == "skip" then
    local tag_element = blind_pane:get_UIE_by_ID("tag_" .. current_blind)
    local button = tag_element.children[2]
    G.FUNCS.skip_blind(button)
    ---@type PendingRequest
    API.pending_requests["skip_or_select_blind"] = {
      condition = utils.COMPLETION_CONDITIONS.skip_or_select_blind,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
    }
  else
    API.send_error_response(
      "Invalid action for skip_or_select_blind",
      ERROR_CODES.INVALID_ACTION,
      { action = args.action, valid_actions = { "select", "skip" } }
    )
    return
  end
end

---Plays selected cards or discards them
---Call G.FUNCS.play_cards_from_highlighted(play_button)
---or G.FUNCS.discard_cards_from_highlighted(discard_button)
---@param args HandActionArgs The hand action to perform
API.functions["play_hand_or_discard"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "action", "cards" })
  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Validate current game state is appropriate for playing hand or discarding
  if G.STATE ~= G.STATES.SELECTING_HAND then
    API.send_error_response(
      "Cannot play hand or discard when not selecting hand",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE }
    )
    return
  end

  -- Validate number of cards is between 1 and 5 (inclusive)
  if #args.cards < 1 or #args.cards > 5 then
    API.send_error_response(
      "Invalid number of cards",
      ERROR_CODES.PARAMETER_OUT_OF_RANGE,
      { cards_count = #args.cards, valid_range = "1-5" }
    )
    return
  end

  if args.action == "discard" and G.GAME.current_round.discards_left == 0 then
    API.send_error_response(
      "No discards left to perform discard",
      ERROR_CODES.NO_DISCARDS_LEFT,
      { discards_left = G.GAME.current_round.discards_left }
    )
    return
  end

  -- adjust from 0-based to 1-based indexing
  for i, card_index in ipairs(args.cards) do
    args.cards[i] = card_index + 1
  end

  -- Check that all cards are selectable
  for _, card_index in ipairs(args.cards) do
    if not G.hand.cards[card_index] then
      API.send_error_response(
        "Invalid card index",
        ERROR_CODES.INVALID_CARD_INDEX,
        { card_index = card_index, hand_size = #G.hand.cards }
      )
      return
    end
  end

  -- Select cards
  for _, card_index in ipairs(args.cards) do
    G.hand.cards[card_index]:click()
  end

  if args.action == "play_hand" then
    ---@diagnostic disable-next-line: undefined-field
    local play_button = UIBox:get_UIE_by_ID("play_button", G.buttons.UIRoot)
    G.FUNCS.play_cards_from_highlighted(play_button)
  elseif args.action == "discard" then
    ---@diagnostic disable-next-line: undefined-field
    local discard_button = UIBox:get_UIE_by_ID("discard_button", G.buttons.UIRoot)
    G.FUNCS.discard_cards_from_highlighted(discard_button)
  else
    API.send_error_response(
      "Invalid action for play_hand_or_discard",
      ERROR_CODES.INVALID_ACTION,
      { action = args.action, valid_actions = { "play_hand", "discard" } }
    )
    return
  end

  -- Defer sending response until the run has started
  ---@type PendingRequest
  API.pending_requests["play_hand_or_discard"] = {
    condition = utils.COMPLETION_CONDITIONS.play_hand_or_discard,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Rearranges the hand based on the given card indices
---Call G.FUNCS.rearrange_hand(new_hand)
---@param args RearrangeHandArgs The card indices to rearrange the hand with
API.functions["rearrange_hand"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "cards" })

  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Validate current game state is appropriate for rearranging cards
  if G.STATE ~= G.STATES.SELECTING_HAND then
    API.send_error_response(
      "Cannot rearrange hand when not selecting hand",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE }
    )
    return
  end

  -- Validate number of cards is equal to the number of cards in hand
  if #args.cards ~= #G.hand.cards then
    API.send_error_response(
      "Invalid number of cards to rearrange",
      ERROR_CODES.PARAMETER_OUT_OF_RANGE,
      { cards_count = #args.cards, valid_range = tostring(#G.hand.cards) }
    )
    return
  end

  -- Convert incoming indices from 0-based to 1-based
  for i, card_index in ipairs(args.cards) do
    args.cards[i] = card_index + 1
  end

  -- Create a new hand to swap card indices
  local new_hand = {}
  for _, old_index in ipairs(args.cards) do
    local card = G.hand.cards[old_index]
    if not card then
      API.send_error_response(
        "Card index out of range",
        ERROR_CODES.PARAMETER_OUT_OF_RANGE,
        { index = old_index, max_index = #G.hand.cards }
      )
      return
    end
    table.insert(new_hand, card)
  end

  G.hand.cards = new_hand

  -- Update each card's order field so future sort('order') calls work correctly
  for i, card in ipairs(G.hand.cards) do
    card.config.card.order = i
    if card.config.center then
      card.config.center.order = i
    end
  end

  ---@type PendingRequest
  API.pending_requests["rearrange_hand"] = {
    condition = utils.COMPLETION_CONDITIONS.rearrange_hand,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Cashes out from the current round to enter the shop
---Call G.FUNCS.cash_out() to cash out from the current round to enter the shop.
---@param _ table Arguments (not used)
API.functions["cash_out"] = function(_)
  -- Validate current game state is appropriate for cash out
  if G.STATE ~= G.STATES.ROUND_EVAL then
    API.send_error_response(
      "Cannot cash out when not in round evaluation",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE }
    )
    return
  end

  G.FUNCS.cash_out({ config = {} })
  ---@type PendingRequest
  API.pending_requests["cash_out"] = {
    condition = utils.COMPLETION_CONDITIONS.cash_out,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Selects an action for shop
---Call G.FUNCS.toggle_shop() to select an action for shop.
---@param args ShopActionArgs The shop action to perform
API.functions["shop"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "action" })
  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Validate current game state is appropriate for shop
  if G.STATE ~= G.STATES.SHOP then
    API.send_error_response(
      "Cannot select shop action when not in shop",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE }
    )
    return
  end

  local action = args.action
  if action == "next_round" then
    G.FUNCS.toggle_shop({})
    ---@type PendingRequest
    API.pending_requests["shop"] = {
      condition = utils.COMPLETION_CONDITIONS.shop,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
    }
  elseif action == "buy_card" then
    -- Validate index argument
    if args.index == nil then
      API.send_error_response("Missing required field: index", ERROR_CODES.MISSING_ARGUMENTS, { field = "index" })
      return
    end

    -- Get card index (1-based) and shop area
    local card_pos = args.index + 1
    local area = G.shop_jokers

    -- Validate card index is in range
    if not area or not area.cards or not area.cards[card_pos] then
      API.send_error_response(
        "Card index out of range",
        ERROR_CODES.PARAMETER_OUT_OF_RANGE,
        { index = args.index, valid_range = "0-" .. tostring(#area.cards - 1) }
      )
      return
    end

    -- Evaluate card
    local card = area.cards[card_pos]

    -- Check if the card can be afforded
    if card.cost > G.GAME.dollars then
      API.send_error_response(
        "Card is not affordable",
        ERROR_CODES.INVALID_ACTION,
        { index = args.index, cost = card.cost, dollars = G.GAME.dollars }
      )
      return
    end

    -- Ensure card has an ability set (should be redundant)
    if not card.ability or not card.ability.set then
      API.send_error_response(
        "Card has no ability set, can't check consumable area",
        ERROR_CODES.INVALID_GAME_STATE,
        { index = args.index }
      )
      return
    end

    -- Ensure card area is not full
    if card.ability.set == "Joker" then
      -- Check for free joker slots
      if G.jokers and G.jokers.cards and G.jokers.card_limit and #G.jokers.cards >= G.jokers.card_limit then
        API.send_error_response(
          "Can't purchase joker card, joker slots are full",
          ERROR_CODES.INVALID_ACTION,
          { index = args.index }
        )
        return
      end
    elseif card.ability.set == "Planet" or card.ability.set == "Tarot" or card.ability.set == "Spectral" then
      -- Check for free consumable slots (typo is intentional, present in source)
      if
        G.consumeables
        and G.consumeables.cards
        and G.consumeables.card_limit
        and #G.consumeables.cards >= G.consumeables.card_limit
      then
        API.send_error_response(
          "Can't purchase consumable card, consumable slots are full",
          ERROR_CODES.INVALID_ACTION,
          { index = args.index }
        )
      end
    end

    -- Validate that some purchase button exists (should be a redundant check)
    local card_buy_button = card.children.buy_button and card.children.buy_button.definition
    if not card_buy_button then
      API.send_error_response("Card has no buy button", ERROR_CODES.INVALID_GAME_STATE, { index = args.index })
      return
    end

    -- Used to ensure dollars and shop have been updated before responding, not inheritly atomic
    local dollars_before = G.GAME.dollars
    local expected_dollars = dollars_before - card.cost
    local shop_size_before = #G.shop_jokers.cards

    -- activate the buy button using the UI element handler
    G.FUNCS.buy_from_shop(card_buy_button)

    -- send response once shop is updated
    ---@type PendingRequest
    API.pending_requests["shop"] = {
      condition = function()
        -- Purchase action is non-atomic, so we need to check dollars
        return utils.COMPLETION_CONDITIONS.shop_idle()
          and #G.shop_jokers.cards == shop_size_before - 1
          and G.GAME.dollars == expected_dollars
      end,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
    }

  -- TODO: add other shop actions [buy_and_use | reroll | open_pack | redeem_voucher]
  else
    API.send_error_response(
      "Invalid action for shop",
      ERROR_CODES.INVALID_ACTION,
      { action = action, valid_actions = { "next_round" } }
    )
    return
  end
end

return API
