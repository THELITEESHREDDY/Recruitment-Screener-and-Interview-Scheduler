from pydantic_settings import BaseSettings,SettingsConfigDict
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):

    GROQ_API_AGENTS_PROVIDER : str

    model_config=SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()