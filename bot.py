import argparse

from decouple import config

from botcity_aux.bot_runner import BotRunnerLocal, BotRunnerMaestro


def parse_args() -> argparse.Namespace:
    """
    Configure command-line arguments.

    Returns:
        argparse.Namespace: Configured arguments.
    """
    parser = argparse.ArgumentParser(description="Bot Runner Configuration")
    parser.add_argument(
        "--environment",
        type=str,
        choices=["maestro", "local"],
        default="maestro",  # Set 'maestro' as the default
        help="Defines the execution environment: 'maestro' or 'local' (default: 'maestro')",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.environment == "maestro":
        bot_runner = BotRunnerMaestro(
            bot_name="My Bot",
            use_telegram=True,
            telegram_group="My Group",
        )
    else:
        server = config("SERVER_MAESTRO", cast=str)
        login = config("LOGIN_MAESTRO", cast=str)
        key = config("KEY_MAESTRO", cast=str)

        bot_runner = BotRunnerLocal(
            bot_name="My Bot",
            server=server,
            login=login,
            key=key,
            use_telegram=True,
            telegram_group="My Group",
        )

    bot_runner.run()
