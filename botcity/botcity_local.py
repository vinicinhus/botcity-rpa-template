import time
import warnings
from typing import Optional

import GPUtil
import psutil
from loguru import logger
from urllib3.exceptions import InsecureRequestWarning

from botcity.maestro import BotMaestroSDK
from core.config import settings
from core.logging import LoggerConfig
from core.sharepoint_wrapper import SharePointApi
from core.sql_database_connector import SQLDatabaseConnectorDict
from src.main import main


class BotRunnerLocal(BotMaestroSDK):
    def __init__(
        self,
        server: str,
        login: str,
        key: str,
        log_dir: str = "logs",
    ) -> None:
        """
        Initializes the BotRunnerLocal instance with the specified configuration.

        Args:
            server (str): BotMaestro server URL.
            login (str): BotMaestro login credential.
            key (str): BotMaestro authentication key.
            log_dir (str, optional): Directory for log files (default: 'logs').

        """
        # BotMaestroSDK config
        super().__init__(server, login, key)
        super().login()
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)

        # initial config
        self.logger: LoggerConfig = LoggerConfig(log_dir)

        # Sharepoint credentials
        self.sharepoint_credentials = self._get_credentials_sharepoint()

        self.sharepoint = SharePointApi(
            self.sharepoint_credentials.get("site_url", "")
            + settings.MAESTRO_SHAREPOINT_SITE_URL_SUFFIX,
            self.sharepoint_credentials.get("username", ""),
            self.sharepoint_credentials.get("password", ""),
            settings.SHAREPOINT_DEPARTMENT_LOG_FOLDER,
        )

        # maestro config
        self.RAISE_NOT_CONNECTED: bool = False
        self.VERIFY_SSL_CERT = False

        # time config
        self.start_time: Optional[float] = None

    def _get_credentials_sharepoint(self) -> dict:
        """
        Retrieves the SharePoint credentials from BotMaestro.

        This method fetches the SharePoint site URL, username, and password from the BotMaestro

        Returns:
            dict: A dictionary containing the SharePoint credentials.
        """

        credentials = {
            "site_url": super().get_credential(
                label=settings.MAESTRO_SHAREPOINT_LABEL,
                key=settings.MAESTRO_SHAREPOINT_SITE_URL,
            ),
            "username": super().get_credential(
                label=settings.MAESTRO_SHAREPOINT_LABEL,
                key=settings.MAESTRO_SHAREPOINT_USERNAME,
            ),
            "password": super().get_credential(
                label=settings.MAESTRO_SHAREPOINT_LABEL,
                key=settings.MAESTRO_SHAREPOINT_PASSWORD,
            ),
        }

        return credentials

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

    def _get_database_credentials(self) -> dict:
        """
        Retrieves the database credentials from BotMaestro.

        Returns:
            dict: A dictionary containing the database credentials.
        """
        credentials_database = {
            "server": super().get_credential(
                label=settings.MAESTRO_SQL_LABEL, key=settings.MAESTRO_SQL_SERVER
            ),
            "database": super().get_credential(
                label=settings.MAESTRO_SQL_LABEL, key=settings.MAESTRO_SQL_DATABASE
            ),
            "username": super().get_credential(
                label=settings.MAESTRO_SQL_LABEL, key=settings.MAESTRO_SQL_USERNAME
            ),
            "password": super().get_credential(
                label=settings.MAESTRO_SQL_LABEL, key=settings.MAESTRO_SQL_PASSWORD
            ),
        }

        return credentials_database

    def _insert_database_log_execution(self, items_processed: int):
        """
        Inserts an execution log entry into the automation logs database.

        This function retrieves the necessary SQL credentials from BotMaestro, establishes a
        connection with the production SQL database, and inserts a log record with information
        about the bot execution (such as bot name, developer, sector, stakeholder, recurrence, and execution time).

        Raises:
            Exception: If there is an error connecting to the database or executing the query.
        """
        time = self._get_execution_time()

        credentials = self._get_database_credentials()

        sql_connector = SQLDatabaseConnectorDict(
            server=credentials.get("server", ""),
            database=credentials.get("database", ""),
            use_windows_auth=True,
            username=credentials.get("username"),
            password=credentials.get("password"),
        )

        sql_connector.connect()

        params = [
            settings.BOT_NAME,
            settings.DEVELOPER,
            settings.SECTOR,
            settings.STAKEHOLDER,
            settings.RECURRENCE,
            time,
            items_processed,
        ]

        query = settings.SQL_QUERY_PATH

        sql_connector.execute_query_from_file(query, params)

        sql_connector.disconnect()

    def _execute_bot_task(self) -> Optional[int]:
        """
        Executes the bot task and returns the number of processed items.

        This method prepares the credentials, calls the `main` function to execute
        the bot's main workflow, and returns the number of processed items. If the
        task fails or produces no result, `None` can be returned.

        Returns:
            Optional[int]:
                The number of items processed if successful, otherwise `None`.

        Example:
            >>> result = self._execute_bot_task()
            >>> if result:
            ...     print(f"Processed {result} items")
            ... else:
            ...     print("No items processed.")
        """
        credentials = {"example1": "credential_1", "example2": "credential_2"}

        items_processed = main(credentials)
        return items_processed

    def run(self) -> None:
        """
        Starts the bot execution process with retry logic and logs the results.

        This method attempts to execute the bot task up to the maximum number of retries
        defined by `self.max_retries`. For each attempt, it logs the start time, execution time,
        resource usage, and final status.

        Logs:
            - Execution start and completion per attempt.
            - Execution time and system resource usage.
            - Any errors encountered during execution.

        Raises:
            Exception: If the bot fails to execute successfully after all retry attempts.
        """
        attempts = 0
        while attempts <= settings.MAX_RETRIES:
            try:
                self.start_time = time.time()
                logger.info(f"Bot execution started. Attempt {attempts}")

                items_processed = self._execute_bot_task()

                logger.info(
                    f"{settings.BOT_NAME} Bot execution completed on attempt {attempts}."
                )
                logger.info(f"Execution time: {self._get_execution_time()}")
                logger.info(
                    f"Resource usage at end of execution: {self._get_resource_usage()}"
                )
                self.sharepoint.list_folders_by_number()
                self.sharepoint.upload_files([rf"{self.logger.log_path}"])
                if not settings.USE_DATABASE:
                    logger.info("Database logging is disabled.")
                elif items_processed is None or items_processed <= 0:
                    logger.warning("No items processed or task failed.")
                else:
                    logger.info(f"Items processed: {items_processed}")
                    self._insert_database_log_execution(items_processed)

                break

            except Exception as e:
                attempts += 1
                logger.error(
                    f"An error occurred during bot '{settings.BOT_NAME}' attempt: {attempts}, execution: {e}"
                )

                if attempts > settings.MAX_RETRIES:
                    logger.error(
                        f"Max retries reached ({settings.MAX_RETRIES}). Giving up."
                    )
                    raise e

                else:
                    logger.info(f"Retrying bot execution (attempt {attempts})...")
