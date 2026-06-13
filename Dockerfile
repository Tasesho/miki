FROM python:3.11-slim

# Configurar usuario no-root por seguridad
RUN groupadd -r miki && useradd -r -g miki -d /app miki

WORKDIR /app

# Variables de entorno de Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del proyecto usando el pyproject.toml
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install .

# Crear volumen local para la base de datos y dar permisos al usuario
RUN mkdir -p /app/data && chown -R miki:miki /app

USER miki
COPY --chown=miki:miki src/ ./src/

CMD ["python", "src/bot.py"]