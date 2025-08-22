import os
import re
from typing import List

from loguru import logger
from office365.sharepoint.client_context import ClientContext

from core.config import settings


class SharePointApi:
    """
    A wrapper class to interact with SharePoint Online for managing folders and uploading files,
    now using app certificate authentication.
    """

    def __init__(
        self,
        site_url: str,
        tenant: str,
        client_id: str,
        thumbprint: str,
        cert_path: str,
        folder_log: str,
    ) -> None:
        """
        Initializes the SharePoint API client using app certificate authentication.

        Args:
            site_url (str): URL of the SharePoint site.
            tenant (str): Azure AD tenant (ex: "minhaempresa.onmicrosoft.com" ou tenant ID).
            client_id (str): Application (client) ID registered in Azure AD.
            thumbprint (str): Certificate thumbprint.
            cert_path (str): Path to the certificate PEM file.
            folder_log (str): Prefix to identify specific folders.
        """
        self.site_url = site_url
        self.tenant = tenant
        self.client_id = client_id
        self.thumbprint = thumbprint
        self.cert_path = cert_path
        self.folder_log = folder_log

        cert_credentials = {
            "tenant": self.tenant,
            "client_id": self.client_id,
            "thumbprint": self.thumbprint,
            "cert_path": self.cert_path,
        }

        self.ctx = ClientContext(site_url).with_client_certificate(
            **cert_credentials, scopes=None
        )

    def list_folders_by_number(self) -> List[str]:
        try:
            folder = self.ctx.web.get_folder_by_server_relative_url(
                settings.SHAREPOINT_ROOT_LOG_FOLDER
            )
            folders = folder.folders
            self.ctx.load(folders)
            self.ctx.execute_query()

            folder_names = [f.name for f in folders]

            regex = rf"^{self.folder_log}\s+-"
            matching_folders = [
                name
                for name in folder_names
                if name is not None and re.match(regex, name)
            ]

            return matching_folders

        except Exception as e:
            logger.error(
                f"Error while listing folders in '{settings.SHAREPOINT_ROOT_LOG_FOLDER}': {e}"
            )
            raise

    def _list_files_in_folder(self, folder_name: str) -> List[str]:
        try:
            folder_path = f"{settings.SHAREPOINT_ROOT_LOG_FOLDER}/{folder_name[0]}"
            folder = self.ctx.web.get_folder_by_server_relative_url(folder_path)
            files = folder.files
            self.ctx.load(files)
            self.ctx.execute_query()

            return [f.name for f in files if f.name is not None]

        except Exception as e:
            logger.error(f"Error while listing files in folder '{folder_name}': {e}")
            raise

    def upload_files(self, file_paths: List[str]) -> None:
        try:
            matching_folders = self.list_folders_by_number()
            if not matching_folders:
                raise Exception(f"No folder found with prefix '{self.folder_log}'.")

            main_folder_name = matching_folders[0]
            main_folder_path = (
                f"{settings.SHAREPOINT_ROOT_LOG_FOLDER}/{main_folder_name}"
            )

            main_folder = self.ctx.web.get_folder_by_server_relative_url(
                main_folder_path
            )
            subfolders = main_folder.folders
            self.ctx.load(subfolders)
            self.ctx.execute_query()

            subfolder_names = [sf.name for sf in subfolders]

            if settings.BOT_NAME in subfolder_names:
                logger.info(
                    f"Subfolder '{settings.BOT_NAME}' already exists inside '{main_folder_name}'."
                )
            else:
                main_folder.folders.add(settings.BOT_NAME)
                self.ctx.execute_query()
                logger.info(
                    f"Subfolder '{settings.BOT_NAME}' created inside '{main_folder_name}'."
                )

            target_folder_path = f"{main_folder_path}/{settings.BOT_NAME}"
            target_folder = self.ctx.web.get_folder_by_server_relative_url(
                target_folder_path
            )

            files = target_folder.files
            self.ctx.load(files)
            self.ctx.execute_query()
            existing_files = [f.name for f in files]

            for file_path in file_paths:
                base_name = os.path.basename(file_path)
                name, ext = os.path.splitext(base_name)
                final_name = base_name
                counter = 1

                while final_name in existing_files:
                    final_name = f"{name}({counter}){ext}"
                    counter += 1

                with open(file_path, "rb") as f:
                    file_content = f.read()
                    target_folder.upload_file(final_name, file_content)
                    self.ctx.execute_query()
                    logger.info(
                        f"File '{final_name}' successfully uploaded to '{target_folder_path}'."
                    )

        except Exception as e:
            logger.error(f"Error while uploading files to the bot's subfolder: {e}")
            raise
