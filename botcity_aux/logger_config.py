from datetime import datetime
from pathlib import Path

from loguru import logger


class LoggerConfig:
    """
    Configures the logger for the bot, creating a directory and log file with the specified name and date.

    Attributes:
        bot_name (str): The name of the bot, used as a prefix in the log file name.
        log_dir (Path): The directory where log files will be saved.
        log_filename (str): The name of the log file, which includes the bot name and current date.
        log_path (str): The full path of the generated log file.
    """

    def __init__(self, bot_name: str, log_dir: str = "logs") -> None:
        """
        Initializes the LoggerConfig by creating the log directory, log file,
        and configuring the logger to save rotated logs.

        Args:
            bot_name (str): The name of the bot to be used in the log file name.
            log_dir (str): The directory where logs will be saved (default: "logs").
        """
        self.bot_name: str = bot_name
        self.log_filename: str = self._create_log_filename()
        self.log_dir: Path = Path(log_dir)
        self.log_path: str = self._create_log_path()
        self._setup_logger()

    def _create_log_filename(self) -> str:
        """
        Creates the log file name based on the bot's name and the current date.

        Returns:
            str: The name of the log file in the format: '<bot_name>-<YYYY-MM-DD>.log'
        """
        log_filename: str = f"{self.bot_name}-{datetime.now().strftime('%Y-%m-%d')}.log"
        return log_filename

    def _create_log_path(self) -> str:
        """
        Creates the full path for the log file by combining the log directory and the log file name.
        If the directory doesn't exist, it will be created.

        Returns:
            str: The full path of the log file.

        Raises:
            PermissionError: If the directory creation is not permitted.
            Exception: If an error occurs while creating the log directory.
        """
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.error(
                f"Permission denied when trying to create directory: {self.log_dir}"
            )
            raise e
        except Exception as e:
            logger.error(
                f"Failed to create log directory: {self.log_dir}. Error: {str(e)}"
            )
            raise e

        return str(self.log_dir / self.log_filename)

    def _setup_logger(self) -> None:
        """
        Configures the Loguru logger to use the created log file and rotate it every 10 MB.

        This method sets up the Loguru logger to log messages to a file with rotation, ensuring that
        the log files are not too large.

        Raises:
            Exception: If the logger setup fails.
        """
        try:
            # Add log file with rotation
            logger.add(self.log_path, rotation="10 MB", colorize=False, encoding="utf8")
        except Exception as e:
            logger.error(
                f"Failed to set up logger with path {self.log_path}. Error: {str(e)}"
            )
            raise e
