import os
import re
from typing import List

from loguru import logger
from office365.sharepoint.client_context import ClientContext, UserCredential


class SharePointApi:
    """
    A wrapper for interacting with SharePoint Online to upload documents.

    Attributes:
        ctx (ClientContext): The SharePoint client context authenticated with user credentials.
    """

    FOLDER_URL = rf"Shared Documents/your_path"

    def __init__(
        self, site_url: str, username: str, password: str, folder_log: str, botname: str
    ) -> None:
        """
        Initializes the SharePointApi with credentials and connects to the given SharePoint site.

        Args:
            site_url (str): The URL of the SharePoint site.
            username (str): The SharePoint account username.
            password (str): The SharePoint account password.
        """
        self.site_url = site_url
        self.username = username
        self.password = password
        self.folder_log = folder_log
        self.botname = botname
        self.ctx = ClientContext(site_url).with_credentials(
            credentials=UserCredential(username, password)
        )

    def list_folders_by_number(self) -> List:
        """
        Lists folders that start with the value defined in `folder_log`.

        Returns:
            list: A list containing the matching folder name(s), or an empty list if none are found.

        Raises:
            Exception: If any error occurs during the operation.
        """
        try:
            folder = self.ctx.web.get_folder_by_server_relative_url(self.FOLDER_URL)
            folders = folder.folders
            self.ctx.load(folders)
            self.ctx.execute_query()

            folder_names = [f.name for f in folders]

            regex = rf"^{self.folder_log}\s+-"
            matching_folders = [name for name in folder_names if re.match(regex, name)]

            return matching_folders

        except Exception as e:
            logger.error(f"Error while listing folders in '{self.FOLDER_URL}': {e}")
            raise

    def _list_files_in_folder(self, folder_name: str) -> List[str]:
        """
        Lists all files inside the specified subfolder.

        Args:
            folder_name (str): The name of the folder (e.g., '10 - Logs').

        Returns:
            List[str]: A list of file names inside the folder.
        """
        try:
            folder_path = f"{self.FOLDER_URL}/{folder_name[0]}"
            folder = self.ctx.web.get_folder_by_server_relative_url(folder_path)
            files = folder.files
            self.ctx.load(files)
            self.ctx.execute_query()

            return [f.name for f in files]

        except Exception as e:
            logger.error(f"Error while listing files in folder '{folder_name}': {e}")
            raise

    def upload_files(self, file_paths: List[str]) -> None:
        """
        Uploads files to a SharePoint subfolder. If a file with the same name exists,
        it appends a counter to the filename. If the subfolder with the bot name doesn't exist,
        it is created automatically.

        Args:
            file_paths (List[str]): List of local file paths to upload.

        Raises:
            Exception: If the upload process fails.
        """
        try:
            matching_folders = self.list_folders_by_number()
            if not matching_folders:
                raise Exception(f"No folder found with prefix '{self.folder_log}'.")

            main_folder_name = matching_folders[0]
            main_folder_path = f"{self.FOLDER_URL}/{main_folder_name}"

            main_folder = self.ctx.web.get_folder_by_server_relative_url(
                main_folder_path
            )
            subfolders = main_folder.folders
            self.ctx.load(subfolders)
            self.ctx.execute_query()

            subfolder_names = [sf.name for sf in subfolders]

            if self.botname in subfolder_names:
                logger.info(
                    f"Subfolder '{self.botname}' already exists inside '{main_folder_name}'."
                )
            else:
                subfolder_url = f"{main_folder_path}/{self.botname}"
                main_folder.folders.add(self.botname)
                self.ctx.execute_query()
                logger.info(
                    f"Subfolder '{self.botname}' created inside '{main_folder_name}'."
                )

            target_folder_path = f"{main_folder_path}/{self.botname}"
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
