#!/bin/bash
# Release-Skript für MGBFreizeitplaner
# Automatisiert: Version setzen, Tag erstellen, committen und pushen
#
# Verwendung:
#   ./release.sh 0.3.0
#   ./release.sh 0.3.0 --no-push  # Nur lokal, kein Push

set -e  # Bei Fehler abbrechen

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Prüfe ob Version angegeben wurde
if [ -z "$1" ]; then
    echo -e "${RED}❌ Fehler: Keine Version angegeben${NC}"
    echo ""
    echo "Verwendung:"
    echo "  ./release.sh 0.3.0           # Erstellt Version 0.3.0 und pusht alles"
    echo "  ./release.sh 0.3.0 --no-push # Nur lokal, kein Push"
    echo ""
    echo "Aktuelle Version:"
    cat version.txt 2>/dev/null || echo "0.0.0"
    exit 1
fi

VERSION=$1
NO_PUSH=false

if [ "$2" == "--no-push" ]; then
    NO_PUSH=true
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  MGBFreizeitplaner Release ${VERSION}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Schritt 1: Version setzen und Tag erstellen
echo -e "${YELLOW}▶ Schritt 1/5: Version setzen und Git-Tag erstellen...${NC}"
python update_version.py "$VERSION"
echo ""

# Schritt 2: version.txt zum Staging-Bereich hinzufügen
echo -e "${YELLOW}▶ Schritt 2/5: version.txt zum Staging-Bereich hinzufügen...${NC}"
git add version.txt
echo -e "${GREEN}✅ version.txt hinzugefügt${NC}"
echo ""

# Schritt 3: Committen
echo -e "${YELLOW}▶ Schritt 3/5: Version-Bump committen...${NC}"
git commit -m "Bump version to ${VERSION}"
echo -e "${GREEN}✅ Commit erstellt${NC}"
echo ""

if [ "$NO_PUSH" = true ]; then
    echo -e "${YELLOW}⚠️  --no-push Flag gesetzt, überspringe Push-Schritte${NC}"
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Version ${VERSION} erfolgreich erstellt (lokal)!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Nächste Schritte (manuell):"
    echo "  git push"
    echo "  git push origin v${VERSION}"
    exit 0
fi

# Schritt 4: Branch pushen
echo -e "${YELLOW}▶ Schritt 4/5: Branch pushen...${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push -u origin "$CURRENT_BRANCH" || {
    echo -e "${RED}❌ Branch-Push fehlgeschlagen${NC}"
    echo -e "${YELLOW}Versuchen Sie manuell: git push${NC}"
    exit 1
}
echo -e "${GREEN}✅ Branch gepusht: ${CURRENT_BRANCH}${NC}"
echo ""

# Schritt 5: Tag pushen
echo -e "${YELLOW}▶ Schritt 5/5: Git-Tag pushen...${NC}"
git push origin "v${VERSION}" 2>&1 | {
    if grep -q "403\|error\|fatal"; then
        echo -e "${YELLOW}⚠️  Tag-Push hat möglicherweise nicht funktioniert${NC}"
        echo -e "${YELLOW}   Bitte pushen Sie den Tag manuell:${NC}"
        echo -e "${BLUE}   git push origin v${VERSION}${NC}"
        echo ""
    else
        echo -e "${GREEN}✅ Tag gepusht: v${VERSION}${NC}"
        echo ""
    fi
}

# Erfolg!
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Release ${VERSION} erfolgreich erstellt!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Zusammenfassung:"
echo "  • Version in version.txt: ${VERSION}"
echo "  • Git-Tag erstellt: v${VERSION}"
echo "  • Branch gepusht: ${CURRENT_BRANCH}"
echo ""
echo "Alle Tags anzeigen:"
echo "  git tag -l"
echo ""
