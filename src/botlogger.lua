Botlogger = {}
Botlogger.path = ""
Botlogger.filename = nil

function Botlogger.fileexists(filename)
	local _f = io.open(filename, "r")
	if _f ~= nil then
		io.close(_f)
		return true
	else
		return false
	end
end

function Botlogger.getfilename(settings)
	local _filename = ""
	_filename = _filename .. tostring(settings.seed)
	_filename = _filename .. "_" .. tostring(settings.deck)
	_filename = _filename .. "_" .. tostring(settings.stake)
	_filename = _filename .. "_" .. tostring(settings.challenge)
	local port = BALATRO_BOT_CONFIG.port
	_filename = _filename .. "_" .. port
	_filename = _filename .. ".run"
	--_filename = Botlogger.path .. _filename
	sendDebugMessage(_filename)
	return _filename
end

function Botlogger.logbotdecision(...)
	local _args = { ... }
	local _action = table.remove(_args, 1)
	local _logstring = ""

	if _action then
		for key, v in pairs(Bot.ACTIONS) do
			if _action == v then
				_logstring = key
				break
			end
		end

		for i = 1, #_args do
			_logstring = _logstring .. "|"
			if type(_args[i]) == "table" then
				for j = 1, #_args[i] do
					_logstring = _logstring .. "," .. tostring(_args[i][j])
				end
			else
				_logstring = _logstring .. tostring(_args[i])
			end
		end

		if Botlogger.filename then
			local _f = io.open(Botlogger.filename, "a")
			_f:write(_logstring, "\n")
			_f:close()
		end
	end
end

function Botlogger.start_run()
	if Bot.SETTINGS.replay and Bot.SETTINGS.replay == true then
		local _filename = Botlogger.getfilename(Bot.SETTINGS)
		if Botlogger.fileexists(_filename) then
			Botlogger.filename = _filename
		end
	else
		-- TODO if seed not specified, get it from the game
		local _filename = nil
		if Bot.SETTINGS.seed and Bot.SETTINGS.seed ~= "" then
			_filename = Botlogger.getfilename(Bot.SETTINGS)
		else
			local _settings = {
				stake = Bot.SETTINGS.stake,
				deck = Bot.SETTINGS.deck,
				seed = tostring(G.GAME.pseudorandom.seed),
				challenge = Bot.SETTINGS.challenge,
			}
			_filename = Botlogger.getfilename(_settings)
		end

		if not Botlogger.fileexists(_filename) then
			Botlogger.filename = _filename
		end
	end
end

function Botlogger.init()
	Botlogger.q_skip_or_select_blind = List.new()
	Botlogger.q_select_cards_from_hand = List.new()
	Botlogger.q_select_shop_action = List.new()
	Botlogger.q_select_booster_action = List.new()
	Botlogger.q_sell_jokers = List.new()
	Botlogger.q_rearrange_jokers = List.new()
	Botlogger.q_use_or_sell_consumables = List.new()
	Botlogger.q_rearrange_consumables = List.new()
	Botlogger.q_rearrange_hand = List.new()
	Botlogger.q_start_run = List.new()

	-- Hook bot functions
	if Bot.SETTINGS.replay == true or Bot.SETTINGS.api == true then
		-- Redefine Bot functions to just return the next action from their queue
		Botlogger.nextaction = 1
		for k, v in pairs(Bot) do
			if type(Bot[k]) == "function" then
				Bot[k] = function()
					--sendDebugMessage(k)
					if not List.isempty(Botlogger["q_" .. k]) then
						local _action = List.popright(Botlogger["q_" .. k])

						if Bot.SETTINGS.api == false and _action[1] == Botlogger.nextaction then
							Botlogger.nextaction = Botlogger.nextaction + 1
							return unpack(_action[2])
						elseif Bot.SETTINGS.api == false then
							List.pushright(Botlogger["q_" .. k], _action)
							return Bot.ACTIONS.PASS

						-- We don't care about action order for the API.
						-- When the queue is populated, return the choice.
						elseif Bot.SETTINGS.api == true then
							return unpack(_action[2])
						end
					else
						-- Return an action of "PASS" when the API is not enabled.
						-- When API is enabled, nothing is returned, and the system waits for the queue to be populated
						if Bot.SETTINGS.api == false then
							return Bot.ACTIONS.PASS
						end
					end
				end
			end
		end
	end

	-- Read replay file and populate action queues
	if Bot.SETTINGS.replay == true then
		local _replayfile = Botlogger.getfilename(Bot.SETTINGS)

		if Botlogger.fileexists(_replayfile) then
			local _num_action = 0
			for line in io.lines(_replayfile) do
				_num_action = _num_action + 1

				local _action = Utils.parseaction(line)
				sendDebugMessage(line)
				local _params = Bot.ACTIONPARAMS[_action[1]]
				for i = 2, #_action do
					sendDebugMessage(tostring(_action[i][1]))
				end
				List.pushleft(Botlogger["q_" .. _params.func], { _num_action, _action })
			end
		end
	elseif Bot.SETTINGS.replay == false then
		for k, v in pairs(Bot) do
			if type(Bot[k]) == "function" then
				Bot[k] = Hook.addcallback(Bot[k], Botlogger.logbotdecision)
			end
		end
	end

	-- TODO Hook run start/end
	G.FUNCS.start_run = Hook.addcallback(G.FUNCS.start_run, Botlogger.start_run)
end

return Botlogger

