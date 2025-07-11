---Global configuration for the BalatroBot mod
---@type BalatrobotConfig
BALATRO_BOT_CONFIG = {
  port = "12346",
  dt = 4.0 / 60.0, -- value >= 4.0 make mod instable
  max_fps = 60,
  vsync_enabled = false,

  --  -- Default values for the original game
  -- port = "12346",
  -- dt = 1.0 / 60.0,
  -- vsync_enabled = true,
  -- max_fps = nil,
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
      debugplus.logger.log('{"name": "' .. args[1] .. '", "G": ' .. utils.table_to_json(G.GAME, 2) .. "}")
    end,
  })
end

-- Initialize API
API.init()

sendInfoMessage("BalatroBot loaded - version " .. SMODS.current_mod.version, "BALATROBOT")
