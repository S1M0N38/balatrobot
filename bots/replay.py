"""Simple bot that replays actions from a run save (JSONL file)."""

import json
import logging
import sys
from pathlib import Path

from balatrobot.client import BalatroClient
from balatrobot.exceptions import BalatroError, ConnectionFailedError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def load_steps_from_jsonl() -> list[dict]:
    """Load replay steps from JSONL file."""
    if len(sys.argv) != 2:
        logger.error("Usage: python replay.py <jsonl_file>")
        sys.exit(1)

    jsonl_file = Path(sys.argv[1])
    if not jsonl_file.exists():
        logger.error(f"File not found: {jsonl_file}")
        sys.exit(1)

    try:
        with open(jsonl_file) as f:
            steps = [json.loads(line) for line in f if line.strip()]
        logger.info(f"Loaded {len(steps)} steps from {jsonl_file}")
        return steps
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {jsonl_file}: {e}")
        sys.exit(1)


def main():
    """Main replay function."""
    steps = load_steps_from_jsonl()

    try:
        with BalatroClient() as client:
            logger.info("Connected to BalatroBot API")

            # Replay each step
            for i, step in enumerate(steps):
                function_name = step["function"]["name"]
                arguments = step["function"]["arguments"]
                logger.info(f"Step {i + 1}/{len(steps)}: {function_name}({arguments})")

                try:
                    response = client.send_message(function_name, arguments)
                    logger.debug(f"Response: {response}")
                except BalatroError as e:
                    logger.error(f"API error in step {i + 1}: {e}")
                    sys.exit(1)

            logger.info("Replay completed successfully!")

    except ConnectionFailedError as e:
        logger.error(f"Failed to connect to BalatroBot API: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Replay interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error during replay: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
