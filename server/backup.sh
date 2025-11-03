#!/usr/bin/env bash
set -euo pipefail

# Backup de Postgres dentro de Compose y archivos media/static.
# Requisitos: docker, permisos para leer volúmenes.

APP_DIR=${APP_DIR:-/opt/urbany}
BACKUP_DIR=${BACKUP_DIR:-/var/backups/urbany}
TIMESTAMP=$(date +%F-%H%M%S)

cd "$APP_DIR"

echo "[backup] Creando dump de Postgres..."
docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -F c \
  > "$BACKUP_DIR/pg_dump_${TIMESTAMP}.dump"

echo "[backup] Empaquetando staticfiles y media..."
tar -czf "$BACKUP_DIR/files_${TIMESTAMP}.tar.gz" -C "$APP_DIR" staticfiles media || true

echo "[backup] Backup completado en $BACKUP_DIR"