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
        API.send_error_response(
          "Invalid JSON: message could not be parsed. Send one JSON object per line with fields 'name' and 'arguments'",
          ERROR_CODES.INVALID_JSON,
          nil
        )
        return
      end
      ---@cast data APIRequest
      if data.name == nil then
        API.send_error_response(
          "Message must contain a name. Include a 'name' field, e.g. 'get_game_state'",
          ERROR_CODES.MISSING_NAME,
          nil
        )
      elseif data.arguments == nil then
        API.send_error_response(
          "Message must contain arguments. Include an 'arguments' object (use {} if no parameters)",
          ERROR_CODES.MISSING_ARGUMENTS,
          nil
        )
      else
        local func = API.functions[data.name]
        local args = data.arguments
        if func == nil then
          API.send_error_response(
            "Unknown function name. See docs for supported names. Common calls: 'get_game_state', 'start_run', 'shop', 'play_hand_or_discard'",
            ERROR_CODES.UNKNOWN_FUNCTION,
            { name = data.name }
          )
        elseif type(args) ~= "table" then
          API.send_error_response(
            "Arguments must be a table. The 'arguments' field must be a JSON object/table (use {} if empty)",
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
      "Cannot skip or select blind when not in blind selection. Wait until gamestate is BLIND_SELECT, or call 'shop' with action 'next_round' to advance out of the shop. Use 'get_game_state' to check the current state.",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE, expected_state = G.STATES.BLIND_SELECT }
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
      "Cannot play hand or discard when not in selecting hand state. First select the blind: call 'skip_or_select_blind' with action 'select' when selecting blind. Use 'get_game_state' to verify.",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE, expected_state = G.STATES.SELECTING_HAND }
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
      "No discards left to perform discard. Play a hand or advance the round; discards will reset next round.",
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

  -- Clear any existing highlights before selecting new cards to prevent state pollution
  G.hand:unhighlight_all()

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
      "Cannot rearrange hand when not selecting hand. You can only rearrange while selecting your hand. You can check the current gamestate with 'get_game_state'.",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE, expected_state = G.STATES.SELECTING_HAND }
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
      "Cannot cash out when not in round evaluation. Finish playing the hand to reach ROUND_EVAL first.",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE, expected_state = G.STATES.ROUND_EVAL }
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
      "Cannot select shop action when not in shop. Reach the shop by calling 'cash_out' during ROUND_EVAL, or finish a hand to enter evaluation.",
      ERROR_CODES.INVALID_GAME_STATE,
      { current_state = G.STATE, expected_state = G.STATES.SHOP }
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
        "Card is not affordable, choose a purchasable card or advance with 'shop' with action 'next_round'.",
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
        "Not enough dollars to reroll. You may use the 'shop' function with action 'next_round' to advance to the next round.",
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
        "Card is not affordable. Choose a cheaper card or advance with 'shop' with action 'next_round'.",
        ERROR_CODES.INVALID_ACTION,
        { index = args.index, cost = card.cost, dollars = G.GAME.dollars }
      )
      return
    end

    -- Check if the consumable can be used
    if not card:can_use_consumeable() then
      API.send_error_response(
        "Consumable cannot be used at this time",
        ERROR_CODES.INVALID_ACTION,
        { index = args.index }
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
  -- TODO: add other shop actions (open_pack)
  else
    API.send_error_response(
      "Invalid action for shop",
      ERROR_CODES.INVALID_ACTION,
      { action = action, valid_actions = { "next_round", "buy_card", "reroll" } }
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

  -- Get consumable's card requirements
  local max_cards = consumable_card.ability.consumeable.max_highlighted
  local min_cards = consumable_card.ability.consumeable.min_highlighted or 1
  local consumable_name = consumable_card.ability.name or "Unknown"
  local required_cards = max_cards ~= nil

  -- Validate cards parameter type if provided
  if args.cards ~= nil then
    if type(args.cards) ~= "table" then
      API.send_error_response(
        "Invalid parameter type for cards. Expected array, got " .. tostring(type(args.cards)),
        ERROR_CODES.INVALID_PARAMETER,
        { parameter = "cards", expected_type = "array" }
      )
      return
    end

    -- Validate all elements are numbers
    for i, card_index in ipairs(args.cards) do
      if type(card_index) ~= "number" then
        API.send_error_response(
          "Invalid card index type. Expected number, got " .. tostring(type(card_index)),
          ERROR_CODES.INVALID_PARAMETER,
          { index = i - 1, value_type = type(card_index) }
        )
        return
      end
    end
  end

  -- The consumable does not require any card selection
  if not required_cards and args.cards then
    if #args.cards > 0 then
      API.send_error_response(
        "The selected consumable does not require card selection. Cards array must be empty or no cards array at all.",
        ERROR_CODES.INVALID_PARAMETER,
        { consumable_name = consumable_name }
      )
      return
    end
    -- If cards=[] (empty), that's fine, just skip the card selection logic
  end

  if required_cards then
    if G.STATE ~= G.STATES.SELECTING_HAND then
      API.send_error_response(
        "Cannot use consumable with cards when there are no cards to select. Expects SELECTING_HAND state.",
        ERROR_CODES.INVALID_GAME_STATE,
        { current_state = G.STATE, required_state = G.STATES.SELECTING_HAND }
      )
      return
    end

    local num_cards = args.cards == nil and 0 or #args.cards
    if num_cards < min_cards or num_cards > max_cards then
      local range_msg = min_cards == max_cards and ("exactly " .. min_cards) or (min_cards .. "-" .. max_cards)
      API.send_error_response(
        "Invalid number of cards for "
          .. consumable_name
          .. ". Expected "
          .. range_msg
          .. ", got "
          .. tostring(num_cards),
        ERROR_CODES.PARAMETER_OUT_OF_RANGE,
        { cards_count = num_cards, min_cards = min_cards, max_cards = max_cards, consumable_name = consumable_name }
      )
      return
    end

    -- Convert from 0-based to 1-based indexing
    for i, card_index in ipairs(args.cards) do
      args.cards[i] = card_index + 1
    end

    -- Check that all cards exist and are selectable
    for _, card_index in ipairs(args.cards) do
      if not G.hand or not G.hand.cards or not G.hand.cards[card_index] then
        API.send_error_response(
          "Invalid card index",
          ERROR_CODES.INVALID_CARD_INDEX,
          { card_index = card_index - 1, hand_size = G.hand and G.hand.cards and #G.hand.cards or 0 }
        )
        return
      end
    end

    -- Clear any existing highlights before selecting new cards
    if G.hand then
      G.hand:unhighlight_all()
    end

    -- Select cards for the consumable to target
    for _, card_index in ipairs(args.cards) do
      G.hand.cards[card_index]:click()
    end
  end

  -- Check if the consumable can be used
  if not consumable_card:can_use_consumeable() then
    local error_msg = "Consumable cannot be used for unknown reason."
    API.send_error_response(error_msg, ERROR_CODES.INVALID_ACTION, {})
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

---Gets the current save file location and profile information
---Note that this will return a non-existent windows path linux, see normalization in client.py
---@param _ table Arguments (not used)
API.functions["get_save_info"] = function(_)
  local save_info = {
    profile_path = G.SETTINGS and G.SETTINGS.profile or nil,
    save_directory = love and love.filesystem and love.filesystem.getSaveDirectory() or nil,
    has_active_run = G.GAME and G.GAME.round and true or false,
  }

  -- Construct full save file path
  if save_info.save_directory and save_info.profile_path then
    -- Full OS path to the save file
    save_info.save_file_path = save_info.save_directory .. "/" .. save_info.profile_path .. "/save.jkr"
  elseif save_info.profile_path then
    -- Fallback to relative path if we can't get save directory
    save_info.save_file_path = save_info.profile_path .. "/save.jkr"
  else
    save_info.save_file_path = nil
  end

  -- Check if save file exists (using the relative path for Love2D filesystem)
  if save_info.profile_path then
    local relative_path = save_info.profile_path .. "/save.jkr"
    local save_data = get_compressed(relative_path)
    save_info.save_exists = save_data ~= nil
  else
    save_info.save_exists = false
  end

  API.send_response(save_info)
end

---Loads a save file directly and starts a run from it
---This allows loading a specific save state without requiring a game restart
---@param args LoadSaveArgs Arguments containing the save file path
API.functions["load_save"] = function(args)
  -- Validate required parameters
  local success, error_message, error_code, context = validate_request(args, { "save_path" })
  if not success then
    ---@cast error_message string
    ---@cast error_code string
    API.send_error_response(error_message, error_code, context)
    return
  end

  -- Load the save file using get_compressed
  local save_data = get_compressed(args.save_path)
  if not save_data then
    API.send_error_response("Failed to load save file", ERROR_CODES.MISSING_GAME_OBJECT, { save_path = args.save_path })
    return
  end

  -- Unpack the save data
  local success, save_table = pcall(STR_UNPACK, save_data)
  if not success then
    API.send_error_response(
      "Failed to parse save file",
      ERROR_CODES.INVALID_PARAMETER,
      { save_path = args.save_path, error = tostring(save_table) }
    )
    return
  end

  -- Delete current run if exists
  G:delete_run()

  -- Start run with the loaded save
  G:start_run({ savetext = save_table })

  -- Wait for run to start
  ---@type PendingRequest
  API.pending_requests["load_save"] = {
    condition = function()
      return utils.COMPLETION_CONDITIONS["load_save"][""]()
    end,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Takes a screenshot of the current game state and saves it to LÖVE's write directory
---Call love.graphics.captureScreenshot() to capture the current frame as compressed PNG image
---Returns the path where the screenshot was saved
API.functions["screenshot"] = function(args)
  -- Track screenshot completion
  local screenshot_completed = false
  local screenshot_error = nil
  local screenshot_filename = nil

  -- Generate unique filename within LÖVE's write directory
  local timestamp = tostring(love.timer.getTime()):gsub("%.", "")
  screenshot_filename = "screenshot_" .. timestamp .. ".png"

  -- Capture screenshot using LÖVE 11.0+ API
  love.graphics.captureScreenshot(function(imagedata)
    if imagedata then
      -- Scale down the image to reduce file size (10% of original size)
      local original_width = imagedata:getWidth()
      local original_height = imagedata:getHeight()
      local scale_factor = 0.2
      local new_width = math.floor(original_width * scale_factor)
      local new_height = math.floor(original_height * scale_factor)

      -- Create a new scaled ImageData
      local scaled_imagedata = love.image.newImageData(new_width, new_height)

      -- Scale the image by sampling pixels
      for y = 0, new_height - 1 do
        for x = 0, new_width - 1 do
          local src_x = math.floor(x / scale_factor)
          local src_y = math.floor(y / scale_factor)
          local r, g, b, a = imagedata:getPixel(src_x, src_y)
          scaled_imagedata:setPixel(x, y, r, g, b, a)
        end
      end

      -- Save the screenshot as PNG to LÖVE's write directory
      local png_success, png_err = pcall(function()
        scaled_imagedata:encode("png", screenshot_filename)
      end)

      if png_success then
        screenshot_completed = true
        sendDebugMessage("Screenshot saved: " .. screenshot_filename, "API")
      else
        screenshot_error = "Failed to save PNG screenshot: " .. tostring(png_err)
        sendErrorMessage(screenshot_error, "API")
      end
    else
      screenshot_error = "Failed to capture screenshot"
      sendErrorMessage(screenshot_error, "API")
    end
  end)

  -- Defer sending response until the screenshot operation completes
  ---@type PendingRequest
  API.pending_requests["screenshot"] = {
    condition = function()
      return screenshot_completed or screenshot_error ~= nil
    end,
    action = function()
      if screenshot_error then
        API.send_error_response(screenshot_error, ERROR_CODES.INVALID_ACTION, {})
      else
        -- Return screenshot path
        local screenshot_response = {
          path = love.filesystem.getSaveDirectory() .. "/" .. screenshot_filename,
        }
        API.send_response(screenshot_response)
      end
    end,
  }
end

return API
