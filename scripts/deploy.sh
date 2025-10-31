#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

function build() {
  echo "[deploy] Construyendo imágenes..."
  docker compose build
}

function up() {
  echo "[deploy] Levantando contenedores..."
  docker compose up -d
}

function status() {
  echo "[deploy] Estado de servicios:"
  docker compose ps
}

function logs() {
  echo "[deploy] Logs de 'web' (Ctrl+C para salir)"
  docker compose logs -f web
}

function down() {
  echo "[deploy] Deteniendo contenedores..."
  docker compose down
}

case "${1:-}" in
  build) build ;;
  up) build; up; status ;;
  status) status ;;
  logs) logs ;;
  down) down ;;
  *)
    echo "Uso: $0 {build|up|status|logs|down}"
    exit 1
    ;;
esac