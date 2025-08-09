---Utility functions for game state extraction and data processing
utils = {}
local json = require("json")
local socket = require("socket")

-- ==========================================================================
-- Game State Extraction
--
-- In the following code there are a lot of comments which document the
-- process of understanding the game state. There are many fields that
-- we are not interested for BalatroBot. I leave the comments here for
-- future reference.
--
-- The proper documnetation of the game state is available in the types.lua
-- file (src/lua/types.lua).
-- ==========================================================================

---Extracts the current game state including game info, hand, and jokers
---@return G game_state The complete game state
function utils.get_game_state()
  local game = nil
  if G.GAME then
    local tags = {}
    if G.GAME.tags then
      for i, tag in pairs(G.GAME.tags) do
        tags[i] = {
          -- There are a couples of fieds regarding UI. we are not intersted in that.
          -- HUD_tag = table/list, -- ??
          -- ID = int -- id used in the UI or tag id?
          -- ability = table/list, -- ??
          -- config = table/list, -- ??
          key = tag.key, -- id string of the tag (e.g. "tag_foil")
          name = tag.name, -- text string of the tag (e.g. "Foil Tag")
          -- pos = table/list, coords of the tags in the UI
          -- tag_sprite = table/list, sprite of the tag for the UI
          -- tally = int (default 0), -- ??
          -- triggered = bool (default false), -- false when the tag will be trigger in later stages.
          -- For exaple double money trigger instantly and it's not even add to the tags talbe,
          -- while other tags trigger in the next shop phase.
        }
      end
    end

    local last_blind = {
      boss = false,
      name = "",
    }
    if G.GAME.last_blind then
      last_blind = {
        boss = G.GAME.last_blind.boss, -- bool. True if the last blind was a boss
        name = G.GAME.last_blind.name, -- str (default "" before entering round 1)
        -- When entering round 1, the last blind is set to "Small Blind".
        -- So I think that the last blind refers  to the blind selected in the most recent BLIND_SELECT state.
      }
    end
    game = {
      -- STOP_USE = int (default 0), -- ??
      bankrupt_at = G.GAME.bankrupt_at,
      -- banned_keys = table/list, -- ??
      base_reroll_cost = G.GAME.base_reroll_cost,

      -- blind = {}, This is active during the playing phase and contains
      -- information about the UI of the blind object. It can be dragged around
      -- We are not interested in it.

      blind_on_deck = G.GAME.blind_on_deck, -- Small | ?? | ??
      bosses_used = {
        -- bl_<boss name> = int, 1 | 0 (default 0)
        -- ... x 28
        -- In a normal ante there should be only one boss used, so only one value is one
      },
      -- cards_played: table<string, number>, change during game phase

      chips = G.GAME.chips,
      -- chip_text =  str, the text of the current chips in the UI
      -- common_mod = int (default 1), -- prob that a common joker appear in the shop

      -- "consumeable_buffer": int, (default 0) -- number of cards in the consumeable buffer?
      -- consumeable_usage = { }, -- table/list to track the consumable usage through the run.
      -- "current_boss_streak": int, (default 0) -- in the simple round should be == to the ante?
      --

      current_round = {
        -- "ancient_card": { -- maybe some random card used by some joker/effect? idk
        --   "suit": "Spades" | "Hearts" | "Diamonds" | "Clubs",
        -- },
        -- any_hand_drawn = true, -- bool (default true) ??
        -- "cards_flipped": int, (Defualt 0)
        -- "castle_card": { -- ??
        --   "suit": "Spades" | "Hearts" | "Diamonds" | "Clubs",
        -- },

        -- This should contains interesting info during playing phase
        -- "current_hand": {
        --   "chip_text": str, Default "-"
        --   "chip_total": int, Default 0
        --   "chip_total_text: str , Default ""
        --   "chips": int, Default 0
        --   "hand_level": str Default ""
        --   "handname": str Default ""
        --   "handname_text": str Default ""
        --   "mult": int, Default 0
        --   "mult_text": str, Default "0"
        -- },

        discards_left = G.GAME.current_round.discards_left, -- Number of discards left for this round
        discards_used = G.GAME.current_round.discards_used, -- int (default 0) Number of discard used in this round

        --"dollars": int, (default 0) -- maybe dollars earned in this round?
        -- "dollars_to_be_earned": str, (default "") -- ??
        -- "free_rerolls": int, (default 0) -- Number  of free rerolls in the shop?
        hands_left = G.GAME.current_round.hands_left, -- Number of hands left for this round
        hands_played = G.GAME.current_round.hands_played, -- Number of hands played in this round

        -- Reroll information (used in shop state)
        reroll_cost = G.GAME.current_round.reroll_cost, -- Current cost for a shop reroll
        free_rerolls = G.GAME.current_round.free_rerolls, -- Free rerolls remaining this round
        -- "idol_card": { -- what's a idol card?? maybe some random used by some joker/effect? idk
        --   "rank": "Ace" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10" | "Jack" | "Queen" | "King",
        --   "suit": "Spades" | "Hearts" | "Diamonds" | "Clubs",
        -- },
        -- "jokers_purchased": int, (default 0) -- Number of jokers purchased in this round ?
        -- "mail_card": { -- what's a mail card?? maybe some random used by some joker/effect? idk
        --   "id": int -- id of the mail card
        --   "rank": str, --
        --  }
        -- "most_played_poker_hand": str, (Default "High Card")
        -- "reroll_cost": int, (default 5)
        -- "reroll_cost_increase": int, (default 0)
        -- "round_dollars": int, (default 0) ??
        -- "round_text": str, (default "Round ")
        -- "used_packs": table/list,
        voucher = { -- this is a list cuz some effect can give multiple vouchers per ante
          -- "1": "v_hone",
          -- "spawn": {
          --   "v_hone": "..."
          -- }
        },
      },

      -- "disabled_ranks" = table/list, -- there are some boss that disable certain ranks
      -- "disabled_suits" = table/list, -- there are some boss that disable certain suits

      discount_percent = G.GAME.discount_percent, -- int (default 0) this lower the price in the shop. A voucher must be redeemed
      dollars = G.GAME.dollars, -- int , current dollars in the run

      -- "ecto_minus": int,
      -- "edition_rate": int, (default 1) -- change the prob. to find a card which is not a base?
      -- "hand_usage": table/list, (default {}) -- maybe track the hand played so far in the run?

      -- table/list. Maybe this track the various hand levels?
      -- "hands": {
      --   "Five of a Kind": {...},
      --   "Flush": {
      --     "_saved_d_u": true, This is a private field so we are not interested in it
      --     "chips": 35, current chips reward
      --     "example": {
      --       "1": "...",
      --       "2": "...",
      --       "3": "...",
      --       "4": "...",
      --       "5": "..."
      --     },
      --     "l_chips": 15, boundary for chips?
      --     "l_mult": 2, boundary for mult?
      --     "level": 1, level of the hand
      --     "mult": 4, curent mult reward
      --     "order": 7, order for how good the hand is Five of a Kind is 1, High Card is 12
      --     "played": 0, how many time the hand has been played in this run
      --     "played_this_round": 0, how many time the hand has been played in this round
      --     "s_chips": 35, boundary for chips?
      --     "s_mult": 4, boundary for mult?
      --     "visible": true, is this hand visible in the Run Info interface
      --   },
      --   "Flush Five": {...},
      --   "Flush House": {...},
      --   "Four of a Kind": {...},
      --   "Full House": {...},
      --   "High Card": {...},
      --   "Pair": {...},
      --   "Straight": {...},
      --   "Straight Flush": {...},
      --   "Three of a Kind": {...},
      --   "Two Pair": {...},
      -- },
      hands_played = G.GAME.hands_played, -- (default 0) hand played in this run
      inflation = G.GAME.inflation, -- (default 0) maybe there are some stakes that increase the prices in the shop ?
      interest_amount = G.GAME.interest_amount, -- (default 1) how much each $ is worth at the eval round stage
      interest_cap = G.GAME.interest_cap, -- (default 25) cap for interest, e.g. 25 dollar means that every each 5 dollar you get one $

      -- joker_buffer = int, -- (default 0) ??
      -- joker_rate = int, -- (default 20) prob that a joker appear in the shop
      -- joker_usage = G.GAME.joker_usage, -- list/table maybe a list of jokers used in the run?
      --
      last_blind = last_blind,
      -- legendary_mod = G.GAME.legendary_mod, -- (default 1) maybe the probality/modifier to find a legendary joker in the shop?

      max_jokers = G.GAME.max_jokers, --(default 0) the number of held jokers?

      -- modifiers = list/table, -- ??
      -- orbital_choices = { -- what's an orbital choice?? This is a list (table with int keys). related to pseudorandom
      --   -- 1: {
      --   --   "Big": "Two Pair",
      --   --   "Boss": "Three of a Kind",
      --   --   "Small": "Full House"
      --   -- }
      -- },
      -- pack_size = G.GAME.pack_size (int default 2), -- number of pack slots ?
      -- perishable_rounds = int (default 5), -- ??
      -- perscribed_bosses = list/table, -- ??

      planet_rate = G.GAME.planet_rate, -- (int default 4) -- prob that a planet card appers in the shop
      playing_card_rate = G.GAME.playing_card_rate, -- (int default 0) -- prob that a playing card appers in the shop. at the start of the run playable cards are not purchasable so it's 0, then by reedming a voucher, you can buy them in the shop.
      -- pool_flags = list/table, -- ??

      previous_round = {
        -- I think that this table will contain the previous round info
        -- "dollars": int, (default 4, this is the dollars amount when starting red deck white stake)
      },
      probabilities = {
        -- Maybe this table track various probabilities for various events (e.g. prob that planet cards appers in the
        -- shop)
        -- "normal": int, (default 1)
      },

      -- This table contains the seed used to start a run. The seed is used in the generation of pseudorandom number
      -- which themselves are used to add randomness to a run. (e.g. which is the first tag? well the float that is
      -- probably used to extract the tag for the first round is in Tag1.)
      pseudorandom = {
        -- float e.g. 0.1987752917732 (all the floats are in the range [0, 1) with 13 digit after the dot.
        -- Tag1 = float,
        -- Voucher1 = float,
        -- Voucher1_resample2 = float,
        -- Voucher1_resample3 = float,
        -- anc1 = float,
        -- boss = float,
        -- cas1 = float,
        -- hashed_seed = float,
        -- idol1 = float,
        -- mail1 = float,
        -- orbital = float,
        -- seed = string, This is the seed used to start a run
        -- shuffle = float,
      },
      -- rare_mod = G.GAME.rare_mod, (int default 1) -- maybe the probality/modifier to find a rare joker in the shop?
      -- rental_rate = int (default 3), -- maybe the probality/modifier to find a rental card in the shop?
      round = G.GAME.round, -- number of the current round. 0 before starting the first rounthe first round
      round_bonus = { -- What's a "round_bonus"? Some bonus given at the end of the round? maybe use in the eval round phase
        -- "discards": int, (default 0) ??
        -- "next_hands": int, (default 0) ??
      },

      -- round_resets = table/list, -- const used to reset the round? but should be not relevant for our use case
      round_scores = {
        -- contains values used in the round eval phase?
        -- "cards_discarded": {
        --   "amt": int, (default 0) amount of cards discarded
        --   "label": "Cards Discarded" label for the amount of cards discarded. maybe used in the interface
        --   },
        -- "cards_played": {...}, amount of cards played in this round
        -- "cards_purchased": {...}, amount of cards purchased in this round
        -- "furthest_ante": {...}, furthest ante in this run
        -- "furthest_round": {...}, furthest round in this round or run?
        -- "hand": {...}, best hand in this round
        -- "new_collection": {...}, new cards discovered in this round
        -- "poker_hand": {...}, most played poker hand in this round
        -- "times_rerolled": {...}, number of times rerolled in this round
      },
      seeded = G.GAME.seeded, -- bool if the run use a seed or not
      selected_back = {
        -- The back should be the deck: Red Deck, Black Deck, etc.
        -- This table contains functions and info about deck selection
        -- effect = {} -- contains function e.g. "set"
        -- loc_name = str, -- ?? (default "Red Deck")
        name = G.GAME.selected_back.name, -- name of the deck
        -- pos = {x = int (default 0), y = int (default 0)}, -- ??
      },
      -- seleted_back_key = table -- ??
      shop = {
        -- contains info about the shop
        -- joker_max = int (default 2), -- max number that can appear in the shop or the number of shop slots?
      },
      skips = G.GAME.skips, -- number of skips in this run
      smods_version = G.GAME.smods_version, -- version of smods loaded
      -- sort = str, (default "desc") card sort order. descending (desc) or suit, I guess?
      -- spectral_rate = int (default 0), -- prob that a spectral card appear in the shop
      stake = G.GAME.stake, --int (default 1), -- the stake for the run (1 for White Stake, 2 for Red Stake ...)
      -- starting_deck_size = int (default 52), -- the starting deck size for the run.
      starting_params = {
        -- The starting parmeters are maybe not relevant, we are intersted in
        -- the actual values of the parameters
        --
        -- ante_scaling = G.GAME.starting_params.ante_scaling, -- (default 1) increase the ante by one after boss defeated
        -- boosters_in_shop = G.GAME.starting_params.boosters_in_shop, -- (default 2) Number of booster slots
        -- consumable_slots = G.GAME.starting_params.consumable_slots, -- (default 2) Number of consumable slots
        -- discard_limit = G.GAME.starting_params.discard_limit, -- (default 5) Number of cards to discard
        -- ...
      },

      -- tag_tally = -- int (default 0), -- what's a tally?
      tags = tags,
      tarot_rate = G.GAME.tarot_rate, -- int (default 4), -- prob that a tarot card appear in the shop
      uncommon_mod = G.GAME.uncommon_mod, -- int (default 1), -- prob that an uncommon joker appear in the shop
      unused_discards = G.GAME.unused_discards, -- int (default 0), -- number of discards left at the of a round. This is used some time to in the eval round phase
      -- used_jokers = { -- table/list to track the joker usage through the run ?
      --   c_base = bool
      -- }
      used_vouchers = G.GAME.used_vouchers, -- table/list to track the voucher usage through the run. Should be the ones that can be see in "Run Info"
      voucher_text = G.GAME.voucher_text, -- str (default ""), -- the text of the voucher for the current run
      win_ante = G.GAME.win_ante, -- int (default 8), -- the ante for the win condition
      won = G.GAME.won, -- bool (default false), -- true if the run is won (e.g. current ante > win_ante)
    }
  end

  local consumables = nil
  if G.consumeables then
    local cards = {}
    if G.consumeables.cards then
      for i, card in pairs(G.consumeables.cards) do
        cards[i] = {
          ability = {
            set = card.ability.set,
          },
          label = card.label,
          cost = card.cost,
          sort_id = card.sort_id, -- Unique identifier for this card instance (used for rearranging)
          config = {
            center_key = card.config.center_key,
          },
          debuff = card.debuff,
          facing = card.facing,
          highlighted = card.highlighted,
        }
      end
    end
    consumables = {
      cards = cards,
      config = {
        card_count = G.consumeables.config.card_count,
        card_limit = G.consumeables.config.card_limit,
      },
    }
  end

  local hand = nil
  if G.hand then
    local cards = {}
    for i, card in pairs(G.hand.cards) do
      cards[i] = {
        ability = {
          set = card.ability.set, -- str. The set of the card: Joker, Planet, Voucher, Booster, or Consumable
        },
        -- ability = table of card abilities effect, mult, extra_value
        label = card.label, -- str (default "Base Card") | ... | ... | ?
        -- playing_card = card.config.card.playing_card, -- int. The card index in the deck for the current round ?
        -- sell_cost = card.sell_cost, -- int (default 1). The dollars you get if you sell this card ?
        sort_id = card.sort_id, -- int. Unique identifier for this card instance
        base = {
          -- These should be the valude for the original base card
          -- without any modifications
          id = card.base.id, -- ??
          name = card.base.name,
          nominal = card.base.nominal,
          original_value = card.base.original_value,
          suit = card.base.suit,
          times_played = card.base.times_played,
          value = card.base.value,
        },
        config = {
          card_key = card.config.card_key,
          card = {
            name = card.config.card.name,
            suit = card.config.card.suit,
            value = card.config.card.value,
          },
        },
        debuff = card.debuff,
        -- debuffed_by_blind = bool (default false). True if the card is debuffed by the blind
        facing = card.facing, -- str (default "front") | ... | ... | ?
        highlighted = card.highlighted, -- bool (default false). True if the card is highlighted
      }
    end

    hand = {
      cards = cards,
      config = {
        card_count = G.hand.config.card_count, -- (int) number of cards in the hand
        card_limit = G.hand.config.card_limit, -- (int) max number of cards in the hand
        highlighted_limit = G.hand.config.highlighted_limit, -- (int) max number of highlighted cards in the hand
        -- lr_padding ?? flaot
        -- sort = G.hand.config.sort, -- (str) sort order of the hand. "desc" | ... | ? not really... idk
        -- temp_limit ?? (int)
        -- type ?? (Default "hand", str)
      },
      -- container = table for UI elements. we are not interested in it
      -- created_on_pause = bool ??
      -- highlighted = list of highlighted cards. This is a list of card.
      -- hover_offset = table/list, coords of the hand in the UI. we are not interested in it.
      -- last_aligned = int, ??
      -- last_moved = int, ??
      --
      -- There a a lot of other fields that we are not interested in ...
    }
  end

  local jokers = nil
  if G.jokers then
    local cards = {}
    if G.jokers.cards then
      for i, card in pairs(G.jokers.cards) do
        cards[i] = {
          ability = {
            set = card.ability.set, -- str. The set of the card: Joker, Planet, Voucher, Booster, or Consumable
          },
          label = card.label,
          cost = card.cost,
          sort_id = card.sort_id, -- Unique identifier for this card instance (used for rearranging)
          config = {
            center_key = card.config.center_key,
          },
          debuff = card.debuff,
          facing = card.facing,
          highlighted = card.highlighted,
        }
      end
    end
    jokers = {
      cards = cards,
      config = {
        card_count = G.jokers.config.card_count,
        card_limit = G.jokers.config.card_limit,
      },
    }
  end

  local shop_jokers = nil
  if G.shop_jokers then
    local config = {}
    if G.shop_jokers.config then
      config = {
        card_count = G.shop_jokers.config.card_count, -- int. how many cards are in the the shop
        card_limit = G.shop_jokers.config.card_limit, -- int. how many cards can be in the shop
      }
    end
    local cards = {}
    if G.shop_jokers.cards then
      for i, card in pairs(G.shop_jokers.cards) do
        cards[i] = {
          ability = {
            set = card.ability.set, -- str. The set of the card: Joker, Planet, Voucher, Booster, or Consumable
          },
          config = {
            center_key = card.config.center_key, -- id of the card
          },
          debuff = card.debuff, -- bool. True if the card is a debuff
          cost = card.cost, -- int. The cost of the card
          label = card.label, -- str. The label of the card
          facing = card.facing, -- str. The facing of the card: front | back
          highlighted = card.highlighted, -- bool. True if the card is highlighted
          sell_cost = card.sell_cost, -- int. The sell cost of the card
        }
      end
    end
    shop_jokers = {
      config = config,
      cards = cards,
    }
  end

  local shop_vouchers = nil
  if G.shop_vouchers then
    local config = {}
    if G.shop_vouchers.config then
      config = {
        card_count = G.shop_vouchers.config.card_count,
        card_limit = G.shop_vouchers.config.card_limit,
      }
    end
    local cards = {}
    if G.shop_vouchers.cards then
      for i, card in pairs(G.shop_vouchers.cards) do
        cards[i] = {
          ability = {
            set = card.ability.set,
          },
          config = {
            center_key = card.config.center_key,
          },
          debuff = card.debuff,
          cost = card.cost,
          label = card.label,
          facing = card.facing,
          highlighted = card.highlighted,
          sell_cost = card.sell_cost,
        }
      end
    end
    shop_vouchers = {
      config = config,
      cards = cards,
    }
  end

  local shop_booster = nil
  if G.shop_booster then
    -- NOTE: In the game these are called "packs"
    -- but the variable name is "cards" in the API.
    local config = {}
    if G.shop_booster.config then
      config = {
        card_count = G.shop_booster.config.card_count,
        card_limit = G.shop_booster.config.card_limit,
      }
    end
    local cards = {}
    if G.shop_booster.cards then
      for i, card in pairs(G.shop_booster.cards) do
        cards[i] = {
          ability = {
            set = card.ability.set,
          },
          config = {
            center_key = card.config.center_key,
          },
          cost = card.cost,
          label = card.label,
          highlighted = card.highlighted,
          sell_cost = card.sell_cost,
        }
      end
    end
    shop_booster = {
      config = config,
      cards = cards,
    }
  end

  return {
    state = G.STATE,
    game = game,
    hand = hand,
    jokers = jokers,
    shop_jokers = shop_jokers, -- NOTE: This contains all cards in the shop, not only jokers.
    shop_vouchers = shop_vouchers,
    shop_booster = shop_booster,
    consumables = consumables,
  }
end

-- ==========================================================================
-- Utility Functions
-- ==========================================================================

function utils.sets_equal(list1, list2)
  if #list1 ~= #list2 then
    return false
  end

  local set = {}
  for _, v in ipairs(list1) do
    set[v] = true
  end

  for _, v in ipairs(list2) do
    if not set[v] then
      return false
    end
  end

  return true
end

-- ==========================================================================
-- Debugging Utilities
-- ==========================================================================

---Converts a Lua table to JSON string with depth limiting to prevent infinite recursion
---@param obj any The object to convert to JSON
---@param depth? number Maximum depth to traverse (default: 3)
---@return string JSON string representation of the object
function utils.table_to_json(obj, depth)
  depth = depth or 3

  -- Fields to skip during serialization to avoid circular references and large data
  local skip_fields = {
    children = true,
    parent = true,
    velocity = true,
    area = true,
    alignment = true,
    container = true,
    h_popup = true,
    role = true,
    colour = true,
    back_overlay = true,
    center = true,
  }

  local function sanitize_for_json(value, current_depth)
    if current_depth <= 0 then
      return "..."
    end

    local value_type = type(value)

    if value_type == "nil" then
      return nil
    elseif value_type == "string" or value_type == "number" or value_type == "boolean" then
      return value
    elseif value_type == "function" then
      return "function"
    elseif value_type == "userdata" then
      return "userdata"
    elseif value_type == "table" then
      local sanitized = {}
      for k, v in pairs(value) do
        local key = type(k) == "string" and k or tostring(k)
        -- Skip keys that start with capital letters (UI-related)
        -- Skip predefined fields to avoid circular references and large data
        if not (type(key) == "string" and string.sub(key, 1, 1):match("[A-Z]")) and not skip_fields[key] then
          sanitized[key] = sanitize_for_json(v, current_depth - 1)
        end
      end
      return sanitized
    else
      return tostring(value)
    end
  end

  local sanitized = sanitize_for_json(obj, depth)
  return json.encode(sanitized)
end

-- Load DebugPlus integration
-- Attempt to load the optional DebugPlus mod (https://github.com/WilsontheWolf/DebugPlus/tree/master).
-- DebugPlus is a Balatro mod that provides additional debugging utilities for mod development,
-- such as custom debug commands and structured logging. It is not required for core functionality
-- and is primarily intended for development and debugging purposes. If the module is unavailable
-- or incompatible, the program will continue to function without it.
local success, dpAPI = pcall(require, "debugplus-api")

if success and dpAPI.isVersionCompatible(1) then
  local debugplus = dpAPI.registerID("balatrobot")
  debugplus.addCommand({
    name = "env",
    shortDesc = "Get game state",
    desc = "Get the current game state, useful for debugging",
    exec = function(args, _, _)
      debugplus.logger.log('{"name": "' .. args[1] .. '", "G": ' .. utils.table_to_json(G.GAME, 2) .. "}")
    end,
  })
end

-- ==========================================================================
-- Completion Conditions
-- ==========================================================================

-- The threshold for determining when game state transitions are complete.
-- This value represents the maximum number of events allowed in the game's event queue
-- to consider the game idle and waiting for user action. When the queue has fewer than
-- 3 events, the game is considered stable enough to process API responses. This is a
-- heuristic based on empirical testing to ensure smooth gameplay without delays.
local EVENT_QUEUE_THRESHOLD = 3

-- Timestamp storage for delayed conditions
local condition_timestamps = {}

---Completion conditions for different game actions to determine when action execution is complete
---These are shared between API and LOG systems to ensure consistent timing
---@type table<string, table>
utils.COMPLETION_CONDITIONS = {
  get_game_state = {
    [""] = function()
      return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
    end,
  },

  go_to_menu = {
    [""] = function()
      return G.STATE == G.STATES.MENU and G.MAIN_MENU_UI
    end,
  },

  start_run = {
    [""] = function()
      return G.STATE == G.STATES.BLIND_SELECT
        and G.GAME.blind_on_deck
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
    end,
  },

  skip_or_select_blind = {
    ["select"] = function()
      if G.GAME and G.GAME.facing_blind and G.STATE == G.STATES.SELECTING_HAND then
        return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
      end
    end,
    ["skip"] = function()
      if G.prev_small_state == "Skipped" or G.prev_large_state == "Skipped" or G.prev_boss_state == "Skipped" then
        return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
      end
      return false
    end,
  },

  play_hand_or_discard = {
    -- TODO: refine condition for be specific about the action
    ["play_hand"] = function()
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
    ["discard"] = function()
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
  },

  rearrange_hand = {
    [""] = function()
      return G.STATE == G.STATES.SELECTING_HAND
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD
        and G.STATE_COMPLETE
    end,
  },

  rearrange_jokers = {
    [""] = function()
      return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE
    end,
  },

  rearrange_consumables = {
    [""] = function()
      return #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE
    end,
  },

  cash_out = {
    [""] = function()
      return G.STATE == G.STATES.SHOP and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE
    end,
  },

  shop = {
    buy_card = function()
      local base_condition = G.STATE == G.STATES.SHOP
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduve the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.shop_buy_card = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.shop_buy_card then
        condition_timestamps.shop_buy_card = socket.gettime()
      end

      -- Check if 0.1 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.shop_buy_card
      return elapsed > 0.1
    end,
    next_round = function()
      return G.STATE == G.STATES.BLIND_SELECT and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD and G.STATE_COMPLETE
    end,
    reroll = function()
      local base_condition = G.STATE == G.STATES.SHOP
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduve the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.shop_reroll = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.shop_reroll then
        condition_timestamps.shop_reroll = socket.gettime()
      end

      -- Check if 0.3 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.shop_reroll
      return elapsed > 0.30
    end,
    redeem_voucher = function()
      local base_condition = G.STATE == G.STATES.SHOP
        and #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduve the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.shop_redeem_voucher = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.shop_redeem_voucher then
        condition_timestamps.shop_redeem_voucher = socket.gettime()
      end

      -- Check if 0.3 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.shop_redeem_voucher
      return elapsed > 0.10
    end,
  },
  sell_joker = {
    [""] = function()
      local base_condition = #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduce the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.sell_joker = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.sell_joker then
        condition_timestamps.sell_joker = socket.gettime()
      end

      -- Check if 0.2 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.sell_joker
      return elapsed > 0.30
    end,
  },
  sell_consumable = {
    [""] = function()
      local base_condition = #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduce the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.sell_consumable = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.sell_consumable then
        condition_timestamps.sell_consumable = socket.gettime()
      end

      -- Check if 0.3 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.sell_consumable
      return elapsed > 0.30
    end,
  },
  use_consumable = {
    [""] = function()
      local base_condition = #G.E_MANAGER.queues.base < EVENT_QUEUE_THRESHOLD - 1 -- need to reduce the threshold
        and G.STATE_COMPLETE

      if not base_condition then
        -- Reset timestamp if base condition is not met
        condition_timestamps.use_consumable = nil
        return false
      end

      -- Base condition is met, start timing
      if not condition_timestamps.use_consumable then
        condition_timestamps.use_consumable = socket.gettime()
      end

      -- Check if 0.2 seconds have passed
      local elapsed = socket.gettime() - condition_timestamps.use_consumable
      return elapsed > 0.20
    end,
  },
}

return utils
