"""Application settings loaded from the .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "CFA Candidate-to-Member Onboarding POC"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_enabled: bool = True

    database_url: str = "postgresql+psycopg://onboarding:onboarding@localhost:5432/onboarding"

    data_dir: str = "./data/mock"
    mcp_config_path: str = "./mcp.config.json"
    a2a_base_url: str = "http://localhost:8000"

    @property
    def data_path(self) -> Path:
        path = Path(self.data_dir)
        return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()

    @property
    def mcp_config_file(self) -> Path:
        path = Path(self.mcp_config_path)
        return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()

    @property
    def use_llm(self) -> bool:
        return self.llm_enabled and bool(self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
