---@meta balatrobot-utils-types
---Type definitions for utility functions and helper modules

-- =============================================================================
-- Utility Module (used in utils.lua)
-- =============================================================================

---Utility functions for game state extraction and data processing
---@class utils
---@field sets_equal fun(list1: any[], list2: any[]): boolean Checks if two lists contain the same elements
---@field table_to_json fun(obj: any, depth?: number): string Converts a Lua table to JSON string with depth limiting
---@field COMPLETION_CONDITIONS table<string, table> Completion conditions for different game actions
