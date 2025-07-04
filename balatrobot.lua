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

assert(SMODS.load_file("src/lua/list.lua"))()
assert(SMODS.load_file("src/lua/hook.lua"))()
assert(SMODS.load_file("src/lua/utils.lua"))()
assert(SMODS.load_file("src/lua/bot.lua"))()
assert(SMODS.load_file("src/lua/middleware.lua"))()
assert(SMODS.load_file("src/lua/api.lua"))()

-- Init middleware
Middleware.hookbalatro()
sendDebugMessage("Middleware loaded", "BALATROBOT")

-- Init API (includes queue initialization)
BalatrobotAPI.init()
sendDebugMessage("API loaded", "BALATROBOT")

sendInfoMessage("BalatroBot loaded - version " .. SMODS.current_mod.version, "BALATROBOT")
