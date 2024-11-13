import time
from datetime import timedelta
from typing import Tuple

from botcity.maestro import BotExecution, BotMaestroSDK, ServerMessage
from loguru import logger

from .logger_config import LoggerConfig
from .telegram_plugin import TelegramBot


class BotRunner:
    """
    This class is responsible for initializing and running the bot execution flow,
    including setting up logging, handling BotMaestroSDK, and interacting with the Telegram API.

    Attributes:
        bot_name (str): The name of the bot, used for logging purposes.
        logger (LoggerConfig): Logger configuration instance to manage logging.
        bot_maestro_sdk_raise (bool): Flag indicating whether to raise errors on BotMaestroSDK connection failures.
        maestro (BotMaestroSDK): Instance of the BotMaestroSDK for managing bot execution tasks.
        telegram_bot (TelegramBot): Telegram bot integration.
    """

    def __init__(
        self,
        bot_name: str,
        bot_maestro_sdk_raise: bool = False,
        log_dir: str = "logs",
    ) -> None:
        """
        Initializes the BotRunner with the provided configuration.

        Args:
            bot_name (str): The name of the bot, used for logging.
            bot_maestro_sdk_raise (bool): Flag for BotMaestroSDK to raise exceptions on connection errors (default is False).
            log_dir (str): Directory to store log files (default is 'logs').
        """
        self.bot_name = bot_name

        self.logger = LoggerConfig(bot_name, log_dir)

        self.bot_maestro_sdk_raise = bot_maestro_sdk_raise
        self.maestro, self.execution = self._setup_maestro()

        self.telegram_token = self._get_telegram_token()
        self.telegram_bot = (
            TelegramBot(token=self.telegram_token) if self.telegram_token else None
        )
        self.start_time = None  # Initialize start time for execution tracking

    def _setup_maestro(self) -> Tuple[BotMaestroSDK, BotExecution]:
        """
        Initializes the BotMaestroSDK instance by loading configuration from the system arguments.
        Logs the execution details, including task ID and parameters.

        This method will return both the BotMaestroSDK instance and the BotExecution instance
        representing the current task execution.

        Returns:
            Tuple[BotMaestroSDK, BotExecution]: A tuple containing:
                - BotMaestroSDK instance (configured with system arguments).
                - BotExecution instance representing the current task execution.

        Raises:
            Exception: If initialization fails, an exception is raised and an error is logged.
        """
        try:
            # Set up the BotMaestroSDK with custom configuration
            BotMaestroSDK.RAISE_NOT_CONNECTED = self.bot_maestro_sdk_raise
            maestro = BotMaestroSDK.from_sys_args()
            execution: BotExecution = maestro.get_execution()

            # Log the task details
            logger.info(f"Task ID is: {execution.task_id}")
            logger.info(f"Task Parameters are: {execution.parameters}")

            return maestro, execution
        except Exception as e:
            logger.error(f"Failed to initialize BotMaestroSDK: {e}")
            raise e

    def _get_telegram_token(self) -> str:
        """
        Retrieves the Telegram bot token from the BotMaestro server.

        This method fetches the Telegram bot token stored as a credential on the BotMaestro server,
        identified by the label "Telegram" and the key "token". The token is used to authenticate
        the bot for Telegram API interactions.

        Returns:
            str: The Telegram bot token as a string.

        Raises:
            Exception: If an error occurs during the token retrieval, such as an issue with
                    server connectivity or invalid credentials.
        """
        try:
            token = self.maestro.get_credential(label="Telegram", key="token")
            logger.info("Telegram token retrieved successfully.")
            return token
        except Exception as e:
            logger.error(f"Failed to retrieve telegram token: {e}")
            raise e

    def _add_log_file_into_maestro(self) -> ServerMessage:
        """
        Uploads the log file to the BotMaestro server as an artifact.

        This method posts the log file generated by the logger to the BotMaestro platform
        under the specified task ID. The log file is sent as an artifact with the name
        and path specified in the logger configuration.

        Returns:
            ServerMessage: The response message from the BotMaestro server, containing
                        details about the uploaded artifact.

        Raises:
            Exception: If the file upload fails or there is an issue with the communication
                    with the BotMaestro server.
        """
        try:
            response: ServerMessage = self.maestro.post_artifact(
                task_id=self.execution.task_id,
                artifact_name=self.logger.log_filename,
                filepath=self.logger.log_path,
            )
            logger.info(
                f"Log file '{self.logger.log_filename}' uploaded successfully to BotCity Maestro."
            )
            return response
        except Exception as e:
            logger.error(
                f"Failed to upload log file '{self.logger.log_filename}' into BotCity Maestro: {e}"
            )
            raise e

    def _get_execution_time(self) -> str:
        """
        Calculates the duration of the bot execution in DD:HH:MM:SS format.

        Returns:
            str: A string representing the execution time in the format 'DD:HH:MM:SS'.
        """
        if self.start_time is None:
            return "Execution time not available"

        end_time = time.time()
        elapsed_seconds = int(end_time - self.start_time)
        elapsed_time = str(timedelta(seconds=elapsed_seconds))

        days, _ = divmod(elapsed_seconds, 86400)
        execution_time = f"{int(days):02}:{elapsed_time}"
        return execution_time

    def run(self) -> None:
        """
        Starts the bot execution process, including handling the logic for the bot's actions.

        Logs:
            Information about the start and completion of the bot execution.
        """
        try:
            self.start_time = time.time()
            logger.info("Bot execution started.")

            # Add bot execution logic here (e.g., interacting with Telegram or other services).
            # Example: self.telegram_bot.send_message("Hello", "Group")

            logger.info(f"{self.bot_name} Bot execution completed.")
            logger.info(f"Execution time: {self._get_execution_time()}")
        except Exception as e:
            self.telegram_bot.send_message(
                f"An error occurred during bot '{self.bot_name}' execution: {e}",
                "Your Group",
            )
            self.telegram_bot.upload_document(
                document=self.logger.log_path, group="Your Group", caption=self.bot_name
            )
            raise e
