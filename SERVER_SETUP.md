# Configuración del Servidor (Hetzner VPS)

Este documento guía la configuración segura del servidor con IP `178.156.143.222` para acceso por SSH, firewall, usuarios, permisos y 2FA.

## 1. Pruebas de Conectividad Inicial

- Ping: `ping 178.156.143.222`
- Puerto SSH (Windows PowerShell): `Test-NetConnection -ComputerName 178.156.143.222 -Port 22 -InformationLevel Detailed`
- Puerto SSH (Linux/macOS): `nc -zv 178.156.143.222 22`

## 2. Conexión SSH Segura

- Conexión: `ssh root@178.156.143.222`
- Si es la primera conexión, acepta la huella y usa la contraseña actual.
- Recomendado: subir una clave pública al servidor y deshabilitar login por contraseña para el usuario admin.

## 3. Cambio de Contraseña Root

- Comando: `passwd root`
- Use una contraseña fuerte y única. Documente el cambio de forma segura (gestor de contraseñas).

## 4. Ejecución del Script de Hardening

1) Copie el script al servidor:

- Windows (PowerShell) desde el proyecto:
  - `scp Urbany/server/setup-server.sh root@178.156.143.222:/root/setup-server.sh`
- Linux/macOS:
  - `scp Urbany/server/setup-server.sh root@178.156.143.222:/root/setup-server.sh`

2) Conéctese y ejecútelo:

```
ssh root@178.156.143.222
chmod +x /root/setup-server.sh
ADMIN_USER=deploy SSH_PORT=22 /root/setup-server.sh
```

- Resumen de lo que hace:
  - Actualiza el sistema y habilita actualizaciones automáticas.
  - Instala y configura `ufw` (firewall) con reglas para `22/tcp`, `80/tcp`, `443/tcp` y `limit` en SSH.
  - Instala y configura `fail2ban` para proteger SSH.
  - Crea usuario admin `deploy` y prepara su directorio `.ssh`.
  - Ajusta `sshd_config` para permitir PAM y teclado interactivo (necesario para 2FA), y limita el login de root.
  - Prepara PAM para Google Authenticator (`libpam-google-authenticator`) con `nullok` inicial.
  - Instala Docker y Docker Compose plugin, habilita el servicio y añade `deploy` al grupo `docker`.
  - Crea estructura de directorios: `/opt/urbany` (app), `/var/backups/urbany` (backups).

## 5. Configuración de 2FA (Google Authenticator)

Por cada usuario admin (ej. `deploy`):

```
su - deploy
google-authenticator
```

- Siga el asistente:
  - Escanee el QR con la app Google Authenticator/Authy.
  - Responda las preguntas según su política (recomendado: tokens de emergencia guardados, no permitir varias veces el mismo token, aumentar el rate limit).

- PAM (`/etc/pam.d/sshd`) ya incluye `auth required pam_google_authenticator.so nullok`.
  - Cuando todos los admins tengan 2FA, quite `nullok` para exigir 2FA siempre.

- Opcional: exigir clave pública + 2FA en SSH

  - En `/etc/ssh/sshd_config`: añada/ajuste
    - `AuthenticationMethods publickey,keyboard-interactive`
    - `PasswordAuthentication no` (si todos tienen claves y 2FA)
  - `systemctl restart ssh`

## 6. Firewall (UFW)

- Estado: `sudo ufw status verbose`
- Regla principal: `limit 22/tcp` para mitigar fuerza bruta.
- HTTP/HTTPS abiertos: `80/tcp` y `443/tcp`.
- Ajuste adicional: bloquee todo otro tráfico entrante por defecto.

## 7. fail2ban

- Ver estado: `sudo fail2ban-client status sshd`
- Logs: `/var/log/fail2ban.log`, `/var/log/auth.log`
- Política actual: `maxretry=5`, `bantime=1h`.

## 8. Pruebas después de cambios

- Conectividad:
  - `ssh -vv deploy@178.156.143.222` (verifique prompts y autenticación)
- Firewall:
  - `sudo ufw status verbose`
- 2FA:
  - Intente login y confirme que solicita código OTP.
- fail2ban:
  - Realice intentos fallidos (controlados) y verifique bans.

## 9. Seguridad Adicional (Recomendado)

- Deshabilitar completamente login de root por SSH (`PermitRootLogin no`) una vez que el usuario admin esté operativo.
- Configurar `allowusers` en `sshd_config` con la lista de usuarios permitidos.
- Instalar `auditd` para mayor trazabilidad.
- Crear claves SSH para `deploy` y desactivar `PasswordAuthentication` cuando sea posible.

## 10. Notas Operativas

- Documente cambios (fecha, responsable, comandos) y guarde copias de seguridad de archivos:
  - `/etc/ssh/sshd_config`, `/etc/pam.d/sshd`, `/etc/fail2ban/jail.local`.
- Mantenga tokens de emergencia de Google Authenticator en un gestor seguro.

## 11. Comandos de Reversión

- Si pierde acceso por cambios en SSH, use consola de Hetzner para revertir:
  - Restaurar `sshd_config` desde `.bak`.
  - Rehabilitar `PasswordAuthentication yes` temporalmente.
  - Reiniciar SSH: `systemctl restart ssh`

## 12. Checklist de Finalización

- [ ] Ping y puerto 22 accesibles.
- [ ] Usuario admin creado con acceso SSH funcional.
- [ ] root con contraseña cambiada y login SSH limitado.
- [ ] UFW activo con reglas apropiadas.
- [ ] fail2ban protegiendo SSH.
- [ ] 2FA operativo para usuarios admin.
- [ ] Documentación de cambios almacenada.

## 13. Despliegue y Automatización (systemd)

- Copie los archivos preparados en el repositorio al servidor:
  - `scp Urbany/server/urbany.service root@178.156.143.222:/etc/systemd/system/`
  - `scp Urbany/server/manage-urbany.sh root@178.156.143.222:/usr/local/bin/manage-urbany.sh && chmod +x /usr/local/bin/manage-urbany.sh`
- Habilite la unidad:
  - `systemctl daemon-reload`
  - `systemctl enable urbany.service`
  - `systemctl start urbany.service`
- Gestión:
  - `systemctl status urbany.service`
  - `manage-urbany.sh ps` / `manage-urbany.sh logs`

## 14. Backups

- Instale el script:
  - `scp Urbany/server/backup.sh root@178.156.143.222:/usr/local/bin/backup-urbany.sh && chmod +x /usr/local/bin/backup-urbany.sh`
- Configure cron (ejemplo diario 02:00):
  - `echo "0 2 * * * root /usr/local/bin/backup-urbany.sh" > /etc/cron.d/urbany-backup`
- Verifique que los archivos aparezcan en `/var/backups/urbany`.

## 15. Monitoreo y Logs

- Nginx: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- Docker Compose (app): `docker compose -f /opt/urbany/docker-compose.prod.yml logs -f`
- Django/DRF: logs en consola del contenedor `web` según `LOGGING` de `settings.py`.
- Recomendado: integrar Prometheus/Grafana y alertas si el proyecto lo requiere.