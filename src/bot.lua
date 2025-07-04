Bot = {}

-- DO NOT TOUCH
Bot.ACTIONS = {
	SELECT_BLIND = 1,
	SKIP_BLIND = 2,
	PLAY_HAND = 3,
	DISCARD_HAND = 4,
	END_SHOP = 5,
	REROLL_SHOP = 6,
	BUY_CARD = 7,
	BUY_VOUCHER = 8,
	BUY_BOOSTER = 9,
	SELECT_BOOSTER_CARD = 10,
	SKIP_BOOSTER_PACK = 11,
	SELL_JOKER = 12,
	USE_CONSUMABLE = 13,
	SELL_CONSUMABLE = 14,
	REARRANGE_JOKERS = 15,
	REARRANGE_CONSUMABLES = 16,
	REARRANGE_HAND = 17,
	PASS = 18,
	START_RUN = 19,
}

Bot.ACTIONPARAMS = {}
Bot.ACTIONPARAMS[Bot.ACTIONS.SELECT_BLIND] = {
	num_args = 1,
	func = "skip_or_select_blind",
	isvalid = function(action)
		if G.STATE == G.STATES.BLIND_SELECT then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.SKIP_BLIND] = {
	num_args = 1,
	func = "skip_or_select_blind",
	isvalid = function(action)
		if G.STATE == G.STATES.BLIND_SELECT then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.PLAY_HAND] = {
	num_args = 2,
	func = "select_cards_from_hand",
	isvalid = function(action)
		if
			G
			and G.GAME
			and G.GAME.current_round
			and G.hand
			and G.hand.cards
			and G.GAME.current_round.hands_left > 0
			and #action == 2
			and Utils.isTableInRange(action[2], 1, #G.hand.cards)
			and Utils.isTableUnique(action[2])
		then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.DISCARD_HAND] = {
	num_args = 2,
	func = "select_cards_from_hand",
	isvalid = function(action)
		if
			G
			and G.GAME
			and G.GAME.current_round
			and G.hand
			and G.hand.cards
			and G.GAME.current_round.discards_left > 0
			and #action == 2
			and Utils.isTableInRange(action[2], 1, #G.hand.cards)
			and Utils.isTableUnique(action[2])
		then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.END_SHOP] = {
	num_args = 1,
	func = "select_shop_action",
	isvalid = function(action)
		if G and G.STATE == G.STATES.SHOP then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.REROLL_SHOP] = {
	num_args = 1,
	func = "select_shop_action",
	isvalid = function(action)
		if
			G
			and G.STATE == G.STATES.SHOP
			and (G.GAME.dollars - G.GAME.bankrupt_at - G.GAME.current_round.reroll_cost >= 0)
		then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.BUY_CARD] = {
	num_args = 2,
	func = "select_shop_action",
	isvalid = function(action)
		if
			G
			and G.STATE == G.STATES.SHOP
			and #action == 2
			and #action[2] == 1
			and G.shop_jokers
			and G.shop_jokers.cards
			and #G.shop_jokers.cards >= action[2][1]
			and (G.GAME.dollars - G.GAME.bankrupt_at - G.shop_jokers.cards[action[2][1]].cost >= 0)
		then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.BUY_VOUCHER] = {
	num_args = 2,
	func = "select_shop_action",
	isvalid = function(action)
		if
			G
			and G.STATE == G.STATES.SHOP
			and #action == 2
			and #action[2] == 1
			and G.shop_vouchers
			and G.shop_vouchers.cards
			and #G.shop_vouchers.cards >= action[2][1]
			and (G.GAME.dollars - G.GAME.bankrupt_at - G.shop_vouchers.cards[action[2][1]].cost >= 0)
		then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.BUY_BOOSTER] = {
	num_args = 2,
	func = "select_shop_action",
	isvalid = function(action)
		if
			G
			and G.STATE == G.STATES.SHOP
			and #action == 2
			and #action[2] == 1
			and G.shop_booster
			and G.shop_booster.cards
			and #G.shop_booster.cards >= action[2][1]
			and (G.GAME.dollars - G.GAME.bankrupt_at - G.shop_booster.cards[action[2][1]].cost >= 0)
		then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.SELECT_BOOSTER_CARD] = {
	num_args = 3,
	func = "select_booster_action",
	isvalid = function(action)
		if
			G
			and G.hand
			and G.pack_cards
			and G.hand.cards
			and G.pack_cards.cards
			and (G.STATE == G.STATES.TAROT_PACK or G.STATE == G.STATES.PLANET_PACK or G.STATE == G.STATES.SPECTRAL_PACK or G.STATE == G.STATES.STANDARD_PACK or G.STATE == G.STATES.BUFFOON_PACK)
			and Utils.isTableInRange(action[2], 1, #G.hand.cards)
			and Utils.isTableUnique(action[2])
			and Utils.isTableInRange(action[3], 1, #G.pack_cards.cards)
			and Utils.isTableUnique(action[3])
			and Middleware.BUTTONS.SKIP_PACK ~= nil
			and Middleware.BUTTONS.SKIP_PACK.config.button == "skip_booster"
		then
			if
				G.pack_cards.cards[action[2][1]].ability.consumeable
				and G.pack_cards.cards[action[2][1]].ability.consumeable.max_highlighted ~= nil
				and #action[3] > 0
				and #action[3] <= G.pack_cards.cards[action[2][1]].ability.consumeable.max_highlighted
			then
				return true
			else
				return false
			end
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.SKIP_BOOSTER_PACK] = {
	num_args = 1,
	func = "select_booster_action",
	isvalid = function(action)
		if
			G.pack_cards
			and G.pack_cards.cards
			and G.pack_cards.cards[1]
			and (G.STATE == G.STATES.PLANET_PACK or G.STATE == G.STATES.STANDARD_PACK or G.STATE == G.STATES.BUFFOON_PACK or (G.hand and G.hand.cards[1]))
			and Middleware.BUTTONS.SKIP_PACK ~= nil
			and Middleware.BUTTONS.SKIP_PACK.config.button == "skip_booster"
		then
			return true
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.SELL_JOKER] = {
	num_args = 2,
	func = "sell_jokers",
	isvalid = function(action)
		if G and G.jokers and G.jokers.cards then
			if not action[2] then
				return true
			end

			if
				Utils.isTableInRange(action[2], 1, #G.jokers.cards)
				and not G.jokers.cards[action[2][1]].ability.eternal
			then
				return true
			end
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.USE_CONSUMABLE] = {
	num_args = 2,
	func = "use_or_sell_consumables",
	isvalid = function(action)
		-- TODO implement this
		return true
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.SELL_CONSUMABLE] = {
	num_args = 2,
	func = "use_or_sell_consumables",
	isvalid = function(action)
		-- TODO implement this
		return true
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.REARRANGE_JOKERS] = {
	num_args = 2,
	func = "rearrange_jokers",
	isvalid = function(action)
		if G and G.jokers and G.jokers.cards then
			if not action[2] then
				return true
			end

			if
				Utils.isTableUnique(action[2])
				and Utils.isTableInRange(action[2], 1, #G.jokers.cards)
				and #action[2] == #G.jokers.cards
			then
				return true
			end
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.REARRANGE_CONSUMABLES] = {
	num_args = 2,
	func = "rearrange_consumables",
	isvalid = function(action)
		if G and G.consumeables and G.consumeables.cards then
			if not action[2] then
				return true
			end

			if
				Utils.isTableUnique(action[2])
				and Utils.isTableInRange(action[2], 1, #G.consumeables.cards)
				and #action[2] == #G.consumeables.cards
			then
				return true
			end
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.REARRANGE_HAND] = {
	num_args = 2,
	func = "rearrange_hand",
	isvalid = function(action)
		if G and G.hand and G.hand.cards then
			if not action[2] then
				return true
			end

			if
				Utils.isTableUnique(action[2])
				and Utils.isTableInRange(action[2], 1, #G.hand.cards)
				and #action[2] == #G.hand.cards
			then
				return true
			end
		end
		return false
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.PASS] = {
	num_args = 1,
	func = "",
	isvalid = function(action)
		return true
	end,
}
Bot.ACTIONPARAMS[Bot.ACTIONS.START_RUN] = {
	num_args = 5,
	func = "start_run",
	isvalid = function(action)
		if G and G.STATE == G.STATES.MENU then
			return true
		end
		return false
	end,
}

-- CHANGE ME
Bot.SETTINGS = {
	stake = 1,
	deck = "Plasma Deck",

	-- Keep these nil for random seed
	seed = "1OGB5WO",
	challenge = "",

	-- Time between actions the bot takes (pushing buttons, clicking cards, etc.)
	-- Minimum is 1 frame per action
	action_delay = 0,

	-- Replay actions from file?
	replay = false,

	-- Receive commands from the API?
	api = true,
}

--- Skips or selects the current blind
---@param blind string
--      One of 'Small', 'Big', 'Boss'
---@return number Return
--      Bot.ACTIONS.SELECT_BLIND or Bot.ACTIONS.SKIP_BLIND
function Bot.skip_or_select_blind(blind)
	if blind == "Small" or blind == "Big" then
		return Bot.ACTIONS.SKIP_BLIND
	end

	return Bot.ACTIONS.SELECT_BLIND
end

--- Selects cards from the current hand and plays or discards them
---@return integer
--      Bot.ACTIONS.PLAY_HAND or Bot.ACTIONS.DISCARD_HAND
---@return table
--      { G.hand.cards[1], G.hand.cards[2], G.hand.cards[3] }

local num_hand = 0
function Bot.select_cards_from_hand()
	num_hand = num_hand + 1

	-- Ante 1 Boss
	if num_hand == 1 then
		-- Get flush
		return Bot.ACTIONS.DISCARD_HAND, { 2, 3, 6, 7 }
	elseif num_hand == 2 then
		-- Play Flush
		return Bot.ACTIONS.PLAY_HAND, { 1, 3, 4, 5, 8 }
	end

	-- Play the first card for the rest of the game
	return Bot.ACTIONS.PLAY_HAND, { 1 }
end

---
---@param choices table
-- {
--      Bot.ACTIONS.BUY_BOOSTER = { cards },
--      Bot.ACTIONS.BUY_VOUCHER = { cards },
--      Bot.ACTIONS.BUY_CARD = { cards },
--      Bot.ACTIONS.REROLL_SHOP = true/false,
--      Bot.ACTIONS.END_SHOP = true
-- }
---@return integer
--      One of the above Bot.ACTIONS
---@return card
--      The card you would like to buy
-- ex. return Bot.ACTIONS.BUY_CARD, choices[Bot.ACTIONS.BUY_CARD][1]

local num_shop = 0
function Bot.select_shop_action(choices)
	num_shop = num_shop + 1

	-- Buy the Bull
	if num_shop == 1 and choices[Bot.ACTIONS.BUY_CARD] then
		return Bot.ACTIONS.BUY_CARD, { 2 }
	end

	-- Buy Luchador
	if num_shop == 5 and choices[Bot.ACTIONS.BUY_CARD] then
		return Bot.ACTIONS.BUY_CARD, { 2 }
	end

	return Bot.ACTIONS.END_SHOP
end

-- Returns one of the following ACTIONS, card to pick, and deck cards to pick if applicable
--      SELECT_BOOSTER_CARD
--      SKIP_BOOSTER_PACK

--- Selects actions when opening a booster pack
---@param pack_cards table
--      The list of cards in the booster being opened
---@param hand_cards table
--      The list of cards in your hand when opening a Tarot or Spectral pack
---@return integer
--      Bot.ACTIONS.SKIP_BOOSTER_PACK or Bot.ACTIONS.SELECT_BOOSTER_CARD
---@return card
--      The booster card to pick ex. 1
---@return table
--      The list of hand cards use the booster card on,
--      up to the max of your pack_choice.ability.consumeable.max_highlighted
--      ex. { 1, 2 }
function Bot.select_booster_action(pack_cards, hand_cards)
	return Bot.ACTIONS.SKIP_BOOSTER_PACK
end

function Bot.sell_jokers()
	if #G.jokers.cards > 1 then
		return Bot.ACTIONS.SELL_JOKER, { 2 }
	end
end

-- Return the action and indices of how the jokers should be rearranged
-- ex. return Bot.ACTIONS.REARRANGE_JOKERS, { 2, 1, 3  }
function Bot.rearrange_jokers()
	--return Bot.ACTIONS.REARRANGE_JOKERS, { 2, 1 }
end

function Bot.use_or_sell_consumables() end

function Bot.rearrange_consumables() end

-- Return the full new order of the hand
function Bot.rearrange_hand()
	--return Bot.ACTIONS.REARRANGE_HAND, { 2, 1, 3, 4, 5, 6, 7, 8 }
end

function Bot.start_run()
	return Bot.ACTIONS.START_RUN,
		{ Bot.SETTINGS.stake },
		{ Bot.SETTINGS.deck },
		{ Bot.SETTINGS.seed },
		{ Bot.SETTINGS.challenge }
end

return Bot
