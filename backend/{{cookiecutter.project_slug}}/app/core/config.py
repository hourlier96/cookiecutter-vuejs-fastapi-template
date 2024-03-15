import logging
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "local"
    LOG_LEVEL: int = logging.INFO
    LOG_NAME: str = "{{ cookiecutter.project_slug }}"
    PROJECT_NAME: str = "{{ cookiecutter.project_name }}"

    API_PREFIX: str = "/api"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    SQLALCHEMY_DATABASE_URI: str = (
        "postgresql://postgres:postgres@localhost:5434/{{cookiecutter.project_slug}}_db"
    )
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    GITHUB_ACCESS_TOKEN: Optional[str] = None
    GCLOUD_PROJECT_ID: Optional[str] = "{{cookiecutter.gcloud_project}}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
