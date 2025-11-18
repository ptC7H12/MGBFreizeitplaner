"""
Icon-Generator für MGBFreizeitplaner Desktop-App

Erstellt ein .ico-Icon aus dem SVG-Logo für Windows .exe
"""
import os
from pathlib import Path

# SVG-Icon aus der Landing-Page
SVG_CONTENT = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
    <rect width="20" height="20" fill="#2563eb"/>
    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" fill="white"/>
</svg>'''


def create_icon_with_pillow():
    """Erstellt .ico mit Pillow aus SVG (via cairosvg wenn verfügbar)"""
    try:
        from PIL import Image
        import io

        # Versuche cairosvg zu importieren
        try:
            import cairosvg
            use_cairosvg = True
            print("[INFO] Verwende cairosvg für SVG-Konvertierung")
        except ImportError:
            use_cairosvg = False
            print("[INFO] cairosvg nicht verfügbar, erstelle einfaches Icon")

        if use_cairosvg:
            # Konvertiere SVG zu PNG in verschiedenen Größen
            sizes = [16, 32, 48, 64, 128, 256]
            images = []

            for size in sizes:
                png_bytes = cairosvg.svg2png(
                    bytestring=SVG_CONTENT.encode('utf-8'),
                    output_width=size,
                    output_height=size
                )
                img = Image.open(io.BytesIO(png_bytes))
                images.append(img)

            # Speichere als .ico
            icon_path = Path(__file__).parent / "app_icon.ico"
            images[0].save(
                icon_path,
                format='ICO',
                sizes=[(img.width, img.height) for img in images],
                append_images=images[1:]
            )
            print(f"[OK] Icon erstellt: {icon_path}")
            return str(icon_path)

        else:
            # Fallback: Erstelle einfaches farbiges Icon ohne cairosvg
            from PIL import ImageDraw

            sizes = [16, 32, 48, 64, 128, 256]
            images = []

            for size in sizes:
                img = Image.new('RGBA', (size, size), (37, 99, 235, 255))  # Blue-600
                draw = ImageDraw.Draw(img)

                # Zeichne vereinfachtes Dreieck-Symbol
                points = [
                    (size // 2, size * 0.2),  # Top
                    (size * 0.3, size * 0.8),  # Bottom left
                    (size * 0.7, size * 0.8),  # Bottom right
                ]
                draw.polygon(points, fill=(255, 255, 255, 255))

                images.append(img)

            # Speichere als .ico
            icon_path = Path(__file__).parent / "app_icon.ico"
            images[0].save(
                icon_path,
                format='ICO',
                sizes=[(img.width, img.height) for img in images],
                append_images=images[1:]
            )
            print(f"[OK] Icon erstellt: {icon_path}")
            return str(icon_path)

    except ImportError as e:
        print(f"[FEHLER] Pillow nicht installiert: {e}")
        return None
    except Exception as e:
        print(f"[FEHLER] Icon-Erstellung fehlgeschlagen: {e}")
        return None


def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("  Icon-Generator für MGBFreizeitplaner")
    print("=" * 60)
    print()

    # Versuche Icon zu erstellen
    icon_path = create_icon_with_pillow()

    if icon_path:
        print()
        print("[OK] Icon wurde erfolgreich erstellt!")
        print(f"     Pfad: {icon_path}")
        print()
        print("[INFO] Nächste Schritte:")
        print("       1. Führe 'python build_desktop.py' aus")
        print("       2. Das Icon wird automatisch in die .exe eingebettet")
    else:
        print()
        print("[WARNUNG] Icon konnte nicht erstellt werden.")
        print("          Die .exe wird ohne Icon gebaut.")
        print()
        print("[INFO] Um Icons zu erstellen, installiere:")
        print("       pip install Pillow cairosvg")


if __name__ == "__main__":
    main()
