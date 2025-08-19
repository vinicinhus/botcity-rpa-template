from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from enums.department import DepartmentFolderNumber, DepartmentName
from enums.recurrence import Recurrence


class Settings(BaseSettings):
    # =============================
    # Bot settings
    # =============================
    BOT_NAME: str = "Bot Name"
    RECURRENCE: str = (
        Recurrence.MENSAL
    )  # Change this to whatever recurrence the automation is being builded for
    DEVELOPER: str = "Developer Name"
    STAKEHOLDER: str = "Stakeholder Name"
    SECTOR: str = (
        DepartmentName.OUVIDORIA
    )  # Change this to whatever department the automation is being builded for
    MAX_RETRIES: int = 0

    # =============================
    # Bot Local settings
    # =============================
    SERVER_MAESTRO: Optional[str] = None
    LOGIN_MAESTRO: Optional[str] = None
    KEY_MAESTRO: Optional[str] = None

    # =============================
    # Command-line settings
    # =============================
    DESCRIPTION: str = "Bot Runner Settings"
    HELP_MESSAGE: str = (
        "Defines the execution environment: 'maestro' or 'local' (default: 'maestro')"
    )
    CHOICE_MAESTRO: str = "maestro"
    CHOICE_LOCAL: str = "local"

    # =============================
    # Database settings
    # =============================
    USE_DATABASE: bool = True
    SQL_QUERY_PATH: str = r"queries\Insert Data into Database LOG.sql"
    MAESTRO_SQL_LABEL: str = "Your Maestro SQL Label Credential"
    MAESTRO_SQL_SERVER: str = "Your Maestro SQL Server Credential"
    MAESTRO_SQL_DATABASE: str = "Your Maestro SQL Database Credential"
    MAESTRO_SQL_USERNAME: str = "Your Maestro SQL Username Credential"
    MAESTRO_SQL_PASSWORD: str = "Your Maestro SQL Password Credential"

    # =============================
    # Sharepoint settings
    # =============================
    USE_SHAREPOINT: bool = True
    MAESTRO_SHAREPOINT_LABEL: str = "Your Maestro Sharepoint Label Credential"
    MAESTRO_SHAREPOINT_SITE_URL: str = "Your Maestro Sharepoint Site URL Credential"
    MAESTRO_SHAREPOINT_TENANT: str = "Your Maestro Sharepoint Tenant Credential"
    MAESTRO_SHAREPOINT_CLIENT_ID: str = "Your Maestro Sharepoint Client ID Credential"
    MAESTRO_SHAREPOINT_THUMBPRINT: str = "Your Maestro Sharepoint Thumbprint Credential"
    CERTIFICATE_FILE_PATH: str = r"cert\cert.pem"

    MAESTRO_SHAREPOINT_SITE_URL_SUFFIX: str = "TIeDesenvolvimento"
    SHAREPOINT_ROOT_LOG_FOLDER: str = r"Documentos Compartilhados/Automações/Logs"
    SHAREPOINT_DEPARTMENT_LOG_FOLDER: str = (
        DepartmentFolderNumber.ADM_GRUPOS
    )  # Change this to whatever department the automation is being builded for

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, env_file_encoding="utf-8"
    )

    # In the bellow continue with your settings for the bot


settings = Settings()
