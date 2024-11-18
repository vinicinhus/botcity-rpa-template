import argparse

from botcity_aux.bot_runner import BotRunner


def parse_args():
    """
    Configure command-line arguments.

    Returns:
        argparse.Namespace: Configured arguments.
    """
    parser = argparse.ArgumentParser(description="Bot Runner Configuration")
    parser.add_argument(
        "--environment",
        type=str,
        choices=["production", "test"],
        default="test",
        help="Defines the execution environment: 'production' or 'test' (default: 'test')",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="Sets the execution timeout in minutes (0 for no limit).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    bot_runner = BotRunner(
        bot_name="My Bot",
        telegram_group="My Group",
        environment=args.environment,
        timeout=args.timeout,
    )
    bot_runner.run()
