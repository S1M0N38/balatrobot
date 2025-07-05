Bot = {}

-- ACTIONS
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

-- ACTION PARAMETERS
Bot.ACTIONPARAMS = {
	[Bot.ACTIONS.SELECT_BLIND] = {
		num_args = 1,
		func = "skip_or_select_blind",
		isvalid = function(action)
			if G.STATE == G.STATES.BLIND_SELECT then
				return true
			end
			return false
		end,
	},
	[Bot.ACTIONS.SKIP_BLIND] = {
		num_args = 1,
		func = "skip_or_select_blind",
		isvalid = function(action)
			if G.STATE == G.STATES.BLIND_SELECT then
				return true
			end
			return false
		end,
	},
	[Bot.ACTIONS.PLAY_HAND] = {
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
	},
	[Bot.ACTIONS.DISCARD_HAND] = {
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
	},
	[Bot.ACTIONS.END_SHOP] = {
		num_args = 1,
		func = "select_shop_action",
		isvalid = function(action)
			if G and G.STATE == G.STATES.SHOP then
				return true
			end
			return false
		end,
	},
	[Bot.ACTIONS.REROLL_SHOP] = {
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
	},
	[Bot.ACTIONS.BUY_CARD] = {
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
	},
	[Bot.ACTIONS.BUY_VOUCHER] = {
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
	},
	[Bot.ACTIONS.BUY_BOOSTER] = {
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
	},
	[Bot.ACTIONS.SELECT_BOOSTER_CARD] = {
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
	},
	[Bot.ACTIONS.SKIP_BOOSTER_PACK] = {
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
	},
	[Bot.ACTIONS.SELL_JOKER] = {
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
	},
	[Bot.ACTIONS.USE_CONSUMABLE] = {
		num_args = 2,
		func = "use_or_sell_consumables",
		isvalid = function(action)
			-- TODO implement this
			return true
		end,
	},
	[Bot.ACTIONS.SELL_CONSUMABLE] = {
		num_args = 2,
		func = "use_or_sell_consumables",
		isvalid = function(action)
			-- TODO implement this
			return true
		end,
	},
	[Bot.ACTIONS.REARRANGE_JOKERS] = {
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
	},
	[Bot.ACTIONS.REARRANGE_CONSUMABLES] = {
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
	},
	[Bot.ACTIONS.REARRANGE_HAND] = {
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
	},
	[Bot.ACTIONS.PASS] = {
		num_args = 1,
		func = "",
		isvalid = function(action)
			return true
		end,
	},
	[Bot.ACTIONS.START_RUN] = {
		num_args = 5,
		func = "start_run",
		isvalid = function(action)
			if G and G.STATE == G.STATES.MENU then
				return true
			end
			return false
		end,
	},
}

return Bot
