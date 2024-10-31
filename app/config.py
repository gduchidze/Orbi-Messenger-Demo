import logging
from functools import lru_cache

from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


class Settings(BaseSettings):
    qdrant_endpoint: str
    qdrant_api_key: str

    voyage_api_key: str
    voyage_default_model: str = "voyage-multilingual-2"

    messenger_verify_token: str
    messenger_page_access_token: str

    ailab_api_key: str
    ailab_base_url: str
    ailab_default_model: str = "tbilisi-ai-lab-2.0"

    openai_api_key: str


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
