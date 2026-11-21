"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    data_root: Path = Path("data")
    raw_dir: Path = Path("data/raw")
    bronze_dir: Path = Path("data/bronze")
    silver_dir: Path = Path("data/silver")
    gold_dir: Path = Path("data/gold")

    log_level: str = "INFO"

    @property
    def raw_hm(self) -> Path:
        return self.raw_dir / "hm"

    @property
    def raw_uci(self) -> Path:
        return self.raw_dir / "uci"


settings = Settings()
