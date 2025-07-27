-- Load minimal required files
assert(SMODS.load_file("src/lua/utils.lua"))()
assert(SMODS.load_file("src/lua/api.lua"))()
assert(SMODS.load_file("src/lua/log.lua"))()
assert(SMODS.load_file("src/lua/settings.lua"))()

-- Initialize API
API.init()

-- Initialize Logger
LOG.init()

-- Apply all configuration and Love2D patches
SETTINGS.setup()

sendInfoMessage("BalatroBot loaded - version " .. SMODS.current_mod.version, "BALATROBOT")
