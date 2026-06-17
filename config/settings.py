from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = (
        "AI Clinical Synopsis Service"
    )

    APP_VERSION: str = "1.0.0"

    API_BASE_URL: str

    OLLAMA_URL: str

    OLLAMA_MODEL: str

    LOG_LEVEL: str = "INFO"

    class Config:

        env_file = ".env"


settings = Settings()