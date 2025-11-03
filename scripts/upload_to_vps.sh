#!/usr/bin/env bash
set -euo pipefail

# ======== CONFIGURA TUS CREDENCIALES ========
VPS_USER=${VPS_USER:-root}
VPS_HOST=${VPS_HOST:-178.156.143.222}
LOCAL_PROJECT_PATH=${LOCAL_PROJECT_PATH:-"$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"}
REMOTE_DIR=${REMOTE_DIR:-/opt/urbany}
# ============================================

echo "📁 Validando ruta local del proyecto: ${LOCAL_PROJECT_PATH}"
if [ ! -d "${LOCAL_PROJECT_PATH}" ]; then
  echo "❌ No existe la ruta local ${LOCAL_PROJECT_PATH}" >&2
  exit 1
fi

echo "📁 Creando estructura de carpetas en el VPS..."
ssh "${VPS_USER}@${VPS_HOST}" "mkdir -p ${REMOTE_DIR} ${REMOTE_DIR}/server ${REMOTE_DIR}/logs ${REMOTE_DIR}/media ${REMOTE_DIR}/static"

echo "⬆️ Subiendo proyecto completo al VPS..."
scp -r "${LOCAL_PROJECT_PATH}/." "${VPS_USER}@${VPS_HOST}:${REMOTE_DIR}/"

echo "🔒 Configurando permisos..."
ssh "${VPS_USER}@${VPS_HOST}" "chown -R root:root ${REMOTE_DIR} && chmod -R 755 ${REMOTE_DIR}"

echo "🐳 Construyendo y levantando contenedores en el VPS..."
ssh "${VPS_USER}@${VPS_HOST}" bash -s <<'EOF'
set -euo pipefail
cd /opt/urbany

echo "✅ Validando docker-compose.prod.yml..."
if [ ! -f "docker-compose.prod.yml" ]; then
  echo "❌ Error: no se encontró docker-compose.prod.yml en /opt/urbany"
  exit 1
fi

echo "🛑 Deteniendo contenedores previos (si existen)..."
docker compose -f docker-compose.prod.yml down || true

echo "⚙️ Construyendo imágenes Docker (esto puede tardar unos minutos)..."
docker compose -f docker-compose.prod.yml build

echo "🚀 Iniciando servicios con docker compose..."
docker compose -f docker-compose.prod.yml up -d

echo -e "\n📦 Estado final de contenedores:"
docker compose -f docker-compose.prod.yml ps

echo -e "\n🧾 Logs iniciales (últimas 50 líneas de 'web'):"
docker compose -f docker-compose.prod.yml logs --tail=50 web || true

echo -e "\n📁 Contenido actual de /opt/urbany:"
ls -lah /opt/urbany
EOF

echo "✅ Despliegue completado. Usa /opt/urbany/server/generate_acceso_frontend.sh para generar ACCESO_FRONTEND.md."