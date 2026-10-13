"""Configuration lue depuis les variables d'environnement (fichier .env en local)."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GEMMW_", env_file=".env", extra="ignore")

    env: str = "dev"
    db_path: Path = Path("data/gemmw.db")
    user_agent: str = "gemmw-data/0.1 (+https://github.com/BiraneWANE/gemmw-data)"
    delai_entre_requetes_s: float = 2.0


settings = Settings()
