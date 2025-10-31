# Base: Python slim para producción
FROM python:3.11-slim AS base

# Evita crear pyc y usa stdout/stderr sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings

# Instala dependencias del sistema necesarias (libpq para Postgres, netcat para health/wait)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crea usuario no root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copia solo requirements primero para aprovechar cache
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia el proyecto
COPY . /app

# Asegura permisos para el usuario
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

# Variables de entorno por defecto (se pueden sobrescribir en docker-compose)
ENV REDIS_HOST=redis \
    REDIS_PORT=6379 \
    REDIS_DB=0 \
    USE_POSTGRES=false \
    DB_HOST=db \
    DB_PORT=5432 \
    DB_NAME=urbany_db \
    DB_USER=postgres \
    DB_PASSWORD=postgres \
    ALLOWED_HOSTS=localhost,127.0.0.1

# Copia entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

# Expone puerto de la aplicación ASGI
EXPOSE 8000

# Ejecuta migraciones y arranca Daphne
ENTRYPOINT ["/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]