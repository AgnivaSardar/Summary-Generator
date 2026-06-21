from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = (
        "AI Clinical Synopsis Service"
    )

    APP_VERSION: str = "1.0.0"

    API_BASE_URL: str

    DEFAULT_COMPANY_ID: str = "00262"

    SYNOPSIS_UPDATE_URL: Optional[str] = None

    SYNOPSIS_UPDATE_TIMEOUT_SECONDS: int = 30

    OLLAMA_URL: str

    OLLAMA_MODEL: str

    LOG_LEVEL: str = "INFO"

    GEMINI_API_KEY: Optional[str] = None

    GEMINI_MODEL: str = "gemini-3.1-flash-lite"

    class Config:

        env_file = ".env"


settings = Settings()
