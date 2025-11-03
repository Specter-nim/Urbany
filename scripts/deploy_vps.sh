#!/usr/bin/env bash
set -euo pipefail

# Despliegue al VPS: copia compose de prod, nginx.conf y carga imágenes
# Requisitos en local: docker, ssh/scp.

VPS_HOST=${VPS_HOST:-178.156.143.222}
VPS_USER=${VPS_USER:-root}
REMOTE_DIR=${REMOTE_DIR:-/opt/urbany}
COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.prod.yml}

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "[deploy_vps] Construyendo imágenes locales..."
docker compose build

echo "[deploy_vps] Guardando imágenes como tar..."
mkdir -p dist
docker save urbany/web:latest -o dist/urbany-web.tar
docker save urbany/celery:latest -o dist/urbany-celery.tar
docker save urbany/celery-beat:latest -o dist/urbany-celery-beat.tar

echo "[deploy_vps] Creando directorio remoto: ${REMOTE_DIR}"
ssh "${VPS_USER}@${VPS_HOST}" "mkdir -p ${REMOTE_DIR} ${REMOTE_DIR}/docker ${REMOTE_DIR}/dist"

echo "[deploy_vps] Copiando archivos al VPS..."
scp "$PROJECT_DIR/${COMPOSE_FILE}" "${VPS_USER}@${VPS_HOST}:${REMOTE_DIR}/"
scp "$PROJECT_DIR/docker/nginx.conf" "${VPS_USER}@${VPS_HOST}:${REMOTE_DIR}/docker/nginx.conf"
scp "$PROJECT_DIR/.env" "${VPS_USER}@${VPS_HOST}:${REMOTE_DIR}/.env"
scp "$PROJECT_DIR/dist/urbany-web.tar" "${VPS_USER}@${VPS_HOST}:${REMOTE_DIR}/dist/"
scp "$PROJECT_DIR/dist/urbany-celery.tar" "${VPS_USER}@${VPS_HOST}:${REMOTE_DIR}/dist/"
scp "$PROJECT_DIR/dist/urbany-celery-beat.tar" "${VPS_USER}@${VPS_HOST}:${REMOTE_DIR}/dist/"

echo "[deploy_vps] Cargando imágenes en el VPS..."
ssh "${VPS_USER}@${VPS_HOST}" "docker load -i ${REMOTE_DIR}/dist/urbany-web.tar && docker load -i ${REMOTE_DIR}/dist/urbany-celery.tar && docker load -i ${REMOTE_DIR}/dist/urbany-celery-beat.tar"

echo "[deploy_vps] Levantando servicios en el VPS..."
ssh "${VPS_USER}@${VPS_HOST}" "cd ${REMOTE_DIR} && docker compose -f ${COMPOSE_FILE} up -d"

echo "[deploy_vps] Estado en el VPS:"
ssh "${VPS_USER}@${VPS_HOST}" "cd ${REMOTE_DIR} && docker compose -f ${COMPOSE_FILE} ps"

echo "[deploy_vps] Despliegue completado."