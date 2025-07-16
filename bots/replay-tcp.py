"""Simple TCP-based bot that replays actions from a run save (JSONL file)."""

import json
import logging
import socket
import sys
from pathlib import Path

# TCP connection settings
HOST = "127.0.0.1"
PORT = 12346
TIMEOUT = 10.0
BUFFER_SIZE = 65536


class TCPReplayBot:
    """Simple TCP-based replay bot for Balatro"""

    def __init__(self):
        self.sock: socket.socket | None = None

    def connect(self):
        """Connect to Balatro TCP server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        self.sock.connect((HOST, PORT))

    def disconnect(self):
        """Disconnect from Balatro TCP server"""
        if self.sock:
            self.sock.close()

    def send_message(self, name: str, arguments: dict) -> dict:
        """Send JSON message to Balatro and receive response"""
        if not self.sock:
            raise RuntimeError("Socket not connected")

        message = {"name": name, "arguments": arguments}
        self.sock.send(json.dumps(message).encode() + b"\n")

        data = self.sock.recv(BUFFER_SIZE)
        return json.loads(data.decode().strip())


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Load JSONL file
    assert sys.argv == 2, "Usage: python replay-tcp.py <jsonl_file>"
    jsonl_file = Path(sys.argv[1])
    with open(jsonl_file) as f:
        steps = [json.loads(line) for line in f if line.strip()]
    logger.info(f"Loaded {len(steps)} steps from {jsonl_file}")

    bot = TCPReplayBot()
    try:
        bot.connect()
        logger.info(f"Connected to Balatro at {HOST}:{PORT}")

        try:
            # Replay each step
            for i, step in enumerate(steps):
                function_name = step["function"]["name"]
                arguments = step["function"]["arguments"]
                logger.info(f"Step {i + 1}/{len(steps)}: {function_name}({arguments})")
                bot.send_message(function_name, arguments)

            logger.info("Replay completed successfully!")

        finally:
            bot.disconnect()

    except Exception as e:
        logger.error(f"Error during replay: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
