"""Configuration lue depuis les variables d'environnement (fichier .env en local)."""

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GEMMW_", env_file=".env", extra="ignore")

    env: str = "dev"
    db_path: Path = Path("data/gemmw.db")
    user_agent: str = "gemmw-data/0.1 (+https://github.com/BiraneWANE/gemmw-data)"
    delai_entre_requetes_s: float = 2.0
    # Sel du hachage des emails d'acheteuses. À définir dans .env, jamais dans le dépôt.
    sel_acheteuses: str = ""
    # Collecte Etsy (API officielle). Sans clé, la collecte Etsy est sautée.
    etsy_api_key: str = Field(
        "", validation_alias=AliasChoices("GEMMW_ETSY_API_KEY", "ETSY_API_KEY")
    )
    etsy_recherches: tuple[str, ...] = (
        "livret activités enfant pdf",
        "imagier enfant pdf",
        "cahier activités maternelle pdf",
    )
    # Alerte de prix sur Telegram (facultatif).
    telegram_bot_token: str = Field(
        "", validation_alias=AliasChoices("GEMMW_TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")
    )
    telegram_chat_id: str = Field(
        "", validation_alias=AliasChoices("GEMMW_TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_ID")
    )


settings = Settings()
