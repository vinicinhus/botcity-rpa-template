import argparse
import os

from botcity.botcity_local import BotRunnerLocal
from botcity.botcity_maestro import BotRunnerMaestro
from core.config import settings


def parse_args() -> argparse.Namespace:
    """
    Configure command-line arguments.

    Returns:
        argparse.Namespace: Configured arguments.
    """
    parser = argparse.ArgumentParser(description=settings.DESCRIPTION)
    parser.add_argument(
        "--environment",
        type=str,
        choices=[settings.CHOICE_MAESTRO, settings.CHOICE_LOCAL],
        default=settings.CHOICE_MAESTRO,  # Set 'maestro' as the default
        help=settings.HELP_MESSAGE,
    )
    args, _ = parser.parse_known_args()  # Get only required arguments

    return args


def get_bot_runner(args):
    """
    Factory method to create the appropriate bot runner based on arguments.
    """
    if not os.path.isfile(settings.CERTIFICATE_FILE_PATH):
        raise FileNotFoundError(
            f"Certificate file not found at: {settings.CERTIFICATE_FILE_PATH}"
        )

    if args.environment == settings.CHOICE_MAESTRO:
        return BotRunnerMaestro()
    else:
        if (
            not settings.SERVER_MAESTRO
            or not settings.LOGIN_MAESTRO
            or not settings.KEY_MAESTRO
        ):
            raise ValueError(
                "SERVER_MAESTRO, LOGIN_MAESTRO, and KEY_MAESTRO must be provided in the .env file"
            )
        return BotRunnerLocal(
            server=settings.SERVER_MAESTRO,
            login=settings.LOGIN_MAESTRO,
            key=settings.KEY_MAESTRO,
        )


if __name__ == "__main__":
    args = parse_args()
    bot_runner = get_bot_runner(args)
    bot_runner.run()
