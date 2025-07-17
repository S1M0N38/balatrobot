"""BalatroBot - Python client for the BalatroBot game API."""

from .client import BalatroClient
from .enums import Actions, Decks, Stakes, State
from .exceptions import BalatroError
from .models import GameState

__version__ = "0.5.0"
__all__ = [
    # Main client
    "BalatroClient",
    # Enums
    "Actions",
    "Decks",
    "Stakes",
    "State",
    # Exception
    "BalatroError",
    # Models
    "GameState",
]
