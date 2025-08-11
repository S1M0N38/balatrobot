---@meta balatrobot-log-types
---Type definitions for logging system and log entry structures

-- =============================================================================
-- Log System Types (used in log.lua)
-- =============================================================================

---@class Log
---@field mod_path string? Path to the mod directory for log file storage
---@field current_run_file string? Path to the current run's log file
---@field pending_logs table<string, PendingLog> Map of pending log entries awaiting conditions
---@field game_state_before G Game state before function call
---@field init fun() Initializes the logger by setting up hooks
---@field write fun(log_entry: LogEntry) Writes a log entry to the JSONL file
---@field update fun() Processes pending logs by checking completion conditions
---@field schedule_write fun(function_call: FunctionCall) Schedules a log entry to be written when condition is met

---@class PendingLog
---@field log_entry table The log entry data to be written when condition is met
---@field condition function Function that returns true when the log should be written

---@class FunctionCall
---@field name string The name of the function being called
---@field arguments table The parameters passed to the function

---@class LogEntry
---@field timestamp_ms_before number Timestamp in milliseconds since epoch before function call
---@field timestamp_ms_after number? Timestamp in milliseconds since epoch after function call
---@field function FunctionCall Function call information
---@field game_state_before G Game state before function call
---@field game_state_after G? Game state after function call
