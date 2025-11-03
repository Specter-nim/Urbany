#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${APP_DIR:-/opt/urbany}
COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.prod.yml}

cd "$APP_DIR"

case "${1:-}" in
  start)
    docker compose -f "$COMPOSE_FILE" up -d ;;
  stop)
    docker compose -f "$COMPOSE_FILE" down ;;
  restart)
    docker compose -f "$COMPOSE_FILE" down && docker compose -f "$COMPOSE_FILE" up -d ;;
  ps)
    docker compose -f "$COMPOSE_FILE" ps ;;
  logs)
    docker compose -f "$COMPOSE_FILE" logs -f ;;
  *)
    echo "Uso: $0 {start|stop|restart|ps|logs}"
    exit 1 ;;
esac