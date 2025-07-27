"""BalatroClient-specific test configuration and fixtures."""

import pytest

from balatrobot.client import BalatroClient
from balatrobot.enums import State
from balatrobot.exceptions import BalatroError, ConnectionFailedError
from balatrobot.models import G


@pytest.fixture(scope="function", autouse=True)
def reset_game_to_menu(port):
    """Reset game to menu state before each test."""
    try:
        with BalatroClient(port=port) as client:
            response = client.send_message("go_to_menu", {})
            game_state = G.model_validate(response)
            assert game_state.state_enum == State.MENU
    except (ConnectionFailedError, BalatroError):
        # Game not running or other API error, skip setup
        pass
