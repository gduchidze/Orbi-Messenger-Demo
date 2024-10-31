import logging
from typing import Literal, Optional, Dict, List

import aiohttp


class MessengerClient:

    def __init__(self, access_token: str, page_id: str = 'me'):
        self._access_token = access_token
        self._page_id = page_id
        self.__url = f'https://graph.facebook.com/v21.0/{page_id}/messages'
        self._session = aiohttp.ClientSession()

    async def send_text_message(self, recipient_id: str, message: str, quick_replies: Optional[List[Dict]] = None):
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._access_token}"
        }

        message_data = {
            "text": message
        }

        if quick_replies:
            message_data["quick_replies"] = quick_replies

        payload = {
            "recipient": {"id": recipient_id},
            "message": message_data,
            "messaging_type": "RESPONSE"
        }

        logging.info(f"Sending message payload: {payload}")

        async with self._session.post(self.__url, headers=header, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                logging.info(f"Text message sent: {message}")
                return data
            else:
                error = await response.text()
                logging.error(f"Failed to send message: {error}")
                raise Exception(f"Failed to send text message with status {response.status}: {error}")

    async def send_action(self, recipient_id: str, action: Literal['mark_seen', 'typing_on', 'typing_off']):
        """
        Send a message to a user on Messenger.

        :param recipient_id: The recipient's Facebook ID
        :param message_text: The text content of the message
        :return: The response from the Facebook Graph API as a dictionary
        """
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": action
        }

        async with self._session.post(self.__url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                logging.info(f"Action sent: {action}")
                return data
            else:
                error = await response.text()
                logging.info(f"Failed to send action: {error}")
                raise Exception(f"Failed to send message with status {response.status}: {error}")

    async def send_attachment(self, sender_id: str, attachment_type: str, attachment_url: str) -> Optional[Dict]:
        """
        Sends an attachment to a user.

        Args:
            sender_id (str): The ID of the recipient.
            attachment_type (str): The type of the attachment (e.g., 'image', 'video', 'audio', 'file').
            attachment_url (str): The URL of the attachment to be sent.

        Returns:
            Optional[Dict]: The response from the server if the request is successful, otherwise None.

        Example:
            >>> send_attachment(sender_id, "image", "https://example.com/image.png")
        """
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "recipient": {
                "id": sender_id
            },
            "message": {
                "attachment": {
                    "type": attachment_type,
                    "payload": {
                        "url": attachment_url,
                        "is_reusable": True
                    }
                }
            }
        }

        async with self._session.post(self.__url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                logging.info(f"Attachment message sent")
                return data
            else:
                error = await response.text()
                logging.error(f"Failed to send message: {error}")
                raise Exception(f"Failed to send text message with status {response.status}: {error}")

    async def send_generic_template(self, recipient_id: str, elements: list):
        """
        Send a generic template message (carousel) to a user

        Args:
            recipient_id (str): The recipient's Facebook ID
            elements (list): List of carousel elements
        """
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": elements
                    }
                }
            }
        }

        async with self._session.post(self.__url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                logging.info("Generic template sent successfully")
                return data
            else:
                error = await response.text()
                logging.error(f"Failed to send generic template: {error}")
                raise Exception(f"Failed to send generic template with status {response.status}: {error}")