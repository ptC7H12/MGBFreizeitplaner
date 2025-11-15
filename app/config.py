"""Konfiguration für das Freizeit-Kassen-System"""
import secrets
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Anwendungs-Einstellungen"""

    # App-Grundeinstellungen
    app_name: str = "Freizeit-Kassen-System"
    app_version: str = "0.1.0"
    debug: bool = False  # In Entwicklung: DEBUG=true in .env setzen

    # Datenbank
    database_url: str = "sqlite:///./freizeit_kassen.db"

    # Pfade
    base_dir: Path = Path(__file__).parent.parent
    templates_dir: Path = base_dir / "app" / "templates"
    static_dir: Path = base_dir / "app" / "static"
    rulesets_dir: Path = base_dir / "rulesets"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Security
    # Wird automatisch generiert, falls nicht in .env gesetzt
    # WICHTIG: In Production MUSS SECRET_KEY in .env gesetzt werden!
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for session encryption. Set via SECRET_KEY environment variable in production."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    def is_secret_key_from_env(self) -> bool:
        """Prüft ob SECRET_KEY aus Umgebungsvariable gesetzt wurde"""
        return bool(os.getenv("SECRET_KEY"))


settings = Settings()
