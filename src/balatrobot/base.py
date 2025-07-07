import json
import random
import socket
import string
from abc import ABC, abstractmethod
from typing import Any, TypedDict

from .enums import Actions, Decks, Stakes, State
from .utils import get_logger


class ActionSchema(TypedDict):
    """Schema for action dictionary with name and arguments fields."""

    action: Actions
    args: list[Any] | None


class Bot(ABC):
    """Abstract base class for Balatro bots.

    This class provides the framework for creating bots that can play Balatro.
    Subclasses must implement all abstract methods to define the bot's behavior.

    Attributes:
        G (dict[str, Any] | None): The current game state.
        deck (Decks): The deck type to use.
        stake (Stakes): The stake level to play at.
        seed (str): The random seed for the game.
        challenge (str | None): The challenge mode, if any.
        bot_port (int): The port for bot communication.
        addr (tuple[str, int]): The socket address for communication.
        running (bool): Whether the bot is currently running.
        balatro_instance (Any): The Balatro game instance.
        sock (socket.socket | None): The socket for communication.
        state (dict[str, Any]): The bot's internal state.
    """

    def __init__(
        self,
        deck: Decks,
        stake: Stakes = Stakes.WHITE,
        seed: str = "",
        challenge: str | None = None,
        bot_port: int = 12346,
    ) -> None:
        """Initialize a new Bot instance.

        Args:
            deck (Decks): The deck type to use.
            stake (Stakes): The stake level to play at.
            seed (str): The random seed for the game.
            challenge (str | None): The challenge mode, if any.
            bot_port (int): The port for bot communication.
        """
        self.G: dict[str, Any] | None = None
        self.deck: Decks = deck
        self.stake: Stakes = stake
        self.seed: str = seed
        self.challenge: str | None = challenge

        self.bot_port: int = bot_port

        self.addr: tuple[str, int] = ("127.0.0.1", self.bot_port)
        self.running: bool = False
        self.balatro_instance: Any = None

        self.sock: socket.socket | None = None

        self.state: dict[str, Any] = {}
        self.logger = get_logger("bot")

        # Initialize socket connection
        self._initialize_socket()

    def _initialize_socket(self) -> None:
        """Initialize the socket connection for bot communication.

        Sets up the UDP socket with timeout and connects to the game instance.
        """
        self.state = {}
        self.G = None
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)
        self.sock.connect(self.addr)
        self.logger.debug("Socket initialized and connected to %s:%d", *self.addr)

    @staticmethod
    def random_seed() -> str:
        """Generate a random seed for the game.

        Returns:
            str: A random 7-character seed string.
        """
        return "".join(random.choices(string.digits + string.ascii_uppercase, k=7))

    @abstractmethod
    def skip_or_select_blind(self, env: dict) -> ActionSchema:
        """
        Decide whether to skip or select a blind.

        Returns:
            ActionSchema with 'action' (Actions enum) and optional 'args' (any additional arguments)
            Example: {'action': Actions.SELECT_BLIND, 'args': [0]}
        """
        pass

    @abstractmethod
    def select_cards_from_hand(self, env: dict) -> ActionSchema:
        """
        Select cards from hand to play or discard.

        Returns:
            ActionSchema with 'action' (Actions enum) and optional 'args' (card indices)
            Example: {'action': Actions.PLAY_HAND, 'args': [1, 2, 3]}
        """
        pass

    @abstractmethod
    def select_shop_action(self, env: dict) -> ActionSchema:
        """
        Select an action in the shop.

        Returns:
            ActionSchema with 'action' (Actions enum) and optional 'args' (shop item index)
            Example: {'action': Actions.BUY_CARD, 'args': [0]}
        """
        pass

    @abstractmethod
    def select_booster_action(self, env: dict) -> ActionSchema:
        """
        Select an action for booster packs.

        Returns:
            ActionSchema with 'action' (Actions enum) and optional 'args' (booster card index)
            Example: {'action': Actions.SELECT_BOOSTER_CARD, 'args': [0]}
        """
        pass

    @abstractmethod
    def sell_jokers(self, env: dict) -> ActionSchema:
        """
        Sell jokers from the collection.

        Returns:
            ActionSchema with 'action' (Actions enum) and optional 'args' (joker index)
            Example: {'action': Actions.SELL_JOKER, 'args': [0]}
        """
        pass

    @abstractmethod
    def rearrange_jokers(self, env: dict) -> ActionSchema:
        """
        Rearrange jokers in the collection.

        Returns:
            ActionSchema with 'action' (Actions enum) and optional 'args' (new arrangement)
            Example: {'action': Actions.REARRANGE_JOKERS, 'args': [0, 1, 2]}
        """
        pass

    @abstractmethod
    def use_or_sell_consumables(self, env: dict) -> ActionSchema:
        """
        Use or sell consumable cards.

        Returns:
            ActionSchema with 'action' (Actions enum) and optional 'args' (consumable index)
            Example: {'action': Actions.USE_CONSUMABLE, 'args': [0]}
        """
        pass

    @abstractmethod
    def rearrange_consumables(self, env: dict) -> ActionSchema:
        """
        Rearrange consumable cards.

        Returns:
            ActionSchema with 'action' (Actions enum) and optional 'args' (new arrangement)
            Example: {'action': Actions.REARRANGE_CONSUMABLES, 'args': [0, 1, 2]}
        """
        pass

    @abstractmethod
    def rearrange_hand(self, env: dict) -> ActionSchema:
        """
        Rearrange cards in hand.

        Returns:
            ActionSchema with 'action' (Actions enum) and optional 'args' (new arrangement)
            Example: {'action': Actions.REARRANGE_HAND, 'args': [0, 1, 2, 3, 4]}
        """
        pass

    def _action_to_action_str(self, action: ActionSchema) -> str:
        """
        Convert action to string format expected by the game.

        Args:
            action: ActionSchema dict with 'action' and optional 'args'

        Returns:
            Pipe-separated string representation of the action
        """
        result = []

        # Add the action name
        action_enum = action.get("action")
        if isinstance(action_enum, Actions):
            result.append(action_enum.name)
        else:
            result.append(str(action_enum))

        # Add arguments if present
        args = action.get("args")
        if args:
            if isinstance(args, list):
                result.append(",".join([str(arg) for arg in args]))
            else:
                result.append(str(args))

        return "|".join(result)

    def chooseaction(self, env: dict[str, Any]) -> ActionSchema:
        """Choose an action based on the current game state.

        Args:
            env (dict[str, Any]): The current game environment state.

        Returns:
            ActionSchema: The action to perform with 'action' and optional 'args'.
        """
        try:
            state_name = State(env["state"]).name
        except ValueError:
            state_name = f"UNKNOWN({env['state']})"
        self.logger.debug("Choosing action based on game state: %s", state_name)
        if env["state"] == State.GAME_OVER:
            self.running = False

        match env["waitingFor"]:
            case "start_run":
                self.logger.info("Starting run with deck: %s", self.deck)
                seed = self.seed or self.random_seed()
                return {
                    "action": Actions.START_RUN,
                    "args": [self.stake.value, self.deck.value, seed, self.challenge],
                }
            case "skip_or_select_blind":
                self.logger.debug("Choosing action: skip_or_select_blind")
                return self.skip_or_select_blind(env)
            case "select_cards_from_hand":
                self.logger.debug("Choosing action: select_cards_from_hand")
                return self.select_cards_from_hand(env)
            case "select_shop_action":
                self.logger.debug("Choosing action: select_shop_action")
                return self.select_shop_action(env)
            case "select_booster_action":
                self.logger.debug("Choosing action: select_booster_action")
                return self.select_booster_action(env)
            case "sell_jokers":
                self.logger.debug("Choosing action: sell_jokers")
                return self.sell_jokers(env)
            case "rearrange_jokers":
                self.logger.debug("Choosing action: rearrange_jokers")
                return self.rearrange_jokers(env)
            case "use_or_sell_consumables":
                self.logger.debug("Choosing action: use_or_sell_consumables")
                return self.use_or_sell_consumables(env)
            case "rearrange_consumables":
                self.logger.debug("Choosing action: rearrange_consumables")
                return self.rearrange_consumables(env)
            case "rearrange_hand":
                self.logger.debug("Choosing action: rearrange_hand")
                return self.rearrange_hand(env)
            case _:
                raise ValueError(f"Unhandled waitingFor state: {env['waitingFor']}")

    def run_step(self) -> None:
        """Execute a single step of the bot's main loop.

        This method handles socket communication, receives game state updates,
        and sends actions back to the game.
        """
        if not self.running or self.sock is None:
            return

        if self.running:
            self.sock.send(bytes("HELLO", "utf-8"))

            try:
                data = self.sock.recv(65536)
                env = json.loads(data)

                if "response" in env:
                    self.logger.info("Game response: %s", env["response"])
                else:
                    if env["waitingForAction"]:
                        action = self.chooseaction(env)
                        if action:
                            action_str = self._action_to_action_str(action)
                            self.sock.send(bytes(action_str, "utf-8"))
                        else:
                            raise ValueError("All actions must return a value!")

            except socket.error as e:
                self.logger.error("Socket error: %s", e)
                self.logger.warning("Socket error, reconnecting...")
                self._initialize_socket()

    def run(self) -> None:
        """Run the bot's main game loop.

        This method continues running until the bot is stopped,
        executing run_step() repeatedly.
        """
        while self.running:
            self.run_step()
