-- Environment Variables
local headless = os.getenv("BALATROBOT_HEADLESS") == "1"
local fast = os.getenv("BALATROBOT_FAST") == "1"
local port = os.getenv("BALATROBOT_PORT")

SETTINGS = {}

-- BalatroBot Configuration
local config = {
  dt = fast and (4.0 / 60.0) or (1.0 / 60.0),
  headless = headless,
  fast = fast,
}

-- Apply Love2D patches for performance
local function apply_love_patches()
  local original_update = love.update
  ---@diagnostic disable-next-line: duplicate-set-field
  love.update = function(_)
    original_update(config.dt)
  end
end

-- Configure Balatro G globals for speed
local function configure_balatro_speed()
  -- Skip intro and splash screens
  G.SETTINGS.skip_splash = "Yes"

  if config.fast then
    -- Disable VSync completely
    love.window.setVSync(0)

    -- Fast mode settings
    G.FPS_CAP = nil -- Unlimited FPS
    G.SETTINGS.GAMESPEED = 10 -- 10x game speed
    G.ANIMATION_FPS = 60 -- 6x faster animations

    -- Disable visual effects
    G.SETTINGS.reduced_motion = true
    G.SETTINGS.screenshake = false
    G.VIBRATION = 0
    G.SETTINGS.GRAPHICS.shadows = "Off"
    G.SETTINGS.GRAPHICS.bloom = 0
    G.SETTINGS.GRAPHICS.crt = 0
    G.SETTINGS.GRAPHICS.texture_scaling = 1 -- Fastest (nearest neighbor)
    G.SETTINGS.rumble = false
    G.F_RUMBLE = nil

    -- Disable audio
    G.SETTINGS.SOUND.volume = 0
    G.SETTINGS.SOUND.music_volume = 0
    G.SETTINGS.SOUND.game_sounds_volume = 0
    G.F_MUTE = true

    -- Performance optimizations
    G.F_ENABLE_PERF_OVERLAY = false
    G.SETTINGS.WINDOW.vsync = 0
    G.F_SOUND_THREAD = false
    G.F_VERBOSE = false

    sendInfoMessage("BalatroBot: Running in fast mode")
  else
    -- Normal mode settings (defaults)
    -- Enable VSync
    love.window.setVSync(1)

    -- Performance settings
    G.FPS_CAP = 60
    G.SETTINGS.GAMESPEED = 4 -- Who plays at 1x speed?
    G.ANIMATION_FPS = 10
    G.VIBRATION = 0

    -- Feature flags - restore defaults from globals.lua
    G.F_ENABLE_PERF_OVERLAY = false
    G.F_MUTE = false
    G.F_SOUND_THREAD = true
    G.F_VERBOSE = true
    G.F_RUMBLE = nil

    -- Audio settings - restore normal levels
    G.SETTINGS.SOUND = G.SETTINGS.SOUND or {}
    G.SETTINGS.SOUND.volume = 50
    G.SETTINGS.SOUND.music_volume = 100
    G.SETTINGS.SOUND.game_sounds_volume = 100

    -- Graphics settings - restore normal quality
    G.SETTINGS.GRAPHICS = G.SETTINGS.GRAPHICS or {}
    G.SETTINGS.GRAPHICS.shadows = "On"
    G.SETTINGS.GRAPHICS.bloom = 1
    G.SETTINGS.GRAPHICS.crt = 70
    G.SETTINGS.GRAPHICS.texture_scaling = 2

    -- Window settings - restore normal display
    G.SETTINGS.WINDOW = G.SETTINGS.WINDOW or {}
    G.SETTINGS.WINDOW.vsync = 1

    -- Visual effects - restore normal motion
    G.SETTINGS.reduced_motion = false
    G.SETTINGS.screenshake = true
    G.SETTINGS.rumble = G.F_RUMBLE

    -- Skip intro but allow normal game flow
    G.SETTINGS.skip_splash = "Yes"

    sendInfoMessage("BalatroBot: Running in normal mode")
  end
end

-- Configure headless mode optimizations
local function configure_headless()
  if not config.headless then
    return
  end

  -- Hide the window instead of closing it
  if love.window and love.window.isOpen() then
    -- Try to minimize the window
    if love.window.minimize then
      love.window.minimize()
      sendInfoMessage("BalatroBot: Minimized SMODS loading window")
    end
    -- Set window to smallest possible size and move it off-screen
    love.window.setMode(1, 1)
    love.window.setPosition(-1000, -1000)
    sendInfoMessage("BalatroBot: Hidden SMODS loading window")
  end

  -- Disable all rendering operations
  ---@diagnostic disable-next-line: duplicate-set-field
  love.graphics.isActive = function()
    return false
  end

  -- Disable drawing operations
  ---@diagnostic disable-next-line: duplicate-set-field
  love.draw = function()
    -- Do nothing in headless mode
  end

  -- Disable graphics present/swap buffers
  ---@diagnostic disable-next-line: duplicate-set-field
  love.graphics.present = function()
    -- Do nothing in headless mode
  end

  -- Disable window creation/updates for future calls
  if love.window then
    ---@diagnostic disable-next-line: duplicate-set-field
    love.window.setMode = function()
      -- Return false to indicate window creation failed (headless)
      return false
    end

    ---@diagnostic disable-next-line: duplicate-set-field
    love.window.isOpen = function()
      return false
    end

    ---@diagnostic disable-next-line: duplicate-set-field
    love.graphics.isCreated = function()
      return false
    end
  end

  -- Log headless mode activation
  sendInfoMessage("BalatroBot: Headless mode enabled - graphics rendering disabled")
end

-- Main setup function
SETTINGS.setup = function()
  G.BALATROBOT_PORT = port or "12346"

  -- Apply Love2D performance patches
  apply_love_patches()

  -- Configure Balatro speed settings
  configure_balatro_speed()

  -- Apply headless optimizations if needed
  configure_headless()
end
