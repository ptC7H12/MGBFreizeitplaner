# Multi-stage Build für optimale Image-Größe
# Stage 1: Builder - Installiert Dependencies
FROM python:3.11-slim as builder

# Arbeitsverzeichnis für Build
WORKDIR /app

# Umgebungsvariablen für Build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installiere Build-Dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Requirements und installiere Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Runtime - Finales schlankes Image
FROM python:3.11-slim as runtime

# Arbeitsverzeichnis
WORKDIR /app

# Umgebungsvariablen für Runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Kopiere installierte Python-Packages vom Builder
COPY --from=builder /root/.local /root/.local

# Kopiere Anwendungscode
COPY ./app /app/app
COPY ./rulesets /app/rulesets
COPY ./migrations /app/migrations
COPY ./alembic.ini /app/alembic.ini

# Erstelle notwendige Verzeichnisse
RUN mkdir -p /app/data /app/uploads

# Exponiere Port
EXPOSE 8000

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Starte Anwendung
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
