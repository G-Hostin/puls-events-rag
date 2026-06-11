FROM python:3.13-slim

# Installer uv 
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Repertoire de travail
WORKDIR /app

# Copier les fichiers de gestion de deps en premier (pour le cache Docker)
COPY pyproject.toml uv.lock ./

# Installer les dependances (sans dev)
RUN uv sync --frozen --no-dev

# Copier le code source
COPY src/ ./src/
COPY scripts/ ./scripts/

# Creer les dossiers data attendus
RUN mkdir -p data/index data/eval

# Exposer le port de l'API
EXPOSE 8000

# Commande de demarrage
CMD ["uv", "run", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]