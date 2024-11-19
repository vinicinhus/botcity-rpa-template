import time
import warnings
from typing import Optional, Tuple

import GPUtil
import psutil
from botcity.maestro import BotExecution, BotMaestroSDK, ServerMessage
from loguru import logger
from urllib3.exceptions import InsecureRequestWarning

from src.main import main

from .logger_config import LoggerConfig
from .telegram_plugin import TelegramBot


class BotRunnerMaestro:
    def __init__(
        self,
        bot_name: str,
        bot_maestro_sdk_raise: bool = False,
        log_dir: str = "logs",
        telegram_group: str = None,
    ) -> None:
        """
        Initializes the BotRunnerMaestro with the provided configuration.

        Args:
            bot_name (str): The name of the bot, used for logging and notifications.
            bot_maestro_sdk_raise (bool, optional): Whether to raise exceptions when 
                BotMaestroSDK encounters connection issues (default: False).
            log_dir (str, optional): Directory where log files will be stored (default: "logs").
            telegram_group (Optional[str]): The Telegram group name or ID for sending notifications.

        Raises:
            ValueError: If 'telegram_group' is not provided.
        """
        if not telegram_group:
            raise ValueError("Telegram group must be provided")

        self.bot_name: str = bot_name
        self.telegram_group: str = telegram_group
        self.logger: LoggerConfig = LoggerConfig(bot_name, log_dir)

        self.bot_maestro_sdk_raise: bool = bot_maestro_sdk_raise
        self.maestro, self.execution = self._setup_maestro()

        self.telegram_token: str = self._get_telegram_token()
        self.telegram_bot: TelegramBot = (
            TelegramBot(token=self.telegram_token) if self.telegram_token else None
        )
        self.start_time: Optional[float] = None

    def _setup_maestro(self) -> Tuple[BotMaestroSDK, BotExecution]:
        """
        Sets up the BotMaestroSDK and retrieves the current task execution.

        Returns:
            Tuple[BotMaestroSDK, BotExecution]: 
                - BotMaestroSDK: Instance configured with system arguments.
                - BotExecution: Current task execution details.

        Raises:
            Exception: If the SDK initialization or execution retrieval fails.
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

        Returns:
            str: The Telegram bot token, or None if retrieval fails.

        Raises:
            Exception: If an error occurs during token retrieval.
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
        Uploads the bot's log file as an artifact to the BotMaestro server.

        Returns:
            ServerMessage: Response message from the BotMaestro server.

        Raises:
            Exception: If the file upload fails.
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
        Computes the execution duration since the bot's start time.

        Returns:
            str: Execution time formatted as 'DD:HH:MM:SS'.
        """
        if self.start_time is None:
            return "Execution time not available"

        end_time = time.time()
        elapsed_seconds = int(end_time - self.start_time)

        days, remainder = divmod(elapsed_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        execution_time = f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"
        return execution_time

    def _get_resource_usage(self) -> str:
        """
        Retrieves current resource usage (CPU, RAM, and GPU).

        Returns:
            str: Formatted string with CPU, RAM, and GPU usage.
        """
        # CPU and RAM usage
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory()
        ram_percent = ram_usage.percent
        ram_used_mb = ram_usage.used / (1024 * 1024)

        # GPU usage (if GPU is available)
        gpu_stats = []
        gpus = GPUtil.getGPUs()
        if gpus:
            for gpu in gpus:
                gpu_stats.append(
                    f"GPU {gpu.id}: {gpu.name}, Load: {gpu.load * 100:.1f}%, "
                    f"Memory: {gpu.memoryUsed}MB/{gpu.memoryTotal}MB"
                )
            gpu_usage_str = "; ".join(gpu_stats)
        else:
            gpu_usage_str = "No GPU found."

        # Format the usage information
        usage_info = f"CPU Usage: {cpu_percent}%, RAM Usage: {ram_percent}% ({ram_used_mb:.1f} MB), GPU Usage: {gpu_usage_str}"
        return usage_info

    def _execute_bot_task(self) -> None:
        """
        Executes the main bot task logic.

        Note:
            This method should be extended with the actual task logic for your bot.
        """
        main()

    def run(self) -> None:
        """
        Starts the bot execution process.

        Logs:
            Information about the bot's execution start, completion, and errors.

        Raises:
            Exception: If an error occurs during execution.
        """
        try:
            self.start_time = time.time()
            logger.info("Bot execution started.")

            self._execute_bot_task()

            logger.info(f"{self.bot_name} Bot execution completed.")
            logger.info(f"Execution time: {self._get_execution_time()}")
            logger.info(
                f"Resource usage at end of execution: {self._get_resource_usage()}"
            )
            self.telegram_bot.send_message(
                f"{self.bot_name} Bot execution completed.", group=self.telegram_group
            )
            self.telegram_bot.upload_document(
                document=self.logger.log_path,
                group=self.telegram_group,
                caption=self.bot_name,
            )
        except Exception as e:
            self.telegram_bot.send_message(
                f"An error occurred during bot '{self.bot_name}' execution: {e}",
                self.telegram_group,
            )
            self.telegram_bot.upload_document(
                document=self.logger.log_path,
                group=self.telegram_group,
                caption=self.bot_name,
            )
            raise e
        finally:
            self._add_log_file_into_maestro()


class BotRunnerLocal(BotMaestroSDK):
    def __init__(
        self,
        bot_name: str,
        server: str,
        login: str,
        key: str,
        log_dir: str = "logs",
        telegram_group: str = None,
    ) -> None:
        """
        Initializes the BotRunnerLocal instance with the specified configuration.

        Args:
            bot_name (str): The bot's name, used for logging purposes.
            server (str): BotMaestro server URL.
            login (str): BotMaestro login credential.
            key (str): BotMaestro authentication key.
            log_dir (str, optional): Directory for log files (default: 'logs').
            telegram_group (Optional[str]): Telegram group name or ID for sending notifications.

        Raises:
            ValueError: If 'telegram_group' is not provided.
        """
        super().__init__(server, login, key)
        super().login()
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)

        if not telegram_group:
            raise ValueError("Telegram group must be provided")

        self.bot_name: str = bot_name
        self.telegram_group: str = telegram_group
        self.logger: LoggerConfig = LoggerConfig(bot_name, log_dir)

        self.RAISE_NOT_CONNECTED: bool = False
        self.VERIFY_SSL_CERT = False

        self.telegram_token: str = self._get_telegram_token()
        self.telegram_bot: TelegramBot = (
            TelegramBot(token=self.telegram_token) if self.telegram_token else None
        )
        self.start_time: Optional[float] = None

    def _get_telegram_token(self) -> str:
        """
        Retrieves the Telegram bot token from the BotMaestro server.

        Returns:
            str: The Telegram bot token, or None if retrieval fails.

        Raises:
            Exception: If an error occurs during token retrieval.
        """
        try:
            token = super().get_credential(label="Telegram", key="token")
            logger.info("Telegram token retrieved successfully.")
            return token
        except Exception as e:
            logger.error(f"Failed to retrieve telegram token: {e}")
            raise e

    def _get_execution_time(self) -> str:
        """
        Computes the execution duration since the bot's start time.

        Returns:
            str: Execution time formatted as 'DD:HH:MM:SS'.
        """
        if self.start_time is None:
            return "Execution time not available"

        end_time = time.time()
        elapsed_seconds = int(end_time - self.start_time)

        days, remainder = divmod(elapsed_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        execution_time = f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"
        return execution_time

    def _get_resource_usage(self) -> str:
        """
        Retrieves current resource usage (CPU, RAM, and GPU).

        Returns:
            str: Formatted string with CPU, RAM, and GPU usage.
        """
        # CPU and RAM usage
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory()
        ram_percent = ram_usage.percent
        ram_used_mb = ram_usage.used / (1024 * 1024)

        # GPU usage (if GPU is available)
        gpu_stats = []
        gpus = GPUtil.getGPUs()
        if gpus:
            for gpu in gpus:
                gpu_stats.append(
                    f"GPU {gpu.id}: {gpu.name}, Load: {gpu.load * 100:.1f}%, "
                    f"Memory: {gpu.memoryUsed}MB/{gpu.memoryTotal}MB"
                )
            gpu_usage_str = "; ".join(gpu_stats)
        else:
            gpu_usage_str = "No GPU found."

        # Format the usage information
        usage_info = f"CPU Usage: {cpu_percent}%, RAM Usage: {ram_percent}% ({ram_used_mb:.1f} MB), GPU Usage: {gpu_usage_str}"
        return usage_info

    def _execute_bot_task(self) -> None:
        """
        Executes the main bot task logic.

        Note:
            This method should be extended with the actual task logic for your bot.
        """
        main()

    def run(self) -> None:
        """
        Starts the bot execution process.

        Logs:
            Information about the bot's execution start, completion, and errors.

        Raises:
            Exception: If an error occurs during execution.
        """
        try:
            self.start_time = time.time()
            logger.info("Bot execution started.")

            self._execute_bot_task()

            logger.info(f"{self.bot_name} Bot execution completed.")
            logger.info(f"Execution time: {self._get_execution_time()}")
            logger.info(
                f"Resource usage at end of execution: {self._get_resource_usage()}"
            )
            self.telegram_bot.send_message(
                f"{self.bot_name} Bot execution completed.", group=self.telegram_group
            )
            self.telegram_bot.upload_document(
                document=self.logger.log_path,
                group=self.telegram_group,
                caption=self.bot_name,
            )
        except Exception as e:
            self.telegram_bot.send_message(
                f"An error occurred during bot '{self.bot_name}' execution: {e}",
                self.telegram_group,
            )
            self.telegram_bot.upload_document(
                document=self.logger.log_path,
                group=self.telegram_group,
                caption=self.bot_name,
            )
            raise e
