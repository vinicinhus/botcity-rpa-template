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
    args, _ = parser.parse_known_args()  # Get only required arguments

    return args


if __name__ == "__main__":
    args = parse_args()

    BOT_NAME = "My Bot"
    TELEGRAM_GROUP = "My Group"
    LOG_FOLDER = "00"  # Enter the department number, e.g., 01, 97, 15...
    RECURRENCE = "daily"  # Options: 'weekly' or 'daily'
    SECTOR = "Sector Dev"
    DEVELOPER = "Your Name"
    STAKEHOLDER = "StakeHolder Name"
    MAX_RETRIES = 2  # 0 counts as 1, so always include it in the total retry count

    if args.environment == "maestro":
        bot_runner = BotRunnerMaestro(
            bot_name=BOT_NAME,
            use_telegram=True,
            telegram_group=TELEGRAM_GROUP,
            dev=DEVELOPER,
            sector=SECTOR,
            stakeholder=STAKEHOLDER,
            recurrence=RECURRENCE,
            max_retries=MAX_RETRIES,
            log_folder=LOG_FOLDER,
        )
    else:
        server = config("SERVER_MAESTRO", cast=str)
        login = config("LOGIN_MAESTRO", cast=str)
        key = config("KEY_MAESTRO", cast=str)

        if not server or not login or not key:
            raise ValueError(
                "SERVER_MAESTRO, LOGIN_MAESTRO, and KEY_MAESTRO must be provided in the .env file"
            )

        bot_runner = BotRunnerLocal(
            bot_name=BOT_NAME,
            server=server,
            login=login,
            key=key,
            use_telegram=False,
            telegram_group=TELEGRAM_GROUP,
            dev=DEVELOPER,
            sector=SECTOR,
            stakeholder=STAKEHOLDER,
            recurrence=RECURRENCE,
            max_retries=MAX_RETRIES,
            log_folder=LOG_FOLDER,
        )

    bot_runner.run()
