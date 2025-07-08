---@meta balatrobot
---Main entry point for the BalatroBot mod

---@class BalatrobotConfig
---@field enabled boolean Disables ALL mod functionality if false
---@field port string Port for the bot to listen on
---@field dt number Tells the game that every update is dt seconds long
---@field uncap_fps boolean Whether to uncap the frame rate
---@field instant_move boolean Whether to enable instant card movement
---@field disable_vsync boolean Whether to disable vertical sync
---@field disable_card_eval_status_text boolean Whether to disable card evaluation status text (e.g. +10 when scoring a queen)
---@field frame_ratio integer Draw every nth frame, set to 1 for normal rendering

---Global configuration for the BalatroBot mod
---@type BalatrobotConfig
BALATRO_BOT_CONFIG = {
	enabled = true,
	port = "12346",
	dt = 1.0 / 60.0,
	uncap_fps = false,
	instant_move = false,
	disable_vsync = false,
	disable_card_eval_status_text = true,
	frame_ratio = 1,
}

-- Load debug
local success, dpAPI = pcall(require, "debugplus-api")

-- Load minimal required files
assert(SMODS.load_file("src/lua/utils.lua"))()
assert(SMODS.load_file("src/lua/api.lua"))()

if success and dpAPI.isVersionCompatible(1) then
	local debugplus = dpAPI.registerID("balatrobot")
	debugplus.addCommand({
		name = "env",
		shortDesc = "Get game state",
		desc = "Get the current game state, useful for debugging",
		exec = function(args, rawArgs, dp)
			debugplus.logger.log('{"name": "' .. args[1] .. '", "G": ' .. utils.table_to_json(G, 2) .. "}")
		end,
	})
end

-- Initialize API
API.init()
sendDebugMessage("API loaded", "BALATROBOT")

sendInfoMessage("BalatroBot loaded - version " .. SMODS.current_mod.version, "BALATROBOT")
