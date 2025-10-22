-- Load minimal required files
assert(SMODS.load_file("src/lua/utils.lua"))()
assert(SMODS.load_file("src/lua/api.lua"))()
assert(SMODS.load_file("src/lua/log.lua"))()
assert(SMODS.load_file("src/lua/settings.lua"))()

-- Apply all configuration and Love2D patches FIRST
-- This must run before API.init() to set G.BALATROBOT_PORT
SETTINGS.setup()

-- Initialize API (depends on G.BALATROBOT_PORT being set)
API.init()

-- Initialize Logger
LOG.init()

sendInfoMessage("BalatroBot loaded - version " .. SMODS.current_mod.version, "BALATROBOT")
