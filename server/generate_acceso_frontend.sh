#!/usr/bin/env bash
set -euo pipefail

OUT_FILE="/opt/urbany/ACCESO_FRONTEND.md"
COMPOSE_FILE="/opt/urbany/docker-compose.prod.yml"
USERNAME=${1:-deploy_admin}

echo "=== ESTADO DOCKER ===" | sudo tee "$OUT_FILE" >/dev/null
sudo docker ps -a | sudo tee -a "$OUT_FILE" >/dev/null

echo -e "\n=== PROCESOS ACTIVOS ===" | sudo tee -a "$OUT_FILE" >/dev/null
sudo systemctl status nginx docker containerd --no-pager | sudo tee -a "$OUT_FILE" >/dev/null || true

echo -e "\n=== PUERTOS ABIERTOS ===" | sudo tee -a "$OUT_FILE" >/dev/null
sudo ss -tulpen | grep -E '80|443|5432|6379' | sudo tee -a "$OUT_FILE" >/dev/null || true

echo -e "\n=== UFW STATUS ===" | sudo tee -a "$OUT_FILE" >/dev/null
sudo ufw status verbose | sudo tee -a "$OUT_FILE" >/dev/null || true

echo -e "\n=== FAIL2BAN STATUS ===" | sudo tee -a "$OUT_FILE" >/dev/null
sudo fail2ban-client status | sudo tee -a "$OUT_FILE" >/dev/null || true

echo -e "\n=== VALIDACIÓN ENDPOINTS ===" | sudo tee -a "$OUT_FILE" >/dev/null
curl -Ik http://178.156.143.222/ | sudo tee -a "$OUT_FILE" >/dev/null || true
curl -Ik https://178.156.143.222/ | sudo tee -a "$OUT_FILE" >/dev/null || true
curl -Ik https://178.156.143.222/api/docs/ | sudo tee -a "$OUT_FILE" >/dev/null || true
curl -Ik https://178.156.143.222/api/redoc/ | sudo tee -a "$OUT_FILE" >/dev/null || true

# Comprobación básica para generar token solo si docs/redoc responden 200
DOCS_STATUS=$(curl -Is https://178.156.143.222/api/docs/ | head -n 1 | awk '{print $2}' || true)
REDOC_STATUS=$(curl -Is https://178.156.143.222/api/redoc/ | head -n 1 | awk '{print $2}' || true)

if [[ "$DOCS_STATUS" == "200" ]] || [[ "$REDOC_STATUS" == "200" ]]; then
  echo -e "\n=== GENERACIÓN DE API KEY ===" | sudo tee -a "$OUT_FILE" >/dev/null
  sudo docker compose -f "$COMPOSE_FILE" exec -T web python manage.py drf_create_token "$USERNAME" | sudo tee -a "$OUT_FILE" >/dev/null || true
else
  echo -e "\n=== GENERACIÓN DE API KEY OMITIDA (endpoints no válidos) ===" | sudo tee -a "$OUT_FILE" >/dev/null
fi

echo -e "\n## 🟢 ACCESO FRONTEND (API Key y Estado de Producción)" | sudo tee -a "$OUT_FILE" >/dev/null
echo -e "- Fecha: $(date)" | sudo tee -a "$OUT_FILE" >/dev/null
echo -e "- IP/Dominio: 178.156.143.222" | sudo tee -a "$OUT_FILE" >/dev/null
SERVICIOS=$(sudo docker ps --format '{{.Names}}' | xargs | tr ' ' ', ' || true)
echo -e "- Servicios activos: ${SERVICIOS}" | sudo tee -a "$OUT_FILE" >/dev/null
echo -e "- Endpoints disponibles: https://178.156.143.222/api/docs/ , /api/redoc/" | sudo tee -a "$OUT_FILE" >/dev/null
echo -e "- Archivo generado automáticamente desde VPS." | sudo tee -a "$OUT_FILE" >/dev/null

echo -e "\n=== CERTIFICADO TLS ===" | sudo tee -a "$OUT_FILE" >/dev/null
openssl s_client -connect 178.156.143.222:443 -servername 178.156.143.222 < /dev/null 2>/dev/null | openssl x509 -noout -dates -subject -issuer | sudo tee -a "$OUT_FILE" >/dev/null || true

echo -e "\n=== CABECERAS DE SEGURIDAD (HSTS, CSP) ===" | sudo tee -a "$OUT_FILE" >/dev/null
curl -Is https://178.156.143.222/  | grep -E 'Strict|Content-Security|Access-Control' | sudo tee -a "$OUT_FILE" >/dev/null || true

sudo chmod 600 "$OUT_FILE"
sudo chown root:root "$OUT_FILE"

echo "[OK] Informe generado en $OUT_FILE"