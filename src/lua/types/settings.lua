---@meta balatrobot-settings-types
---Type definitions for configuration and settings structures

-- =============================================================================
-- Configuration Types (used in settings.lua and balatrobot.lua)
-- =============================================================================

---@class BalatrobotConfig
---@field port string Port for the bot to listen on
---@field dt number Tells the game that every update is dt seconds long
---@field headless boolean Whether running in headless mode
---@field fast boolean Whether running in fast mode

---@class SETTINGS
---@field setup fun() Main setup function that configures Love2D, Balatro speed, and headless mode
