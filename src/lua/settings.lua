-- Environment Variables
local headless = os.getenv("BALATROBOT_HEADLESS") == "1"
local fast = os.getenv("BALATROBOT_FAST") == "1"
local audio = os.getenv("BALATROBOT_AUDIO") == "1"
local port = os.getenv("BALATROBOT_PORT")

SETTINGS = {}

-- BalatroBot Configuration
local config = {
  dt = headless and (4.99 / 60.0) or (1.0 / 60.0),
  headless = headless,
  fast = fast,
  audio = audio,
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
  G.F_SKIP_TUTORIAL = true

  -- Configure audio based on --audio flag
  if config.audio then
    -- Enable audio when --audio flag is used
    G.SETTINGS.SOUND = G.SETTINGS.SOUND or {}
    G.SETTINGS.SOUND.volume = 50
    G.SETTINGS.SOUND.music_volume = 100
    G.SETTINGS.SOUND.game_sounds_volume = 100
    G.F_MUTE = false
  else
    -- Disable audio by default
    G.SETTINGS.SOUND.volume = 0
    G.SETTINGS.SOUND.music_volume = 0
    G.SETTINGS.SOUND.game_sounds_volume = 0
    G.F_MUTE = true
  end

  if config.fast then
    -- Disable VSync completely
    love.window.setVSync(0)

    -- Fast mode settings
    G.FPS_CAP = nil -- Unlimited FPS
    G.SETTINGS.GAMESPEED = 10 -- 10x game speed
    G.ANIMATION_FPS = 60 -- 6x faster animations

    -- Disable visual effects
    G.SETTINGS.reduced_motion = true -- Enable reduced motion in fast mode
    G.SETTINGS.screenshake = false
    G.VIBRATION = 0
    G.SETTINGS.GRAPHICS.shadows = "Off" -- Always disable shadows
    G.SETTINGS.GRAPHICS.bloom = 0 -- Always disable CRT bloom
    G.SETTINGS.GRAPHICS.crt = 0 -- Always disable CRT
    G.SETTINGS.GRAPHICS.texture_scaling = 1 -- Always disable pixel art smoothing
    G.SETTINGS.rumble = false
    G.F_RUMBLE = nil

    -- Performance optimizations
    G.F_ENABLE_PERF_OVERLAY = false
    G.SETTINGS.WINDOW.vsync = 0
    G.F_SOUND_THREAD = config.audio -- Enable sound thread only if audio is enabled
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
    G.F_MUTE = not config.audio -- Mute if audio is disabled
    G.F_SOUND_THREAD = config.audio -- Enable sound thread only if audio is enabled
    G.F_VERBOSE = true
    G.F_RUMBLE = nil

    -- Audio settings - only restore if audio is enabled
    if config.audio then
      G.SETTINGS.SOUND = G.SETTINGS.SOUND or {}
      G.SETTINGS.SOUND.volume = 50
      G.SETTINGS.SOUND.music_volume = 100
      G.SETTINGS.SOUND.game_sounds_volume = 100
    end

    -- Graphics settings - restore normal quality
    G.SETTINGS.GRAPHICS = G.SETTINGS.GRAPHICS or {}
    G.SETTINGS.GRAPHICS.shadows = "Off" -- Always disable shadows
    G.SETTINGS.GRAPHICS.bloom = 0 -- Always disable CRT bloom
    G.SETTINGS.GRAPHICS.crt = 0 -- Always disable CRT
    G.SETTINGS.GRAPHICS.texture_scaling = 1 -- Always disable pixel art smoothing

    -- Window settings - restore normal display
    G.SETTINGS.WINDOW = G.SETTINGS.WINDOW or {}
    G.SETTINGS.WINDOW.vsync = 0

    -- Visual effects - enable reduced motion
    G.SETTINGS.reduced_motion = true -- Always enable reduced motion
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
