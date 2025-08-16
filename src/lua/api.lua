local socket = require("socket")
local json = require("json")

-- Constants
local SOCKET_TIMEOUT = 0

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
    condition = utils.COMPLETION_CONDITIONS["get_game_state"][""],
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
    condition = utils.COMPLETION_CONDITIONS["go_to_menu"][""],
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
    condition = utils.COMPLETION_CONDITIONS["start_run"][""],
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
      condition = utils.COMPLETION_CONDITIONS["skip_or_select_blind"]["select"],
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
      condition = utils.COMPLETION_CONDITIONS["skip_or_select_blind"]["skip"],
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
    condition = utils.COMPLETION_CONDITIONS["play_hand_or_discard"][args.action],
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
    condition = utils.COMPLETION_CONDITIONS["rearrange_hand"][""],
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Rearranges the jokers based on the given card indices
---Call G.FUNCS.rearrange_jokers(new_jokers)
---@param args RearrangeJokersArgs The card indices to rearrange the jokers with
API.functions["rearrange_jokers"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "jokers" })

  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Validate that jokers exist
  if not G.jokers or not G.jokers.cards or #G.jokers.cards == 0 then
    API.send_error_response(
      "No jokers available to rearrange",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { jokers_available = false }
    )
    return
  end

  -- Validate number of jokers is equal to the number of jokers in the joker area
  if #args.jokers ~= #G.jokers.cards then
    API.send_error_response(
      "Invalid number of jokers to rearrange",
      ERROR_CODES.PARAMETER_OUT_OF_RANGE,
      { jokers_count = #args.jokers, valid_range = tostring(#G.jokers.cards) }
    )
    return
  end

  -- Convert incoming indices from 0-based to 1-based
  for i, joker_index in ipairs(args.jokers) do
    args.jokers[i] = joker_index + 1
  end

  -- Create a new joker array to swap card indices
  local new_jokers = {}
  for _, old_index in ipairs(args.jokers) do
    local card = G.jokers.cards[old_index]
    if not card then
      API.send_error_response(
        "Joker index out of range",
        ERROR_CODES.PARAMETER_OUT_OF_RANGE,
        { index = old_index, max_index = #G.jokers.cards }
      )
      return
    end
    table.insert(new_jokers, card)
  end

  G.jokers.cards = new_jokers

  -- Update each joker's order field so future sort('order') calls work correctly
  for i, card in ipairs(G.jokers.cards) do
    if card.ability then
      card.ability.order = i
    end
    if card.config and card.config.center then
      card.config.center.order = i
    end
  end

  ---@type PendingRequest
  API.pending_requests["rearrange_jokers"] = {
    condition = utils.COMPLETION_CONDITIONS["rearrange_jokers"][""],
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Rearranges the consumables based on the given card indices
---Call G.FUNCS.rearrange_consumables(new_consumables)
---@param args RearrangeConsumablesArgs The card indices to rearrange the consumables with
API.functions["rearrange_consumables"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "consumables" })

  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Validate that consumables exist
  if not G.consumeables or not G.consumeables.cards or #G.consumeables.cards == 0 then
    API.send_error_response(
      "No consumables available to rearrange",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { consumables_available = false }
    )
    return
  end

  -- Validate number of consumables is equal to the number of consumables in the consumables area
  if #args.consumables ~= #G.consumeables.cards then
    API.send_error_response(
      "Invalid number of consumables to rearrange",
      ERROR_CODES.PARAMETER_OUT_OF_RANGE,
      { consumables_count = #args.consumables, valid_range = tostring(#G.consumeables.cards) }
    )
    return
  end

  -- Convert incoming indices from 0-based to 1-based
  for i, consumable_index in ipairs(args.consumables) do
    args.consumables[i] = consumable_index + 1
  end

  -- Create a new consumables array to swap card indices
  local new_consumables = {}
  for _, old_index in ipairs(args.consumables) do
    local card = G.consumeables.cards[old_index]
    if not card then
      API.send_error_response(
        "Consumable index out of range",
        ERROR_CODES.PARAMETER_OUT_OF_RANGE,
        { index = old_index, max_index = #G.consumeables.cards }
      )
      return
    end
    table.insert(new_consumables, card)
  end

  G.consumeables.cards = new_consumables

  -- Update each consumable's order field so future sort('order') calls work correctly
  for i, card in ipairs(G.consumeables.cards) do
    if card.ability then
      card.ability.order = i
    end
    if card.config and card.config.center then
      card.config.center.order = i
    end
  end

  ---@type PendingRequest
  API.pending_requests["rearrange_consumables"] = {
    condition = utils.COMPLETION_CONDITIONS["rearrange_consumables"][""],
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
    condition = utils.COMPLETION_CONDITIONS["cash_out"][""],
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
      condition = utils.COMPLETION_CONDITIONS["shop"]["next_round"],
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

    -- activate the buy button using the UI element handler
    G.FUNCS.buy_from_shop(card_buy_button)

    -- send response once shop is updated
    ---@type PendingRequest
    API.pending_requests["shop"] = {
      condition = function()
        return utils.COMPLETION_CONDITIONS["shop"]["buy_card"]()
      end,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
    }
  elseif action == "reroll" then
    -- Capture the state before rerolling for response validation
    local dollars_before = G.GAME.dollars
    local reroll_cost = G.GAME.current_round and G.GAME.current_round.reroll_cost or 0

    if dollars_before < reroll_cost then
      API.send_error_response(
        "Not enough dollars to reroll",
        ERROR_CODES.INVALID_ACTION,
        { dollars = dollars_before, reroll_cost = reroll_cost }
      )
      return
    end

    -- no UI element required for reroll
    G.FUNCS.reroll_shop(nil)

    ---@type PendingRequest
    API.pending_requests["shop"] = {
      condition = function()
        return utils.COMPLETION_CONDITIONS["shop"]["reroll"]()
      end,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
    }
  elseif action == "redeem_voucher" then
    -- Validate index argument
    if args.index == nil then
      API.send_error_response("Missing required field: index", ERROR_CODES.MISSING_ARGUMENTS, { field = "index" })
      return
    end

    local area = G.shop_vouchers

    if not area then
      API.send_error_response("Voucher area not found in shop", ERROR_CODES.INVALID_GAME_STATE, {})
      return
    end

    -- Get voucher index (1-based) and validate range
    local card_pos = args.index + 1
    if not area.cards or not area.cards[card_pos] then
      API.send_error_response(
        "Voucher index out of range",
        ERROR_CODES.PARAMETER_OUT_OF_RANGE,
        { index = args.index, valid_range = "0-" .. tostring(#area.cards - 1) }
      )
      return
    end

    local card = area.cards[card_pos]
    -- Check affordability
    local dollars_before = G.GAME.dollars
    if dollars_before < card.cost then
      API.send_error_response(
        "Not enough dollars to redeem voucher",
        ERROR_CODES.INVALID_ACTION,
        { dollars = dollars_before, cost = card.cost }
      )
      return
    end

    -- Activate the voucher's purchase button to redeem
    local use_button = card.children.buy_button and card.children.buy_button.definition
    G.FUNCS.use_card(use_button)

    -- Wait until the shop is idle and dollars are updated (redeem is non-atomic)
    ---@type PendingRequest
    API.pending_requests["shop"] = {
      condition = function()
        return utils.COMPLETION_CONDITIONS["shop"]["redeem_voucher"]()
      end,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
    }

  elseif action == "buy_and_use_card" then
    -- Validate index argument
    if args.index == nil then
      API.send_error_response("Missing required field: index", ERROR_CODES.MISSING_ARGUMENTS, { field = "index" })
      return
    end

    -- Get card index (1-based) and shop area (shop_jokers also holds consumables)
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

    -- Locate the Buy & Use button definition
    local buy_and_use_button = card.children.buy_and_use_button and card.children.buy_and_use_button.definition
    if not buy_and_use_button then
      API.send_error_response(
        "Card has no buy_and_use button",
        ERROR_CODES.INVALID_GAME_STATE,
        { index = args.index, card_name = card.name }
      )
      return
    end

    -- Activate the buy_and_use button via the game's shop function
    G.FUNCS.buy_from_shop(buy_and_use_button)

    -- Defer sending response until the shop has processed the purchase and use
    ---@type PendingRequest
    API.pending_requests["shop"] = {
      condition = function()
        return utils.COMPLETION_CONDITIONS["shop"]["buy_and_use_card"]()
      end,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
    }
  elseif action == "open_pack" then
    -- TODO: add open_pack
  else
    API.send_error_response(
      "Invalid action for shop",
      ERROR_CODES.INVALID_ACTION,
      { action = action, valid_actions = { "next_round", "buy_card", "reroll", "buy_and_use_card", "redeem_voucher" } }
    )
    return
  end
end

---Sells a joker at the specified index
---Call G.FUNCS.sell_card() to sell the joker at the given index
---@param args SellJokerArgs The sell joker action arguments
API.functions["sell_joker"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "index" })
  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Validate that jokers exist
  if not G.jokers or not G.jokers.cards or #G.jokers.cards == 0 then
    API.send_error_response(
      "No jokers available to sell",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { jokers_available = false }
    )
    return
  end

  -- Validate that index is a number
  if type(args.index) ~= "number" then
    API.send_error_response(
      "Invalid parameter type",
      ERROR_CODES.INVALID_PARAMETER,
      { parameter = "index", expected_type = "number" }
    )
    return
  end

  -- Convert from 0-based to 1-based indexing
  local joker_index = args.index + 1

  -- Validate joker index is in range
  if joker_index < 1 or joker_index > #G.jokers.cards then
    API.send_error_response(
      "Joker index out of range",
      ERROR_CODES.PARAMETER_OUT_OF_RANGE,
      { index = args.index, jokers_count = #G.jokers.cards }
    )
    return
  end

  -- Get the joker card
  local joker_card = G.jokers.cards[joker_index]
  if not joker_card then
    API.send_error_response("Joker not found at index", ERROR_CODES.MISSING_GAME_OBJECT, { index = args.index })
    return
  end

  -- Check if the joker can be sold
  if not joker_card:can_sell_card() then
    API.send_error_response("Joker cannot be sold at this time", ERROR_CODES.INVALID_ACTION, { index = args.index })
    return
  end

  -- Create a mock UI element to call G.FUNCS.sell_card
  local mock_element = {
    config = {
      ref_table = joker_card,
    },
  }

  -- Call G.FUNCS.sell_card to sell the joker
  G.FUNCS.sell_card(mock_element)

  ---@type PendingRequest
  API.pending_requests["sell_joker"] = {
    condition = function()
      return utils.COMPLETION_CONDITIONS["sell_joker"][""]()
    end,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Uses a consumable at the specified index
---Call G.FUNCS.use_card() to use the consumable at the given index
---@param args UseConsumableArgs The use consumable action arguments
API.functions["use_consumable"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "index" })
  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Validate that consumables exist
  if not G.consumeables or not G.consumeables.cards or #G.consumeables.cards == 0 then
    API.send_error_response(
      "No consumables available to use",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { consumables_available = false }
    )
    return
  end

  -- Validate that index is a number and an integer
  if type(args.index) ~= "number" then
    API.send_error_response(
      "Invalid parameter type",
      ERROR_CODES.INVALID_PARAMETER,
      { parameter = "index", expected_type = "number" }
    )
    return
  end

  -- Validate that index is an integer
  if args.index % 1 ~= 0 then
    API.send_error_response(
      "Invalid parameter type",
      ERROR_CODES.INVALID_PARAMETER,
      { parameter = "index", expected_type = "integer" }
    )
    return
  end

  -- Convert from 0-based to 1-based indexing
  local consumable_index = args.index + 1

  -- Validate consumable index is in range
  if consumable_index < 1 or consumable_index > #G.consumeables.cards then
    API.send_error_response(
      "Consumable index out of range",
      ERROR_CODES.PARAMETER_OUT_OF_RANGE,
      { index = args.index, consumables_count = #G.consumeables.cards }
    )
    return
  end

  -- Get the consumable card
  local consumable_card = G.consumeables.cards[consumable_index]
  if not consumable_card then
    API.send_error_response("Consumable not found at index", ERROR_CODES.MISSING_GAME_OBJECT, { index = args.index })
    return
  end

  -- Check if the consumable can be used
  if not consumable_card:can_use_consumeable() then
    API.send_error_response(
      "Consumable cannot be used at this time",
      ERROR_CODES.INVALID_ACTION,
      { index = args.index }
    )
    return
  end

  -- Create a mock UI element to call G.FUNCS.use_card
  local mock_element = {
    config = {
      ref_table = consumable_card,
    },
  }

  -- Call G.FUNCS.use_card to use the consumable
  G.FUNCS.use_card(mock_element)

  ---@type PendingRequest
  API.pending_requests["use_consumable"] = {
    condition = function()
      return utils.COMPLETION_CONDITIONS["use_consumable"][""]()
    end,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Sells a consumable at the specified index
---Call G.FUNCS.sell_card() to sell the consumable at the given index
---@param args SellConsumableArgs The sell consumable action arguments
API.functions["sell_consumable"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "index" })
  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Validate that consumables exist
  if not G.consumeables or not G.consumeables.cards or #G.consumeables.cards == 0 then
    API.send_error_response(
      "No consumables available to sell",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { consumables_available = false }
    )
    return
  end

  -- Validate that index is a number
  if type(args.index) ~= "number" then
    API.send_error_response(
      "Invalid parameter type",
      ERROR_CODES.INVALID_PARAMETER,
      { parameter = "index", expected_type = "number" }
    )
    return
  end

  -- Convert from 0-based to 1-based indexing
  local consumable_index = args.index + 1

  -- Validate consumable index is in range
  if consumable_index < 1 or consumable_index > #G.consumeables.cards then
    API.send_error_response(
      "Consumable index out of range",
      ERROR_CODES.PARAMETER_OUT_OF_RANGE,
      { index = args.index, consumables_count = #G.consumeables.cards }
    )
    return
  end

  -- Get the consumable card
  local consumable_card = G.consumeables.cards[consumable_index]
  if not consumable_card then
    API.send_error_response("Consumable not found at index", ERROR_CODES.MISSING_GAME_OBJECT, { index = args.index })
    return
  end

  -- Check if the consumable can be sold
  if not consumable_card:can_sell_card() then
    API.send_error_response(
      "Consumable cannot be sold at this time",
      ERROR_CODES.INVALID_ACTION,
      { index = args.index }
    )
    return
  end

  -- Create a mock UI element to call G.FUNCS.sell_card
  local mock_element = {
    config = {
      ref_table = consumable_card,
    },
  }

  -- Call G.FUNCS.sell_card to sell the consumable
  G.FUNCS.sell_card(mock_element)

  ---@type PendingRequest
  API.pending_requests["sell_consumable"] = {
    condition = function()
      return utils.COMPLETION_CONDITIONS["sell_consumable"][""]()
    end,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

--------------------------------------------------------------------------------
-- Checkpoint System
--------------------------------------------------------------------------------

---Creates a checkpoint directory if it doesn't exist
---@return string The checkpoint directory path
local function ensure_checkpoint_dir()
  local checkpoint_dir = "checkpoints"
  if not love.filesystem.getInfo(checkpoint_dir) then
    love.filesystem.createDirectory(checkpoint_dir)
  end
  return checkpoint_dir
end

---Saves current game state to a checkpoint
---@param args table Arguments containing checkpoint_name (optional)
API.functions["save_checkpoint"] = function(args)
  -- Ensure we're in a valid game state
  if not G.GAME or not G.GAME.round then
    API.send_error_response("No active game to checkpoint", ERROR_CODES.INVALID_GAME_STATE)
    return
  end

  -- Trigger the native save function
  save_run()

  ---@type PendingRequest
  API.pending_requests["save_checkpoint"] = {
    condition = function()
      -- Wait for save to complete
      return G.FILE_HANDLER and not G.FILE_HANDLER.update_queued
    end,
    action = function()
      -- Read the save file
      local save_path = G.SETTINGS.profile .. "/save.jkr"
      local save_data = get_compressed(save_path)

      if not save_data then
        API.send_error_response("Failed to read save file", ERROR_CODES.INVALID_GAME_STATE)
        return
      end

      -- Generate checkpoint name if not provided
      local checkpoint_name = args.checkpoint_name
      if not checkpoint_name then
        checkpoint_name = os.date("%Y%m%d_%H%M%S") .. "_checkpoint"
      end

      -- Ensure checkpoint directory exists
      local checkpoint_dir = ensure_checkpoint_dir()
      local checkpoint_path = checkpoint_dir .. "/" .. checkpoint_name .. ".jkr"

      -- Write checkpoint file (already compressed)
      love.filesystem.write(checkpoint_path, save_data)

      -- Also save metadata about the checkpoint
      local metadata = {
        name = checkpoint_name,
        created_at = os.time(),
        profile = G.SETTINGS.profile,
        round = G.GAME.round,
        ante = G.GAME.round_resets.ante,
        dollars = G.GAME.dollars,
        deck = G.GAME.selected_back_key or "Unknown",
        stake = G.GAME.stake or 1,
      }

      local metadata_path = checkpoint_dir .. "/" .. checkpoint_name .. ".meta"
      love.filesystem.write(metadata_path, json.encode(metadata))

      API.send_response({
        success = true,
        checkpoint_name = checkpoint_name,
        metadata = metadata,
      })
    end,
  }
end

---Loads a game state from a checkpoint
---@param args table Arguments containing checkpoint_name and optional mode
API.functions["load_checkpoint"] = function(args)
  local valid, err_msg, err_code = validate_request(args, { "checkpoint_name" })
  if not valid then
    API.send_error_response(err_msg, err_code)
    return
  end

  local checkpoint_dir = ensure_checkpoint_dir()
  local checkpoint_path = checkpoint_dir .. "/" .. args.checkpoint_name .. ".jkr"

  -- Check if checkpoint exists
  if not love.filesystem.getInfo(checkpoint_path) then
    API.send_error_response(
      "Checkpoint not found",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { checkpoint_name = args.checkpoint_name }
    )
    return
  end

  -- Read checkpoint data
  local checkpoint_data = love.filesystem.read(checkpoint_path)
  if not checkpoint_data then
    API.send_error_response(
      "Failed to read checkpoint",
      ERROR_CODES.INVALID_GAME_STATE,
      { checkpoint_name = args.checkpoint_name }
    )
    return
  end

  -- Determine load mode (default to "restart" for full game restart)
  local mode = args.mode or "restart"

  if mode == "restart" then
    -- Full restart: Write checkpoint to save file and restart the run
    local save_path = G.SETTINGS.profile .. "/save.jkr"
    love.filesystem.write(save_path, checkpoint_data)

    -- Delete current run and reload from checkpoint
    G:delete_run()
    G.SAVED_GAME = get_compressed(save_path)
    if G.SAVED_GAME ~= nil then
      G.SAVED_GAME = STR_UNPACK(G.SAVED_GAME)
    end

    -- Start the run from saved state
    G:start_run({ savetext = G.SAVED_GAME })

    ---@type PendingRequest
    API.pending_requests["load_checkpoint"] = {
      condition = function()
        -- Wait for game to be fully loaded
        return G.STATE and G.GAME and G.GAME.round and not G.CONTROLLER.locks.load
      end,
      action = function()
        API.send_response({
          success = true,
          checkpoint_name = args.checkpoint_name,
          mode = mode,
          state = G.STATE,
          round = G.GAME.round,
          ante = G.GAME.round_resets.ante,
        })
      end,
    }
  elseif mode == "overwrite" then
    -- Just overwrite the save file without restarting
    -- Useful for setting up a checkpoint to be loaded on next game start
    local save_path = G.SETTINGS.profile .. "/save.jkr"
    love.filesystem.write(save_path, checkpoint_data)

    API.send_response({
      success = true,
      checkpoint_name = args.checkpoint_name,
      mode = mode,
      message = "Save file overwritten. Checkpoint will be loaded on next game start.",
    })
  elseif mode == "resume" then
    -- Attempt to resume mid-action by restoring state more granularly
    -- This is experimental and may not work for all game states

    -- Decompress and parse the checkpoint
    local decompressed = checkpoint_data
    if string.sub(decompressed, 1, 6) ~= "return" then
      local success
      success, decompressed = pcall(love.data.decompress, "string", "deflate", checkpoint_data)
      if not success then
        API.send_error_response("Failed to decompress checkpoint", ERROR_CODES.INVALID_GAME_STATE)
        return
      end
    end

    local checkpoint_state = STR_UNPACK(decompressed)

    -- Try to restore the game state while preserving current UI
    if checkpoint_state then
      -- Restore card areas
      if checkpoint_state.cardAreas then
        for k, v in pairs(checkpoint_state.cardAreas) do
          if G[k] and G[k].load then
            G[k]:load(v)
          end
        end
      end

      -- Restore game state
      if checkpoint_state.GAME then
        -- Preserve certain UI states
        local current_state = G.STATE
        G.GAME = checkpoint_state.GAME

        -- Restore blind
        if checkpoint_state.BLIND then
          G.GAME.blind = Blind(checkpoint_state.BLIND.config.blind)
          G.GAME.blind:load(checkpoint_state.BLIND)
        end

        -- Restore deck
        if checkpoint_state.BACK then
          G.GAME.selected_back = Back(checkpoint_state.BACK.name)
          G.GAME.selected_back:load(checkpoint_state.BACK)
        end

        -- Try to maintain current state if compatible
        if checkpoint_state.STATE and (current_state == G.STATES.MENU or args.force_state) then
          G.STATE = checkpoint_state.STATE
        end
      end

      -- Restore tags
      if checkpoint_state.tags then
        G.GAME.tags = {}
        for k, v in ipairs(checkpoint_state.tags) do
          local tag = Tag(v.key)
          tag:load(v)
          G.GAME.tags[k] = tag
        end
      end

      API.send_response({
        success = true,
        checkpoint_name = args.checkpoint_name,
        mode = mode,
        state = G.STATE,
        round = G.GAME and G.GAME.round or 0,
        ante = G.GAME and G.GAME.round_resets and G.GAME.round_resets.ante or 0,
        message = "Checkpoint partially restored. Some UI elements may need refresh.",
      })
    else
      API.send_error_response("Failed to parse checkpoint data", ERROR_CODES.INVALID_GAME_STATE)
    end
  else
    API.send_error_response(
      "Invalid load mode",
      ERROR_CODES.INVALID_PARAMETER,
      { mode = mode, valid_modes = { "restart", "overwrite", "resume" } }
    )
  end
end

---Lists all available checkpoints
---@param _ table Arguments (not used)
API.functions["list_checkpoints"] = function(_)
  local checkpoint_dir = ensure_checkpoint_dir()
  local checkpoints = {}

  -- Get all files in checkpoint directory
  local files = love.filesystem.getDirectoryItems(checkpoint_dir)

  for _, filename in ipairs(files) do
    -- Only process .meta files
    if filename:match("%.meta$") then
      local base_name = filename:gsub("%.meta$", "")
      local meta_path = checkpoint_dir .. "/" .. filename
      local checkpoint_path = checkpoint_dir .. "/" .. base_name .. ".jkr"

      -- Check that both files exist
      if love.filesystem.getInfo(checkpoint_path) then
        local meta_data = love.filesystem.read(meta_path)
        if meta_data then
          local ok, metadata = pcall(json.decode, meta_data)
          if ok then
            table.insert(checkpoints, metadata)
          end
        end
      end
    end
  end

  -- Sort by creation time (newest first)
  table.sort(checkpoints, function(a, b)
    return (a.created_at or 0) > (b.created_at or 0)
  end)

  API.send_response({
    checkpoints = checkpoints,
  })
end

---Deletes a checkpoint
---@param args table Arguments containing checkpoint_name
API.functions["delete_checkpoint"] = function(args)
  local valid, err_msg, err_code = validate_request(args, { "checkpoint_name" })
  if not valid then
    API.send_error_response(err_msg, err_code)
    return
  end

  local checkpoint_dir = ensure_checkpoint_dir()
  local checkpoint_path = checkpoint_dir .. "/" .. args.checkpoint_name .. ".jkr"
  local metadata_path = checkpoint_dir .. "/" .. args.checkpoint_name .. ".meta"

  -- Check if checkpoint exists
  if not love.filesystem.getInfo(checkpoint_path) then
    API.send_error_response(
      "Checkpoint not found",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { checkpoint_name = args.checkpoint_name }
    )
    return
  end

  -- Remove both checkpoint and metadata files
  love.filesystem.remove(checkpoint_path)
  love.filesystem.remove(metadata_path)

  API.send_response({
    success = true,
    deleted = args.checkpoint_name,
  })
end

---Exports checkpoint data as base64 for external storage
---@param args table Arguments containing checkpoint_name
API.functions["export_checkpoint"] = function(args)
  local valid, err_msg, err_code = validate_request(args, { "checkpoint_name" })
  if not valid then
    API.send_error_response(err_msg, err_code)
    return
  end

  local checkpoint_dir = ensure_checkpoint_dir()
  local checkpoint_path = checkpoint_dir .. "/" .. args.checkpoint_name .. ".jkr"
  local metadata_path = checkpoint_dir .. "/" .. args.checkpoint_name .. ".meta"

  -- Check if checkpoint exists
  if not love.filesystem.getInfo(checkpoint_path) then
    API.send_error_response(
      "Checkpoint not found",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { checkpoint_name = args.checkpoint_name }
    )
    return
  end

  -- Read checkpoint and metadata
  local checkpoint_data = love.filesystem.read(checkpoint_path)
  local metadata = love.filesystem.read(metadata_path)

  if not checkpoint_data then
    API.send_error_response("Failed to read checkpoint", ERROR_CODES.INVALID_GAME_STATE)
    return
  end

  -- Encode to base64 for safe transport
  local encoded_data = love.data.encode("string", "base64", checkpoint_data)

  API.send_response({
    checkpoint_name = args.checkpoint_name,
    data = encoded_data,
    metadata = metadata and json.decode(metadata) or nil,
  })
end

---Imports checkpoint data from base64
---@param args table Arguments containing checkpoint_name and data
API.functions["import_checkpoint"] = function(args)
  local valid, err_msg, err_code = validate_request(args, { "checkpoint_name", "data" })
  if not valid then
    API.send_error_response(err_msg, err_code)
    return
  end

  -- Decode from base64
  local success, checkpoint_data = pcall(love.data.decode, "string", "base64", args.data)
  if not success then
    API.send_error_response(
      "Failed to decode checkpoint data",
      ERROR_CODES.INVALID_ARGUMENTS,
      { error = tostring(checkpoint_data) }
    )
    return
  end

  -- Ensure checkpoint directory exists
  local checkpoint_dir = ensure_checkpoint_dir()
  local checkpoint_path = checkpoint_dir .. "/" .. args.checkpoint_name .. ".jkr"
  local metadata_path = checkpoint_dir .. "/" .. args.checkpoint_name .. ".meta"

  -- Write checkpoint file
  love.filesystem.write(checkpoint_path, checkpoint_data)

  -- Create or update metadata
  local metadata = args.metadata
    or {
      name = args.checkpoint_name,
      created_at = os.time(),
      imported = true,
    }

  love.filesystem.write(metadata_path, json.encode(metadata))

  API.send_response({
    success = true,
    checkpoint_name = args.checkpoint_name,
    message = "Checkpoint imported successfully",
  })
end

---Sets the active profile's save to a checkpoint without restarting
---@param args table Arguments containing checkpoint_name and optional profile
API.functions["set_profile_save"] = function(args)
  local valid, err_msg, err_code = validate_request(args, { "checkpoint_name" })
  if not valid then
    API.send_error_response(err_msg, err_code)
    return
  end

  local checkpoint_dir = ensure_checkpoint_dir()
  local checkpoint_path = checkpoint_dir .. "/" .. args.checkpoint_name .. ".jkr"

  -- Check if checkpoint exists
  if not love.filesystem.getInfo(checkpoint_path) then
    API.send_error_response(
      "Checkpoint not found",
      ERROR_CODES.MISSING_GAME_OBJECT,
      { checkpoint_name = args.checkpoint_name }
    )
    return
  end

  -- Read checkpoint data
  local checkpoint_data = love.filesystem.read(checkpoint_path)
  if not checkpoint_data then
    API.send_error_response("Failed to read checkpoint", ERROR_CODES.INVALID_GAME_STATE)
    return
  end

  -- Determine target profile (default to current)
  local target_profile = args.profile or G.SETTINGS.profile
  local save_path = target_profile .. "/save.jkr"

  -- Write to the profile's save file
  love.filesystem.write(save_path, checkpoint_data)

  API.send_response({
    success = true,
    checkpoint_name = args.checkpoint_name,
    profile = target_profile,
    message = "Profile save updated. Will be loaded on next game start or continue.",
  })
end

return API
