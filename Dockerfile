# Multi-stage Build für optimale Image-Größe
FROM python:3.11-slim as base

# Setze Arbeitsverzeichnis
WORKDIR /app

# Umgebungsvariablen
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installiere System-Dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Requirements und installiere Python-Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere Anwendungscode
COPY ./app /app/app
COPY ./rulesets /app/rulesets

# Erstelle Verzeichnis für Datenbank
RUN mkdir -p /app/data

# Exponiere Port
EXPOSE 8000

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Starte Anwendung
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
