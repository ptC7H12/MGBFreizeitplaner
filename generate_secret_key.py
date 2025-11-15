#!/usr/bin/env python3
"""
Helper-Script zum Generieren eines sicheren Secret Keys für die Session-Verschlüsselung.

Verwendung:
    python generate_secret_key.py

Das Script generiert einen neuen Secret Key und zeigt Anweisungen zur Verwendung.
"""
import secrets
import os
from pathlib import Path


def generate_secret_key() -> str:
    """Generiert einen sicheren Secret Key"""
    return secrets.token_urlsafe(32)


def update_env_file(secret_key: str):
    """Fügt den Secret Key zur .env Datei hinzu oder aktualisiert ihn"""
    env_file = Path(".env")
    env_example_file = Path(".env.example")

    # Wenn .env nicht existiert, von .env.example kopieren
    if not env_file.exists() and env_example_file.exists():
        print(f"📄 Erstelle .env aus .env.example...")
        env_file.write_text(env_example_file.read_text())

    if env_file.exists():
        # .env Datei lesen
        lines = env_file.read_text().splitlines()

        # Prüfen ob SECRET_KEY bereits existiert
        secret_key_found = False
        new_lines = []

        for line in lines:
            if line.startswith("SECRET_KEY="):
                # Bestehenden Key ersetzen
                new_lines.append(f"SECRET_KEY={secret_key}")
                secret_key_found = True
                print(f"✅ SECRET_KEY in .env aktualisiert")
            else:
                new_lines.append(line)

        # Wenn SECRET_KEY nicht gefunden, am Ende hinzufügen
        if not secret_key_found:
            # Prüfen ob Security-Sektion existiert
            if any("# Security" in line for line in new_lines):
                # Nach Security-Kommentar einfügen
                insert_idx = next(i for i, line in enumerate(new_lines) if "# Security" in line)
                # Überspringe Kommentarzeilen
                while insert_idx < len(new_lines) and (new_lines[insert_idx].startswith("#") or not new_lines[insert_idx].strip()):
                    insert_idx += 1
                new_lines.insert(insert_idx, f"SECRET_KEY={secret_key}")
            else:
                # Am Ende hinzufügen
                new_lines.append("")
                new_lines.append("# Security")
                new_lines.append(f"SECRET_KEY={secret_key}")

            print(f"✅ SECRET_KEY zu .env hinzugefügt")

        # .env Datei speichern
        env_file.write_text("\n".join(new_lines) + "\n")
        return True
    else:
        print(f"⚠️  .env Datei nicht gefunden. Bitte manuell erstellen.")
        return False


def main():
    print("=" * 80)
    print("🔐 Secret Key Generator für Freizeit-Kassen-System")
    print("=" * 80)
    print()

    # Secret Key generieren
    secret_key = generate_secret_key()

    print(f"✨ Neuer Secret Key generiert:")
    print(f"   {secret_key}")
    print()

    # Frage ob automatisch in .env einfügen
    try:
        response = input("💾 Soll der Key automatisch in .env gespeichert werden? (j/n): ").strip().lower()

        if response in ['j', 'ja', 'y', 'yes']:
            if update_env_file(secret_key):
                print()
                print("✅ Fertig! Der Secret Key wurde in .env gespeichert.")
                print("⚠️  Bitte starte die Anwendung neu, damit die Änderung wirksam wird.")
            else:
                print()
                print("ℹ️  Bitte füge den folgenden Eintrag manuell zu deiner .env Datei hinzu:")
                print(f"   SECRET_KEY={secret_key}")
        else:
            print()
            print("ℹ️  Bitte füge den folgenden Eintrag zu deiner .env Datei hinzu:")
            print(f"   SECRET_KEY={secret_key}")

    except KeyboardInterrupt:
        print()
        print()
        print("⚠️  Abgebrochen. Bitte verwende den folgenden Key manuell:")
        print(f"   SECRET_KEY={secret_key}")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
