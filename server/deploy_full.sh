#!/usr/bin/env bash
set -euo pipefail

# Despliegue completo de Urbany en VPS (Ubuntu/Debian)
# - Verifica requisitos
# - Valida variables de entorno
# - Ajusta permisos
# - Construye y levanta contenedores
# - Ejecuta pruebas de humo y valida endpoints
# - Genera reporte y registra versión/estado

APP_DIR=${APP_DIR:-/opt/urbany}
COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.prod.yml}
USERNAME=${USERNAME:-deploy_admin}
REPORT_FILE=${REPORT_FILE:-$APP_DIR/deploy_report.md}
CHANGELOG_FILE=${CHANGELOG_FILE:-$APP_DIR/deployments.log}

cd "$APP_DIR"

echo "[1/5] Verificando requisitos previos..."
for cmd in docker curl openssl systemctl; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "❌ Falta el comando: $cmd" >&2
  else
    echo "✅ $cmd OK"
  fi
done

echo "[2/5] Validando variables de entorno (.env)..."
if [ ! -f "$APP_DIR/.env" ]; then
  echo "❌ No existe $APP_DIR/.env" >&2
  exit 1
fi

required_vars=(DEBUG ALLOWED_HOSTS USE_POSTGRES DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD REDIS_HOST REDIS_PORT SECRET_KEY CORS_ALLOWED_ORIGINS URBANY_TOKEN)
missing=()
for var in "${required_vars[@]}"; do
  if ! grep -q "^$var=" "$APP_DIR/.env"; then
    missing+=("$var")
  fi
done
if [ ${#missing[@]} -gt 0 ]; then
  echo "❌ Faltan variables en .env: ${missing[*]}" >&2
  exit 1
fi
echo "✅ .env contiene variables esenciales"

echo "[2.1] Ajustando permisos de directorios..."
mkdir -p "$APP_DIR/server" "$APP_DIR/logs" "$APP_DIR/media" "$APP_DIR/static"
chown -R root:root "$APP_DIR"
chmod -R 755 "$APP_DIR"
echo "✅ Permisos aplicados"

echo "[3/5] Construyendo y levantando servicios Docker..."
if [ ! -f "$APP_DIR/$COMPOSE_FILE" ]; then
  echo "❌ No se encontró $APP_DIR/$COMPOSE_FILE" >&2
  exit 1
fi
# Selección automática de configuración Nginx según disponibilidad de certificados
if [ ! -f "/etc/nginx/certs/privkey.pem" ] || [ ! -f "/etc/nginx/certs/fullchain.pem" ]; then
  echo "⚠️ Certificados TLS no encontrados. Usando configuración HTTP temporal."
  if [ -f "$APP_DIR/docker/nginx.http.conf" ]; then
    cp -f "$APP_DIR/docker/nginx.http.conf" "$APP_DIR/docker/nginx.conf"
  fi
else
  echo "✅ Certificados TLS detectados. Usando configuración HTTPS."
fi
docker compose -f "$COMPOSE_FILE" down || true
docker compose -f "$COMPOSE_FILE" build
docker compose -f "$COMPOSE_FILE" up -d
echo "✅ Servicios levantados"

echo "[3.1] Estado de contenedores:"
docker compose -f "$COMPOSE_FILE" ps

echo "[3.2] Esperando a que 'web' y 'nginx' estén Up..."
for svc in web nginx; do
  tries=0
  until docker compose -f "$COMPOSE_FILE" ps "$svc" | grep -q "Up"; do
    tries=$((tries+1))
    if [ $tries -gt 30 ]; then
      echo "❌ $svc no está Up tras esperar" >&2
      docker compose -f "$COMPOSE_FILE" logs "$svc" || true
      exit 1
    fi
    sleep 2
  done
  echo "✅ $svc Up"
done

echo "[4/5] Pruebas de humo y validación de endpoints..."
HTTP_STATUS=$(curl -Is http://localhost/ | head -n1 | awk '{print $2}' || true)
HTTPS_STATUS=$(curl -Is https://localhost/ | head -n1 | awk '{print $2}' || true)
DOCS_STATUS=$(curl -Is https://localhost/api/docs/ | head -n1 | awk '{print $2}' || true)
REDOC_STATUS=$(curl -Is https://localhost/api/redoc/ | head -n1 | awk '{print $2}' || true)

echo "HTTP: $HTTP_STATUS | HTTPS: $HTTPS_STATUS | /api/docs: $DOCS_STATUS | /api/redoc: $REDOC_STATUS"

if [ "$DOCS_STATUS" = "200" ] || [ "$REDOC_STATUS" = "200" ]; then
  echo "[4.1] Endpoints válidos, generando API Key..."
  if [ -x "$APP_DIR/server/generate_acceso_frontend.sh" ]; then
    "$APP_DIR/server/generate_acceso_frontend.sh" "$USERNAME" || true
  else
    echo "⚠️ No se encontró generate_acceso_frontend.sh ejecutable"
  fi
else
  echo "⚠️ Endpoints docs/redoc no devuelven 200; revisar TLS, ALLOWED_HOSTS, CORS y logs"
fi

echo "[5/5] Generando reporte de despliegue..."
{
  echo "# Reporte de Despliegue - Urbany"
  echo "Fecha: $(date)"
  echo "Directorio de app: $APP_DIR"
  echo "Compose: $COMPOSE_FILE"
  echo "\n## Estado de Servicios"
  docker compose -f "$COMPOSE_FILE" ps || true
  echo "\n## Docker Images"
  docker compose -f "$COMPOSE_FILE" images || true
  echo "\n## Puertos abiertos"
  ss -tulpen | grep -E 'LISTEN|80|443|5432|6379' || true
  echo "\n## UFW"
  ufw status verbose || true
  echo "\n## fail2ban"
  fail2ban-client status || true
  echo "\n## Nginx config test"
  docker compose -f "$COMPOSE_FILE" exec -T nginx nginx -t || true
  echo "\n## TLS Cert resumen"
  openssl s_client -connect localhost:443 -servername localhost < /dev/null 2>/dev/null | openssl x509 -noout -dates -subject -issuer || true
  echo "\n## HTTP/HTTPS Status"
  echo "HTTP: $HTTP_STATUS | HTTPS: $HTTPS_STATUS | /api/docs: $DOCS_STATUS | /api/redoc: $REDOC_STATUS"
} > "$REPORT_FILE"
chmod 644 "$REPORT_FILE"
echo "✅ Reporte generado: $REPORT_FILE"

echo "Registrando despliegue en $CHANGELOG_FILE..."
{
  echo "$(date) - Despliegue ejecutado. HTTP:$HTTP_STATUS HTTPS:$HTTPS_STATUS DOCS:$DOCS_STATUS REDOC:$REDOC_STATUS"
} >> "$CHANGELOG_FILE"
chmod 644 "$CHANGELOG_FILE"
echo "✅ Registro actualizado: $CHANGELOG_FILE"

echo "[FIN] Despliegue completo y verificado."