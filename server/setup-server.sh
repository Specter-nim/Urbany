#!/usr/bin/env bash
set -euo pipefail

# Este script debe ejecutarse como root en el servidor (Ubuntu/Debian).
# Prepara firewall (UFW), fail2ban, actualizaciones automáticas, crea usuario admin,
# instala Docker + Compose, crea directorios de despliegue y backup,
# y deja listo el entorno para configurar 2FA con Google Authenticator.

SSH_PORT=${SSH_PORT:-22}
ADMIN_USER=${ADMIN_USER:-deploy}
APP_DIR=${APP_DIR:-/opt/urbany}
BACKUP_DIR=${BACKUP_DIR:-/var/backups/urbany}

if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] Debe ejecutar este script como root" >&2
  exit 1
fi

echo "[setup] Actualizando sistema y herramientas básicas..."
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ufw fail2ban unattended-upgrades sudo ca-certificates curl gnupg \
  libpam-google-authenticator qrencode

echo "[setup] Habilitando actualizaciones automáticas..."
dpkg-reconfigure -plow unattended-upgrades || true
systemctl enable --now unattended-upgrades || true

echo "[setup] Creando usuario administrador: ${ADMIN_USER}"
if ! id "${ADMIN_USER}" &>/dev/null; then
  adduser --disabled-password --gecos "" "${ADMIN_USER}"
  usermod -aG sudo "${ADMIN_USER}"
fi
mkdir -p "/home/${ADMIN_USER}/.ssh"
chmod 700 "/home/${ADMIN_USER}/.ssh"
touch "/home/${ADMIN_USER}/.ssh/authorized_keys"
chmod 600 "/home/${ADMIN_USER}/.ssh/authorized_keys"
chown -R "${ADMIN_USER}:${ADMIN_USER}" "/home/${ADMIN_USER}/.ssh"
echo "[setup] Copie su clave pública en /home/${ADMIN_USER}/.ssh/authorized_keys"

echo "[setup] Configurando SSH (sshd)..."
SSHD_CFG="/etc/ssh/sshd_config"
cp "$SSHD_CFG" "/etc/ssh/sshd_config.bak.$(date +%F-%H%M%S)"
sed -i "s/^#\?Port .*/Port ${SSH_PORT}/" "$SSHD_CFG"
sed -i "s/^#\?PermitRootLogin .*/PermitRootLogin prohibit-password/" "$SSHD_CFG"
sed -i "s/^#\?PasswordAuthentication .*/PasswordAuthentication yes/" "$SSHD_CFG"
sed -i "s/^#\?UsePAM .*/UsePAM yes/" "$SSHD_CFG"
if ! grep -q '^KbdInteractiveAuthentication' "$SSHD_CFG"; then
  echo "KbdInteractiveAuthentication yes" >> "$SSHD_CFG"
fi
# Para requerir 2FA + clave pública posteriormente (cuando 2FA esté listo),
# puede habilitar: AuthenticationMethods publickey,keyboard-interactive
# sed -i "s/^#\?AuthenticationMethods.*/AuthenticationMethods publickey,keyboard-interactive/" "$SSHD_CFG"
systemctl restart ssh || systemctl restart sshd

echo "[setup] Configurando UFW (firewall)..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ${SSH_PORT}/tcp
ufw limit ${SSH_PORT}/tcp
ufw allow 80/tcp
ufw allow 443/tcp
yes | ufw enable
ufw status verbose

echo "[setup] Configurando fail2ban para proteger SSH..."
cat >/etc/fail2ban/jail.local <<'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port    = ssh
logpath = /var/log/auth.log
backend = systemd
EOF
systemctl enable --now fail2ban
fail2ban-client status sshd || true

echo "[setup] Preparando PAM para Google Authenticator (2FA)..."
PAM_SSHD="/etc/pam.d/sshd"
cp "$PAM_SSHD" "/etc/pam.d/sshd.bak.$(date +%F-%H%M%S)"
# Permite que los usuarios sin 2FA aún puedan entrar (nullok). Se recomienda
# quitar 'nullok' una vez configurado 2FA para todos los usuarios administradores.
if ! grep -q 'pam_google_authenticator.so' "$PAM_SSHD"; then
  sed -i '1i auth required pam_google_authenticator.so nullok' "$PAM_SSHD"
fi

echo "[setup] Instalando Docker y Compose..."
curl -fsSL https://get.docker.com | sh
usermod -aG docker "${ADMIN_USER}"
systemctl enable --now docker
docker --version || true
docker compose version || true

echo "[setup] Creando estructura de directorios para app y backups..."
mkdir -p "${APP_DIR}/docker" "${APP_DIR}/dist" "${BACKUP_DIR}"
chmod 750 "${APP_DIR}" "${BACKUP_DIR}"

echo "[setup] Endurecimiento básico completado. Próximos pasos manuales:"
echo "  1) Establecer contraseña segura para root: passwd root"
echo "  2) Inicializar 2FA para cada usuario admin: su - ${ADMIN_USER} -c google-authenticator"
echo "  3) (Opcional) Requerir 2FA + clave pública: habilitar AuthenticationMethods en sshd_config"
echo "  4) Probar conectividad SSH, firewall y fail2ban"
echo "  5) Copiar compose y archivos de la app a ${APP_DIR} y levantar con Docker Compose"

echo "[setup] Done."