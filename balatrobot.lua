---@meta balatrobot
---Main entry point for the BalatroBot mod

---@class BalatrobotConfig
---@field port string Port for the bot to listen on
---@field dt number Tells the game that every update is dt seconds long.
---@field max_fps integer Maximum frames per second
---@field vsync_enabled boolean Whether vertical sync is enabled

---Global configuration for the BalatroBot mod
---@type BalatrobotConfig
BALATRO_BOT_CONFIG = {
  port = "12346",
  dt = 2.0 / 60.0,
  max_fps = 60,
  vsync_enabled = false,

  --  -- Default values for the original game
  -- port = "12346",
  -- dt = 1.0 / 60.0,
  -- vsync_enabled = true,
  --  max_fps = nil,
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
    exec = function(args, _, _)
      debugplus.logger.log('{"name": "' .. args[1] .. '", "G": ' .. utils.table_to_json(G, 2) .. "}")
    end,
  })
end

-- Initialize API
API.init()

sendInfoMessage("BalatroBot loaded - version " .. SMODS.current_mod.version, "BALATROBOT")
