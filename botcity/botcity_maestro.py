import time
from typing import Dict, List, Optional, Tuple

import GPUtil
import psutil
from loguru import logger

from botcity.core.config import settings
from botcity.core.logger import LoggerConfig
from botcity.maestro import (
    AutomationTaskFinishStatus,
    BotExecution,
    BotMaestroSDK,
    ServerMessage,
)
from botcity.services.sharepoint import SharePointApi
from botcity.services.sql_connector import SQLDatabaseConnectorDict
from src.main import main


class BotRunnerMaestro:
    """
    Class to handle execution of a BotCity bot with integration to BotMaestro,
    SharePoint, and optional database logging.

    Responsibilities:
        - Initialize bot, logging, SharePoint, and BotMaestro SDK.
        - Execute main bot task with retries.
        - Capture and log execution time, CPU/RAM/GPU usage.
        - Upload logs to BotMaestro and SharePoint.
        - Insert execution details into SQL database if enabled.
    """

    def __init__(
        self,
        bot_maestro_sdk_raise: bool = False,
    ) -> None:
        """
        Initializes the BotRunnerMaestro with provided configuration.

        Args:
            bot_maestro_sdk_raise (bool, optional): Raise exceptions on BotMaestro connection issues (default False).

        Attributes:
            logger (LoggerConfig): Logger instance for the bot.
            maestro (BotMaestroSDK): Configured BotMaestro SDK instance.
            execution (BotExecution): Current task execution object.
            sharepoint (SharePointApi): SharePoint API instance.
            start_time (Optional[float]): Time when execution starts.
        """
        # initial config
        self.logger: LoggerConfig = LoggerConfig(settings.BOT_NAME)

        # maestro config
        self.bot_maestro_sdk_raise: bool = bot_maestro_sdk_raise
        self.maestro, self.execution = self._setup_maestro()

        if settings.USE_SHAREPOINT:
            # Sharepoint credentials
            self.sharepoint_credentials = self._get_credentials_sharepoint()

            self.sharepoint = SharePointApi(
                self.sharepoint_credentials.get("site_url", "")
                + settings.MAESTRO_SHAREPOINT_SITE_URL_SUFFIX,
                self.sharepoint_credentials.get("tenant", ""),
                self.sharepoint_credentials.get("client_id", ""),
                self.sharepoint_credentials.get("thumbprint", ""),
                settings.CERTIFICATE_FILE_PATH,
                settings.SHAREPOINT_DEPARTMENT_LOG_FOLDER,
            )

        # time config
        self.start_time: Optional[float] = None

    def _setup_maestro(self) -> Tuple[BotMaestroSDK, BotExecution]:
        """
        Sets up BotMaestro SDK and retrieves the current task execution.

        Returns:
            Tuple[BotMaestroSDK, BotExecution]: Configured SDK instance and current task execution.

        Raises:
            Exception: If SDK initialization or execution retrieval fails.
        """
        try:
            # Set up the BotMaestroSDK with custom configuration
            if self.bot_maestro_sdk_raise:
                BotMaestroSDK.RAISE_NOT_CONNECTED = True
            maestro = BotMaestroSDK.from_sys_args()
            execution: BotExecution = maestro.get_execution()

            # Log the task details
            logger.info(f"Task ID is: {execution.task_id}")
            logger.info(f"Task Parameters are: {execution.parameters}")

            return maestro, execution
        except Exception as e:
            logger.error(f"Failed to initialize BotMaestroSDK: {e}")
            raise e

    def _get_credentials_sharepoint(self) -> Dict[str, str]:
        """
        Retrieves the SharePoint credentials from BotMaestro.

        This method fetches the SharePoint site URL, username, and password from the BotMaestro

        Returns:
            dict: A dictionary containing the SharePoint credentials.
        """

        credentials = {
            "site_url": self.maestro.get_credential(
                label=settings.MAESTRO_SHAREPOINT_LABEL,
                key=settings.MAESTRO_SHAREPOINT_SITE_URL,
            ),
            "tenant": self.maestro.get_credential(
                label=settings.MAESTRO_SHAREPOINT_LABEL,
                key=settings.MAESTRO_SHAREPOINT_TENANT,
            ),
            "client_id": self.maestro.get_credential(
                label=settings.MAESTRO_SHAREPOINT_LABEL,
                key=settings.MAESTRO_SHAREPOINT_CLIENT_ID,
            ),
            "thumbprint": self.maestro.get_credential(
                label=settings.MAESTRO_SHAREPOINT_LABEL,
                key=settings.MAESTRO_SHAREPOINT_THUMBPRINT,
            ),
        }

        return credentials

    def _add_log_file_into_maestro(self) -> ServerMessage:
        """
        Uploads the bot's log file to BotMaestro as an artifact.

        Returns:
            ServerMessage: Response from BotMaestro server.

        Raises:
            Exception: If upload fails.
        """
        try:
            response: ServerMessage = self.maestro.post_artifact(
                task_id=int(self.execution.task_id),
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
        Calculates execution duration since bot start.

        Returns:
            str: Execution time formatted as 'DD:HH:MM:SS', or message if start_time is None.
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
        Retrieves current system resource usage.

        Returns:
            str: Formatted CPU, RAM, and GPU usage.
        """
        # CPU and RAM usage
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory()
        ram_percent = ram_usage.percent
        ram_used_mb = ram_usage.used / (1024 * 1024)

        # GPU usage (if GPU is available)
        gpu_stats = []
        gpus: List = GPUtil.getGPUs()
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
            "server": self.maestro.get_credential(
                label=settings.MAESTRO_SQL_LABEL, key=settings.MAESTRO_SQL_SERVER
            ),
            "database": self.maestro.get_credential(
                label=settings.MAESTRO_SQL_LABEL, key=settings.MAESTRO_SQL_DATABASE
            ),
            "username": self.maestro.get_credential(
                label=settings.MAESTRO_SQL_LABEL, key=settings.MAESTRO_SQL_USERNAME
            ),
            "password": self.maestro.get_credential(
                label=settings.MAESTRO_SQL_LABEL, key=settings.MAESTRO_SQL_PASSWORD
            ),
        }

        return credentials_database

    def _insert_database_log_execution(self, items_processed: int):
        """
        Inserts an execution record into the automation logs database.

        Fetches SQL credentials from BotMaestro, connects to the database, and
        inserts a record including bot name, developer, sector, stakeholder,
        recurrence, execution time, and items processed.

        Args:
            items_processed (int): Number of items processed in the bot task.

        Raises:
            Exception: If database connection or query execution fails.
        """
        time = self._get_execution_time()

        credentials = self._get_database_credentials()

        sql_connector = SQLDatabaseConnectorDict(
            server=credentials.get("server", ""),
            database=credentials.get("database", ""),
            use_windows_auth=False,
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
        Executes the bot task with retry logic, logging, and resource monitoring.

        - Attempts the task up to `settings.MAX_RETRIES`.
        - Logs execution time, CPU/RAM/GPU usage, and errors.
        - Uploads logs to SharePoint and BotMaestro.
        - Inserts execution details into SQL database if enabled.
        - Marks the task as SUCCESS or FAILED in BotMaestro.

        Raises:
            Exception: If bot execution fails after all retries.
        """
        attempts = 0
        while attempts <= settings.MAX_RETRIES:
            try:
                self.start_time = time.time()
                logger.info(f"Bot execution started. Attempt {attempts}")

                items_processed = self._execute_bot_task()

                execution_time = self._get_execution_time()
                resource_usage = self._get_resource_usage()

                logger.info(
                    f"{settings.BOT_NAME} Bot execution completed on attempt {attempts}."
                )
                logger.info(f"Execution time: {execution_time}")
                logger.info(f"Resource usage at end of execution: {resource_usage}")

                if settings.USE_SHAREPOINT:
                    self.sharepoint.upload_files([rf"{self.logger.log_path}"])

                if not settings.USE_DATABASE:
                    logger.info("Database logging is disabled.")
                elif items_processed is None or items_processed <= 0:
                    logger.warning("No items processed or task failed.")
                else:
                    logger.info(f"Items processed: {items_processed}")
                    self._insert_database_log_execution(items_processed)

                success_message = f"""Execution time: {execution_time}\nResource usage at end of execution: {resource_usage}"""

                self.maestro.finish_task(
                    self.execution.task_id,
                    AutomationTaskFinishStatus.SUCCESS,
                    success_message,
                )

                break

            except Exception as e:
                attempts += 1
                logger.error(
                    f"An error occurred during bot '{settings.BOT_NAME}' execution: {e}"
                )

                self.maestro.error(
                    int(self.execution.task_id), e, attachments=[self.logger.log_path]
                )

                self.maestro.finish_task(
                    self.execution.task_id,
                    AutomationTaskFinishStatus.FAILED,
                    f"An error occurred during bot execution: {e}",
                )

                if attempts > settings.MAX_RETRIES:
                    logger.error(
                        f"Max retries reached ({settings.MAX_RETRIES}). Giving up."
                    )
                    if settings.USE_SHAREPOINT:
                        self.sharepoint.upload_files([rf"{self.logger.log_path}"])
                    raise e

                else:
                    logger.info(f"Retrying bot execution (attempt {attempts})...")

            finally:
                self._add_log_file_into_maestro()
