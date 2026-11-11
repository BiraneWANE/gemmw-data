# Générateur de livrets au prénom (vague 1).
# Construire : docker build -t gemmw-generateur .
# Lancer     : docker run -p 8000:8000 -e GEMMW_API_CLE=... -v "$PWD/livrets:/livrets:ro" gemmw-generateur
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --extra api --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev --extra api

# Les livrets ne sont jamais copiés dans l'image : ils sont montés au lancement.
ENV GEMMW_LIVRETS_DIR=/livrets PATH="/app/.venv/bin:$PATH"
RUN useradd --create-home gemmw
USER gemmw
EXPOSE 8000
CMD ["uvicorn", "gemmw.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
