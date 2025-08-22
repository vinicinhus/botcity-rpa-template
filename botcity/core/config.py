from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from botcity.enums.department import DepartmentFolderNumber, DepartmentName
from botcity.enums.recurrence import Recurrence


class Settings(BaseSettings):
    """
    Centralized application configuration settings.

    This class aggregates all configuration areas (bot, maestro, cli, database,
    sharepoint, simplesclique) into a single BaseSettings object. It keeps the
    environment variables flat (no nested __ required) while remaining modular
    and organized with prefixes.
    """

    # =============================
    # Bot settings
    # =============================
    BOT_NAME: str = Field("Bot name", description="Bot name")
    RECURRENCE: Recurrence = Field(
        Recurrence.DIARIA, description="Automation recurrence"
    )
    DEVELOPER: str = Field("Developer name", description="Developer name")
    STAKEHOLDER: str = Field("Business stakeholder", description="Business stakeholder")
    SECTOR: DepartmentName = Field(
        DepartmentName.ADM_GRUPOS, description="Responsible department"
    )
    MAX_RETRIES: int = Field(0, description="Maximum retries")

    # =============================
    # Maestro settings
    # =============================
    SERVER_MAESTRO: Optional[str] = None
    LOGIN_MAESTRO: Optional[str] = None
    KEY_MAESTRO: Optional[str] = None

    # =============================
    # CLI settings
    # =============================
    DESCRIPTION: str = "Bot Runner Settings"
    HELP_MESSAGE: str = (
        "Define the execution environment: 'maestro' or 'local' (default: 'maestro')"
    )
    CHOICE_MAESTRO: str = "maestro"
    CHOICE_LOCAL: str = "local"

    # =============================
    # Database production settings
    # =============================
    USE_DATABASE: bool = True
    SQL_QUERY_PATH: str = r"botcity\sql\query\log_insert.sql"
    MAESTRO_SQL_LABEL: str = "Your Maestro SQL Label Credential"
    MAESTRO_SQL_SERVER: str = "Your Maestro SQL Server Credential"
    MAESTRO_SQL_DATABASE: str = "Your Maestro SQL Database Credential"
    MAESTRO_SQL_USERNAME: str = "Your Maestro SQL Username Credential"
    MAESTRO_SQL_PASSWORD: str = "Your Maestro SQL Password Credential"

    # =============================
    # Database approval settings
    # =============================
    MAESTRO_SQL_LABEL_HOMOL: str = "Your Maestro SQL Label Homol Credential"
    MAESTRO_SQL_SERVER_HOMOL: str = "Your Maestro SQL Server Homol Credential"
    MAESTRO_SQL_DATABASE_HOMOL: str = "Your Maestro SQL Database Homol Credential"

    # =============================
    # SharePoint settings
    # =============================
    USE_SHAREPOINT: bool = True
    MAESTRO_SHAREPOINT_LABEL: str = "Your Maestro Sharepoint Label Credential"
    MAESTRO_SHAREPOINT_SITE_URL: str = "Your Maestro Sharepoint Site URL Credential"
    MAESTRO_SHAREPOINT_TENANT: str = "Your Maestro Sharepoint Tenant Credential"
    MAESTRO_SHAREPOINT_CLIENT_ID: str = "Your Maestro Sharepoint Client ID Credential"
    MAESTRO_SHAREPOINT_THUMBPRINT: str = "Your Maestro Sharepoint Thumbprint Credential"
    CERTIFICATE_FILE_PATH: str = r"botcity\cert\cert.pem"

    MAESTRO_SHAREPOINT_SITE_URL_SUFFIX: str = "TIeDesenvolvimento"
    SHAREPOINT_ROOT_LOG_FOLDER: str = r"Documentos Compartilhados/Automações/Logs"
    SHAREPOINT_DEPARTMENT_LOG_FOLDER: DepartmentFolderNumber = Field(
        DepartmentFolderNumber.ADM_GRUPOS, description="Department-specific log folder"
    )

    # =============================
    # Pydantic Settings
    # =============================
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, env_file_encoding="utf-8"
    )


# Global settings instance
settings = Settings()
