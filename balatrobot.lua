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
	port = "12345",
	dt = 1.0 / 60.0,
	uncap_fps = false,
	instant_move = false,
	disable_vsync = false,
	disable_card_eval_status_text = true,
	frame_ratio = 1,
}

-- External libraries
---@type List
assert(SMODS.load_file("lib/list.lua"))()
---@type Hook
assert(SMODS.load_file("lib/hook.lua"))()
---@type table
assert(SMODS.load_file("lib/bitser.lua"))()
---@type table
assert(SMODS.load_file("lib/sock.lua"))()

-- Mod specific files
---@type Utils
assert(SMODS.load_file("src/utils.lua"))()
---@type Bot
assert(SMODS.load_file("src/bot.lua"))()
---@type Middleware
assert(SMODS.load_file("src/middleware.lua"))()
---@type Botlogger
assert(SMODS.load_file("src/botlogger.lua"))()
---@type BalatrobotAPI
assert(SMODS.load_file("src/api.lua"))()

-- Init middleware
Middleware.hookbalatro()
sendDebugMessage("Middleware loaded", "BALATROBOT")

-- Init logger
Botlogger.path = "balatrobot.log"
Botlogger.init()
sendDebugMessage("Logger loaded", "BALATROBOT")

-- Init API
BalatrobotAPI.init()
sendDebugMessage("API loaded", "BALATROBOT")

sendInfoMessage("BalatroBot loaded - version " .. SMODS.current_mod.version, "BALATROBOT")