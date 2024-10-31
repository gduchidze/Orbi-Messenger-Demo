from .messenger_client import MessengerClient as MessengerClient
from app.config import settings

#
messenger_client = MessengerClient(access_token=settings.messenger_page_access_token)
