import json
import os
import random
import socket
import string
from abc import ABC, abstractmethod
from datetime import datetime

from .enums import Actions, Decks, Stakes, State


def cache_state(game_step, G):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    if not os.path.exists(f"gamestate_cache/{game_step}/"):
        os.makedirs(f"gamestate_cache/{game_step}/")
    filename = f"gamestate_cache/{game_step}/{timestamp}.json"
    with open(filename, "w") as f:
        f.write(json.dumps(G, indent=4))


class Bot(ABC):
    def __init__(
        self,
        deck: Decks,
        stake: Stakes = Stakes.WHITE,
        seed: str = "",
        challenge: str | None = None,
        bot_port: int = 12346,
    ):
        self.G = None
        self.deck = deck
        self.stake = stake
        self.seed = seed
        self.challenge = challenge

        self.bot_port = bot_port

        self.addr = ("127.0.0.1", self.bot_port)
        self.running = False
        self.balatro_instance = None

        self.sock = None

        self.state = {}

    @staticmethod
    def random_seed():
        return "".join(random.choices(string.digits + string.ascii_uppercase, k=7))

    @abstractmethod
    def skip_or_select_blind(self, env: dict):
        pass

    @abstractmethod
    def select_cards_from_hand(self, env: dict):
        pass

    @abstractmethod
    def select_shop_action(self, env: dict):
        pass

    @abstractmethod
    def select_booster_action(self, env: dict):
        pass

    @abstractmethod
    def sell_jokers(self, env: dict):
        pass

    @abstractmethod
    def rearrange_jokers(self, env: dict):
        pass

    @abstractmethod
    def use_or_sell_consumables(self, env: dict):
        pass

    @abstractmethod
    def rearrange_consumables(self, env: dict):
        pass

    @abstractmethod
    def rearrange_hand(self, env: dict):
        pass

    def _action_to_action_str(self, action):
        result = []

        for x in action:
            if isinstance(x, Actions):
                result.append(x.name)
            elif type(x) is list:
                result.append(",".join([str(y) for y in x]))
            else:
                result.append(str(x))

        return "|".join(result)

    def chooseaction(self, env: dict):
        print("Choosing action based on game state:", env["state"])
        if env["state"] == State.GAME_OVER:
            self.running = False

        match env["waitingFor"]:
            case "start_run":
                print("Starting run with deck:", self.deck)
                seed = self.seed or self.random_seed()
                return [
                    Actions.START_RUN,
                    self.stake.value,
                    self.deck.value,
                    seed,
                    self.challenge,
                ]
            case "skip_or_select_blind":
                print("Choosing action: skip_or_select_blind")
                return self.skip_or_select_blind(env)
            case "select_cards_from_hand":
                print("Choosing action: select_cards_from_hand")
                return self.select_cards_from_hand(env)
            case "select_shop_action":
                print("Choosing action: select_shop_action")
                return self.select_shop_action(env)
            case "select_booster_action":
                print("Choosing action: select_booster_action")
                return self.select_booster_action(env)
            case "sell_jokers":
                print("Choosing action: sell_jokers")
                return self.sell_jokers(env)
            case "rearrange_jokers":
                print("Choosing action: rearrange_jokers")
                return self.rearrange_jokers(env)
            case "use_or_sell_consumables":
                print("Choosing action: use_or_sell_consumables")
                return self.use_or_sell_consumables(env)
            case "rearrange_consumables":
                print("Choosing action: rearrange_consumables")
                return self.rearrange_consumables(env)
            case "rearrange_hand":
                print("Choosing action: rearrange_hand")
                return self.rearrange_hand(env)

    def run_step(self):
        if self.sock is None:
            self.state = {}
            self.G = None

            self.running = True
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(1)
            self.sock.connect(self.addr)

        if self.running:
            self.sock.send(bytes("HELLO", "utf-8"))

            try:
                data = self.sock.recv(65536)
                env = json.loads(data)

                if "response" in env:
                    print(env["response"])
                else:
                    if env["waitingForAction"]:
                        cache_state(env["waitingFor"], env)
                        action = self.chooseaction(env)
                        if action:
                            action_str = self._action_to_action_str(action)
                            self.sock.send(bytes(action_str, "utf-8"))
                        else:
                            raise ValueError("All actions must return a value!")

            except socket.error as e:
                print(e)
                print("Socket error, reconnecting...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.settimeout(1)
                self.sock.connect(self.addr)

    def run(self):
        while self.running:
            self.run_step()
