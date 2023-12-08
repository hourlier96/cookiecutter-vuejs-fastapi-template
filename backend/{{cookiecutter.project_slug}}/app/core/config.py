import logging
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "local"
    LOG_LEVEL: int = logging.INFO
    LOG_NAME: str = "{{ cookiecutter.project_slug }}"
    PROJECT_NAME: str = "{{ cookiecutter.project_name }}"

    API_PREFIX: str = "/api"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    # SQLALCHEMY_DATABASE_URI: str = "postgresql://postgres:postgres@localhost:5432/minseed"
    # PROJECT_ID: Optional[str] = None
    # PROJECT_NUMBER: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
