"""Simple bot that replays actions from a run save (JSONL file)."""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from balatrobot.client import BalatroClient
from balatrobot.exceptions import BalatroError, ConnectionFailedError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_most_recent_jsonl() -> Path:
    """Find the most recent JSONL file in the runs directory."""
    runs_dir = Path("runs")
    if not runs_dir.exists():
        logger.error("Runs directory not found")
        sys.exit(1)

    jsonl_files = list(runs_dir.glob("*.jsonl"))
    if not jsonl_files:
        logger.error("No JSONL files found in runs directory")
        sys.exit(1)

    # Sort by modification time, most recent first
    most_recent = max(jsonl_files, key=lambda f: f.stat().st_mtime)
    return most_recent


def load_steps_from_jsonl(jsonl_path: Path) -> list[dict]:
    """Load replay steps from JSONL file."""
    if not jsonl_path.exists():
        logger.error(f"File not found: {jsonl_path}")
        sys.exit(1)

    try:
        with open(jsonl_path) as f:
            steps = [json.loads(line) for line in f if line.strip()]
        logger.info(f"Loaded {len(steps)} steps from {jsonl_path}")
        return steps
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {jsonl_path}: {e}")
        sys.exit(1)


def main():
    """Main replay function."""
    parser = argparse.ArgumentParser(description="Replay actions from a JSONL run file")
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=0.0,
        help="Delay between played moves in seconds (default: 0.0)",
    )
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        help="Path to JSONL run file (default: most recent file in runs/)",
    )

    args = parser.parse_args()

    # Determine the path to use
    if args.path:
        jsonl_path = args.path
    else:
        jsonl_path = get_most_recent_jsonl()
        logger.info(f"Using most recent file: {jsonl_path}")

    steps = load_steps_from_jsonl(jsonl_path)

    try:
        with BalatroClient() as client:
            logger.info("Connected to BalatroBot API")

            # Replay each step
            for i, step in enumerate(steps):
                function_name = step["function"]["name"]
                arguments = step["function"]["arguments"]
                logger.info(f"Step {i + 1}/{len(steps)}: {function_name}({arguments})")
                time.sleep(args.delay)

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
