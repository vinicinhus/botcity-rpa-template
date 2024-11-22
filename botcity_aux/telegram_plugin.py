from typing import Any, Dict, List, Optional, Union

from botcity.plugins.telegram import BotTelegramPlugin
from loguru import logger
from requests import Response


class TelegramBot:
    """
    Class to integrate BotCity functionalities with Telegram, allowing the sending,
    editing, uploading, and deleting of messages and documents in groups or chats.

    Attributes:
        telegram (BotTelegramPlugin): Instance of the BotTelegram plugin for Telegram integration.
    """

    def __init__(self, token: str) -> None:
        """
        Initializes the TelegramBot with a Telegram API token.

        Args:
            token (str): The Telegram bot's API token.
        """
        self.telegram = BotTelegramPlugin(token=token)
        logger.info(
            f"Telegram bot initialized with token: {token[:4]}..."
        )  # Mask part of the token for security

    def send_message(
        self, text: str, group: str, username: Optional[List[str]] = None
    ) -> Union[Response, Dict[str, Any]]:
        """
        Sends a message to a specified group or chat on Telegram.

        Args:
            text (str): The text of the message to be sent.
            group (str): The name or ID of the group to which the message will be sent.
            username (Optional[List[str]]): Optional list of usernames to mention in the message.

        Returns:
            Union[Response, Dict[str, Any]]: The response object from the request sent to Telegram.
        """
        try:
            response = self.telegram.send_message(
                text=text, group=group, username=username
            )
            logger.info(f"Sent message to group '{group}': {text}")
            return response
        except Exception as e:
            logger.error(f"Failed to send message to group '{group}': {e}")

    def edit_message(
        self, text: str, response: dict, username: Optional[List[str]] = None
    ) -> None:
        """
        Edits a previously sent message.

        Args:
            text (str): New text to update the message with.
            response (dict): The response object from the previously sent message.
            username (Optional[List[str]]): Optional list of usernames to mention in the updated message.

        Returns:
            None
        """
        try:
            self.telegram.edit_message(text=text, response=response, username=username)
            logger.info(f"Edited message to: {text}")
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")

    def upload_document(
        self, document: str, group: str, caption: str
    ) -> Union[Response, Dict[str, Any]]:
        """
        Uploads a document to a specified group or chat on Telegram with an optional caption.

        Args:
            document (str): Path to the document to be uploaded.
            group (str): The name or ID of the group to which the document will be uploaded.
            caption (str): The caption to accompany the document.

        Returns:
            Union[Response, Dict[str, Any]]: The response object from the request sent to Telegram.
        """
        try:
            response = self.telegram.upload_document(
                document=document, group=group, caption=caption
            )
            logger.info(
                f"Uploaded document '{document}' to group '{group}' with caption: {caption}"
            )
            return response
        except Exception as e:
            logger.error(
                f"Failed to upload document '{document}' to group '{group}': {e}"
            )

    def delete_message(self, response: Union[Response, Dict[str, Any]]) -> None:
        """
        Deletes a previously sent message or document.

        Args:
            response (Union[Response, Dict[Any, str]]]): The response object from the previously sent message or document.

        Returns:
            None
        """
        try:
            self.telegram.delete_message(response=response)
            logger.info("Deleted message or document.")
        except Exception as e:
            logger.error(f"Failed to delete message or document: {e}")
