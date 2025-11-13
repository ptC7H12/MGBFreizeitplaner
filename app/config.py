"""Konfiguration für das Freizeit-Kassen-System"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Anwendungs-Einstellungen"""

    # App-Grundeinstellungen
    app_name: str = "Freizeit-Kassen-System"
    app_version: str = "0.1.0"
    debug: bool = True

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
