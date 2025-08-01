"""Simple bot that replays actions from a run save (JSONL file)."""

import argparse
import json
import logging
import sys
import tempfile
import time
from pathlib import Path

from balatrobot.client import BalatroClient
from balatrobot.exceptions import BalatroError, ConnectionFailedError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def format_function_call(function_name: str, arguments: dict) -> str:
    """Format function call in Python syntax for dry run mode."""
    args_str = json.dumps(arguments, indent=None, separators=(",", ": "))
    return f"{function_name}({args_str})"


def determine_output_path(output_arg: Path | None, input_path: Path) -> Path:
    """Determine the final output path based on input and output arguments."""
    if output_arg is None:
        return input_path

    if output_arg.is_dir():
        return output_arg / input_path.name
    else:
        return output_arg


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
    parser = argparse.ArgumentParser(
        description="Replay actions from a JSONL run file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Input JSONL file to replay",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path for generated run log (directory or .jsonl file). "
        "If directory, uses original filename. If not specified, overwrites input.",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=12346,
        help="Port to connect to BalatroBot API",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay between played moves in seconds",
    )
    parser.add_argument(
        "--dry",
        "-d",
        action="store_true",
        help="Dry run mode: print function calls without executing them",
    )

    args = parser.parse_args()

    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)

    if not args.input.suffix == ".jsonl":
        logger.error(f"Input file must be a .jsonl file: {args.input}")
        sys.exit(1)

    steps = load_steps_from_jsonl(args.input)
    final_output_path = determine_output_path(args.output, args.input)
    if args.dry:
        logger.info(
            f"Dry run mode: printing {len(steps)} function calls from {args.input}"
        )
        for i, step in enumerate(steps):
            function_name = step["function"]["name"]
            arguments = step["function"]["arguments"]
            print(format_function_call(function_name, arguments))
            time.sleep(args.delay)
        logger.info("Dry run completed")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output_path = Path(temp_dir) / final_output_path.name

        try:
            with BalatroClient(port=args.port) as client:
                logger.info(f"Connected to BalatroBot API on port {args.port}")
                logger.info(f"Replaying {len(steps)} steps from {args.input}")
                if final_output_path != args.input:
                    logger.info(f"Output will be saved to: {final_output_path}")

                for i, step in enumerate(steps):
                    function_name = step["function"]["name"]
                    arguments = step["function"]["arguments"]

                    if function_name == "start_run":
                        arguments = arguments.copy()
                        arguments["log_path"] = str(temp_output_path)

                    logger.info(
                        f"Step {i + 1}/{len(steps)}: {format_function_call(function_name, arguments)}"
                    )
                    time.sleep(args.delay)

                    try:
                        response = client.send_message(function_name, arguments)
                        logger.debug(f"Response: {response}")
                    except BalatroError as e:
                        logger.error(f"API error in step {i + 1}: {e}")
                        sys.exit(1)

                logger.info("Replay completed successfully!")

                if temp_output_path.exists():
                    final_output_path.parent.mkdir(parents=True, exist_ok=True)
                    temp_output_path.rename(final_output_path)
                    logger.info(f"Output saved to: {final_output_path}")
                elif final_output_path != args.input:
                    logger.warning(
                        f"No output file was generated at {temp_output_path}"
                    )

        except ConnectionFailedError as e:
            logger.error(
                f"Failed to connect to BalatroBot API on port {args.port}: {e}"
            )
            sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Replay interrupted by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error during replay: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
