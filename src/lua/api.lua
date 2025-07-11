local socket = require("socket")
local json = require("json")

-- Constants
local UDP_BUFFER_SIZE = 65536
local SOCKET_TIMEOUT = 0
local EVENT_QUEUE_THRESHOLD = 3
API = {}
API.socket = nil
API.functions = {}
API.pending_requests = {}
API.last_client_ip = nil
API.last_client_port = nil

--------------------------------------------------------------------------------
-- Update Loop
--------------------------------------------------------------------------------

---Updates the API by processing UDP messages and pending requests
---@param _ number Delta time (not used)
function API.update(_)
  -- Create socket if it doesn't exist
  if not API.socket then
    API.socket = socket.udp()
    API.socket:settimeout(SOCKET_TIMEOUT)
    local port = BALATRO_BOT_CONFIG.port
    API.socket:setsockname("127.0.0.1", tonumber(port) or 12346)
    sendDebugMessage("UDP socket created on port " .. port, "API")
  end

  -- Process pending requests
  for key, request in pairs(API.pending_requests) do
    if request.condition() then
      request.action()
      API.pending_requests[key] = nil
    end
  end

  -- Parse received data and run the appropriate function
  local raw_data, client_ip, client_port = API.socket:receivefrom(UDP_BUFFER_SIZE)
  if raw_data and client_ip and client_port then
    -- Store the last client connection
    API.last_client_ip = client_ip
    API.last_client_port = client_port

    local ok, data = pcall(json.decode, raw_data)
    if not ok then
      API.send_error_response("Invalid JSON")
      return
    end
    if data.name == nil then
      API.send_error_response("Message must contain a name")
    elseif data.arguments == nil then
      API.send_error_response("Message must contain arguments")
    else
      local func = API.functions[data.name]
      local args = data.arguments
      if func == nil then
        API.send_error_response("Unknown function name", { name = data.name })
      elseif type(args) ~= "table" then
        API.send_error_response("Arguments must be a table", { received_type = type(args) })
      else
        sendDebugMessage(data.name .. "(" .. json.encode(args) .. ")", "API")
        func(args)
      end
    end
  elseif client_ip ~= "timeout" then
    sendErrorMessage("UDP error: " .. tostring(client_ip), "API")
  end
end

---Sends a response back to the last connected client
---@param response table The response data to send
function API.send_response(response)
  if API.last_client_ip and API.last_client_port then
    API.socket:sendto(json.encode(response), API.last_client_ip, API.last_client_port)
  end
end

---Sends an error response to the client with optional context
---@param message string The error message
---@param context? table Optional additional context about the error
function API.send_error_response(message, context)
  sendErrorMessage(message, "API")
  local response = { error = message, state = G.STATE }
  if context then
    response.context = context
  end
  API.send_response(response)
end

---Initializes the API by hooking into the game's update loop and configuring settings
function API.init()
  -- Hook into the game's update loop
  local original_update = love.update
  love.update = function(_)
    original_update(BALATRO_BOT_CONFIG.dt)
    API.update(BALATRO_BOT_CONFIG.dt)
  end

  if not BALATRO_BOT_CONFIG.vsync_enabled then
    love.window.setVSync(0)
  end

  if BALATRO_BOT_CONFIG.max_fps then
    G.FPS_CAP = 60
  end

  sendInfoMessage("BalatrobotAPI initialized", "API")
end

--------------------------------------------------------------------------------
-- API Functions
--------------------------------------------------------------------------------

---Gets the current game state
---@param _ table Arguments (not used)
API.functions["get_game_state"] = function(_)
  local game_state = utils.get_game_state()
  API.send_response(game_state)
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
    condition = function()
      return G.STATE == G.STATES.MENU and G.MAIN_MENU_UI
    end,
    action = function()
      local game_state = utils.get_game_state()
      API.send_response(game_state)
    end,
  }
end

---Starts a new game run with specified parameters
---Call G.FUNCS.start_run() to start a new game run with specified parameters.
---@param args StartRunArgs The run configuration
API.functions["start_run"] = function(args)
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
    API.send_error_response("Invalid deck arg for start_run", { deck = args.deck })
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
  G.FUNCS.start_run(nil, { stake = args.stake, seed = args.seed, challenge = challenge_obj })

  -- Defer sending response until the run has started
  API.pending_requests["start_run"] = {
    condition = function()
      return G.STATE == G.STATES.BLIND_SELECT and G.GAME.blind_on_deck
    end,
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
  -- Validate current game state is appropriate for blind selection
  if G.STATE ~= G.STATES.BLIND_SELECT then
    API.send_error_response("Cannot skip or select blind when not in blind selection", { current_state = G.STATE })
    return
  end

  -- Get the current blind pane
  local current_blind = G.GAME.blind_on_deck
  assert(current_blind, "current_blind is nil")
  local blind_pane = G.blind_select_opts[string.lower(current_blind)]

  if args.action == "select" then
    local button = blind_pane:get_UIE_by_ID("select_blind_button")
    G.FUNCS.select_blind(button)
    API.pending_requests["skip_or_select_blind"] = {
      condition = function()
        return G.GAME and G.GAME.facing_blind and G.STATE == G.STATES.SELECTING_HAND
      end,
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
    API.pending_requests["skip_or_select_blind"] = {
      condition = function()
        local prev_state = {
          ["Small"] = G.prev_small_state,
          ["Large"] = G.prev_large_state, -- this is Large not Big
          ["Boss"] = G.prev_boss_state,
        }
        return prev_state[current_blind] == "Skipped"
      end,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
    }
  else
    API.send_error_response("Invalid action arg for skip_or_select_blind", { action = args.action })
    return
  end
end

---Plays selected cards or discards them
---Call G.FUNCS.play_cards_from_highlighted(play_button)
---or G.FUNCS.discard_cards_from_highlighted(discard_button)
---@param args HandActionArgs The hand action to perform
API.functions["play_hand_or_discard"] = function(args)
  -- Validate current game state is appropriate for playing hand or discarding
  if G.STATE ~= G.STATES.SELECTING_HAND then
    API.send_error_response("Cannot play hand or discard when not selecting hand", { current_state = G.STATE })
    return
  end

  if args.action == "discard" and G.GAME.current_round.discards_left == 0 then
    API.send_error_response(
      "No discards left to perform discard",
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
      API.send_error_response("Invalid card index", { card_index = card_index, hand_size = #G.hand.cards })
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
    API.send_error_response("Invalid action arg for play_hand_or_discard", { action = args.action })
    return
  end

  -- Defer sending response until the run has started
  API.pending_requests["play_hand_or_discard"] = {
    condition = function()
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
    API.send_error_response("Cannot cash out when not in shop", { current_state = G.STATE })
    return
  end

  G.FUNCS.cash_out({ config = {} })
  API.pending_requests["cash_out"] = {
    condition = function()
      return G.STATE == G.STATES.SHOP and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE
    end,
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
  -- Validate current game state is appropriate for shop
  if G.STATE ~= G.STATES.SHOP then
    API.send_error_response("Cannot select shop action when not in shop", { current_state = G.STATE })
    return
  end

  local action = args.action
  if action == "next_round" then
    G.FUNCS.toggle_shop({})
    API.pending_requests["shop"] = {
      condition = function()
        return G.STATE == G.STATES.BLIND_SELECT
          and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
          and G.STATE_COMPLETE
      end,
      action = function()
        local game_state = utils.get_game_state()
        API.send_response(game_state)
      end,
    }
  else
    API.send_error_response("Invalid action arg for shop", { action = action })
    return
  end
end

return API
