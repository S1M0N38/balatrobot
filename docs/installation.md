# Installation Guide

This guide will walk you through installing and setting up Balatrobot.

## Prerequisites

Before installing Balatrobot, ensure you have:

- **[balatro](https://store.steampowered.com/app/2379780/Balatro/)**: Steam version (>= 1.0.1)
- **[git](https://git-scm.com/downloads)**: for cloning the repository
- **[uv](https://docs.astral.sh/uv/)**: for managing Python installations, environments and dependencies
- **[lovely](https://github.com/ethangreen-dev/lovely-injector)**: for injecting Lua code into Balatro (>= 0.8.0)
- **[steamodded](https://github.com/Steamodded/smods)**: for loading and injecting mods (>=1.0.0)

## Step 1: Install Balatrobot

Balatrobot is installed like any other Steamodded mod.

=== "Windows"

    ``` sh
    cd %AppData%/Balatro
    mkdir -p Mods
    cd Mods
    git clone https://github.com/S1M0N38/balatrobot.git
    ```

=== "MacOS"

    ``` sh
    cd "/Users/$USER/Library/Application Support/Balatro"
    mkdir -p Mods
    cd Mods
    git clone https://github.com/S1M0N38/balatrobot.git
    ```

=== "Linux"

    ``` sh
    cd ~/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro
    mkdir -p Mods
    cd Mods
    git clone https://github.com/S1M0N38/balatrobot.git
    ```

!!! tip

    You can also clone the repository somewhere else and then provide a symlink
    to the `balatrobot` directory in the `Mods` directory.

    === "Windows"

        ``` sh
        # Clone repository to a custom location
        cd C:\your\custom\path
        git clone https://github.com/S1M0N38/balatrobot.git
        
        # Create symlink in Mods directory
        cd %AppData%/Balatro/Mods
        mklink /D balatrobot C:\your\custom\path\balatrobot
        ```

    === "MacOS"

        ``` sh
        # Clone repository to a custom location
        cd /your/custom/path
        git clone https://github.com/S1M0N38/balatrobot.git
        
        # Create symlink in Mods directory
        cd "/Users/$USER/Library/Application Support/Balatro/Mods"
        ln -s /your/custom/path/balatrobot balatrobot
        ```

    === "Linux"

        ``` sh
        # Clone repository to a custom location
        cd /your/custom/path
        git clone https://github.com/S1M0N38/balatrobot.git
        
        # Create symlink in Mods directory
        cd ~/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods
        ln -s /your/custom/path/balatrobot balatrobot
        ```


??? "Update Balatrobot"

    Updating Balatrobot is as simple as pulling the latest changes from the repository.

    === "Windows"

        ``` sh
        cd %AppData%/Balatro/Mods/balatrobot
        git pull
        ```

    === "MacOS"

        ``` sh
        cd "/Users/$USER/Library/Application Support/Balatro/Mods/balatrobot"
        git pull
        ```

    === "Linux"

        ``` sh
        cd ~/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods/balatrobot
        git pull
        ```

??? "Uninstall Balatrobot"

    Simply delete the balatrobot mod directory.

    === "Windows"

        ``` sh
        cd %AppData%/Balatro/Mods
        rmdir /S /Q balatrobot
        ```

    === "MacOS"

        ``` sh
        cd "/Users/$USER/Library/Application Support/Balatro/Mods"
        rm -rf balatrobot
        ```

    === "Linux"

        ``` sh
        cd ~/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods
        rm -rf balatrobot
        ```

## Step 2: Setup Python Environment

Uv takes care of managing Python installations, virtual environments creation and dependencies installation.
To setup the Python environment for running Balatrobot bots simply run:

=== "Windows"

    ``` sh
    cd %AppData%/Balatro/Mods/balatrobot
    uv sync
    ```

=== "MacOS"

    ``` sh
    cd "/Users/$USER/Library/Application Support/Balatro/Mods/balatrobot"
    uv sync
    ```

=== "Linux"

    ``` sh
    cd ~/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods/balatrobot
    uv sync
    ```

The same command can be used to update the Python environment and dependencies in the future.

??? "Remove Python Environment"

    To uninstall the Python environment and dependencies, simply remove the `.venv` directory.

    === "Windows"

        ``` sh
        cd %AppData%/Balatro/Mods/balatrobot
        rmdir /S /Q .venv
        ```

    === "MacOS"

        ``` sh
        cd "/Users/$USER/Library/Application Support/Balatro/Mods/balatrobot"
        rm -rf .venv
        ```

    === "Linux"

        ``` sh
        cd ~/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods/balatrobot
        rm -rf .venv
        ```

## Step 3: Test Installation

### Launch Balatro with Mods

1. Start Balatro through Steam
2. In the main menu, click "Mods"
3. Verify "Balatrobot" appears in the mod list
4. Enable the mod if it's not already enabled and restart the game

!!! warning "macOS Steam Client Issue"

    On macOS, you cannot start Balatro through the Steam App due to a bug in the
    Steam client. Instead, you must use the `run_lovely_macos.sh` script.

    === "MacOS"

        ``` sh
        cd "/Users/$USER/Library/Application Support/Steam/steamapps/common/Balatro"
        ./run_lovely_macos.sh
        ```

    **First-time setup:** If this is your first time running the script, macOS Security & Privacy
    settings will prevent it from executing. Open **System Preferences** → **Security & Privacy**
    and click "Allow" when prompted, then run the script again.


### Quick Test with Example Bot

With Balatro running and the mod enabled, you can quickly test if everything is set up correctly using the provided example bot.


=== "Windows"

    ``` sh
    cd %AppData%/Balatro/Mods/balatrobot
    uv run bot_example.py
    ```

=== "MacOS"

    ``` sh
    cd "/Users/$USER/Library/Application Support/Balatro/Mods/balatrobot"
    uv run bot_example.py
    ```

=== "Linux"

    ``` sh
    cd ~/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods/balatrobot
    uv run bot_example.py
    ```

!!! tip 

    You can also navigate to the `balatrobot` directory, activate the Python
    environment and run the bot with `python bot_example.py` if you prefer.
    However, remember to always activate the virtual environment first.


The bot is working correctly if:

1. Game starts automatically
2. Cards are played/discarded automatically
3. Shop actions occur without user input
4. Game progresses through rounds

## Troubleshooting

If you encounter issues during installation or testing:

- **Discord Support**: Join our community at [https://discord.gg/xzBAj4JFVC](https://discord.gg/xzBAj4JFVC) for real-time help
- **GitHub Issues**: Report bugs or request features by [opening an issue](https://github.com/S1M0N38/balatrobot/issues) on GitHub
- **Documentation**: Check the [Troubleshooting](troubleshooting.md) page (work in progress)

---

*Once installation is complete, proceed to the [Bot Development Guide](bot-development.md) to create your first bot!*
