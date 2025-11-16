"""Konfiguration für das Freizeit-Kassen-System"""
import secrets
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, ValidationError
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Anwendungs-Einstellungen mit Validierung

    Alle Einstellungen können via Umgebungsvariablen (.env) überschrieben werden.
    """

    # App-Grundeinstellungen
    app_name: str = Field(
        default="Freizeit-Kassen-System",
        description="Name der Anwendung"
    )
    app_version: str = Field(
        default="0.1.0",
        description="Version der Anwendung"
    )
    debug: bool = Field(
        default=False,
        description="Debug-Modus (nur für Entwicklung)"
    )

    # Datenbank
    database_url: str = Field(
        default="sqlite:///./freizeit_kassen.db",
        description="Datenbank-URL (SQLite oder PostgreSQL)"
    )

    # Pfade
    base_dir: Path = Path(__file__).parent.parent
    templates_dir: Path = base_dir / "app" / "templates"
    static_dir: Path = base_dir / "app" / "static"
    rulesets_dir: Path = base_dir / "rulesets"

    # Server
    host: str = Field(
        default="0.0.0.0",
        description="Server-Host (0.0.0.0 für alle Interfaces, 127.0.0.1 nur lokal)"
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server-Port (1-65535)"
    )

    # Security
    # Wird automatisch generiert, falls nicht in .env gesetzt
    # WICHTIG: In Production MUSS SECRET_KEY in .env gesetzt werden!
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        min_length=32,
        description="Secret key für Session-Verschlüsselung (min. 32 Zeichen)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignoriere unbekannte Env-Vars
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validiert die Datenbank-URL"""
        if not v:
            raise ValueError("DATABASE_URL darf nicht leer sein")

        # Erlaube SQLite und PostgreSQL
        if not (v.startswith("sqlite://") or v.startswith("postgresql://")):
            raise ValueError(
                "DATABASE_URL muss mit 'sqlite://' oder 'postgresql://' beginnen"
            )

        return v

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validiert den Server-Host"""
        if not v:
            raise ValueError("HOST darf nicht leer sein")

        # Warne bei öffentlichem Zugriff (für lokale Anwendung)
        if v in ["0.0.0.0", "::"]:
            logger.warning(
                "⚠️  Server ist auf ALLEN Netzwerk-Interfaces erreichbar! "
                "Für lokalen Betrieb HOST=127.0.0.1 verwenden."
            )

        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validiert den Secret Key"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY muss mindestens 32 Zeichen lang sein")

        return v

    def is_secret_key_from_env(self) -> bool:
        """Prüft ob SECRET_KEY aus Umgebungsvariable gesetzt wurde"""
        return bool(os.getenv("SECRET_KEY"))

    def validate_paths(self) -> None:
        """
        Validiert dass alle erforderlichen Pfade existieren

        Wird beim App-Start aufgerufen
        """
        required_paths = {
            "Templates": self.templates_dir,
            "Static Files": self.static_dir,
        }

        for name, path in required_paths.items():
            if not path.exists():
                raise FileNotFoundError(
                    f"{name} Verzeichnis nicht gefunden: {path}"
                )

        # Rulesets-Verzeichnis erstellen falls nicht vorhanden
        self.rulesets_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
