# Informe de Validación, Correcciones y Estado Final (178.156.143.222)

Este documento consolida el diagnóstico de conectividad, la configuración aplicada, los cambios realizados en el proyecto y los comandos de verificación para asegurar operación segura y disponible de los endpoints.

## 1) Estado Inicial y Validaciones

- Conectividad (ping):
```
Haciendo ping a 178.156.143.222 con 32 bytes de datos:
Respuesta desde 178.156.143.222: bytes=32 tiempo=112ms TTL=48
Respuesta desde 178.156.143.222: bytes=32 tiempo=112ms TTL=48
Respuesta desde 178.156.143.222: bytes=32 tiempo=112ms TTL=48
Respuesta desde 178.156.143.222: bytes=32 tiempo=122ms TTL=48

Estadísticas de ping:
Paquetes: enviados = 4, recibidos = 4, perdidos = 0 (0% perdidos)
RTT: mínimo=112ms, máximo=122ms, media=114ms
```

- Ruta (traceroute):
```
tracert -d 178.156.143.222
  1  192.168.100.1 (<1 ms)
  2  172.16.100.1 (3 ms)
  3  177.53.153.9 (4 ms)
  4  200.25.45.230 (4 ms)
  5  200.25.51.98 (3-5 ms)
  6  200.25.75.24 (65 ms)
  7  62.115.39.144 (65-66 ms)
  8  62.115.119.230 (93-94 ms)
  9  62.115.138.190 (93-96 ms, un salto con *)
 10  62.115.56.201 (113-116 ms)
 11  5.161.0.82 (113-115 ms)
 12  * * * (timeout)
 13  5.161.8.160 (112-113 ms)
 14  178.156.143.222 (113-114 ms)
Traza completa.
```

- DNS (PTR reverse):
```
nslookup 178.156.143.222
Nombre: static.222.143.156.178.clients.your-server.de
Address: 178.156.143.222
```

- Pruebas de puertos HTTP/HTTPS:
```
Test-NetConnection -ComputerName 178.156.143.222 -Port 80
TcpTestSucceeded: False

Test-NetConnection -ComputerName 178.156.143.222 -Port 443
TcpTestSucceeded: False

curl -I http://178.156.143.222/
curl: (7) Failed to connect to 178.156.143.222 port 80: Could not connect to server

curl -vk https://178.156.143.222/
* connect to 178.156.143.222 port 443 failed: Connection refused
curl: (7) Failed to connect to 178.156.143.222 port 443: Could not connect to server
```

Conclusión inicial: Red accesible; sin dominio A/AAAA público y sin TLS operativo.

Actualización HTTP: el puerto 80 muestra la página por defecto de Nginx en la IP, indicando que el servicio está instalado y sirviendo contenido básico (Welcome page) [0].

## 2) Correcciones Implementadas en el Proyecto

- Reverse proxy Nginx con HTTPS, WebSockets y rate limiting:
  - `docker/nginx.conf` (HTTP→HTTPS, TLS, HSTS, headers seguros, soporte WebSockets, limit_req 10 r/s con burst 20).
- Compose de producción con imágenes preconstruidas:
  - `docker-compose.prod.yml` (servicios `web`, `db`, `redis`, `celery`, `celery_beat`, `nginx`). Se eliminó atributo `version` obsoleto.
- Configuración Django para seguridad y rendimiento:
  - `core/settings.py` (CORS por entorno, throttling DRF anon/user, seguridad detrás de proxy: `SECURE_*`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, logging estándar).
  - `core/urls.py` (aliases `/api/docs` y `/api/redoc`).
- Hardening y preparación del servidor:
  - `server/setup-server.sh` (UFW, fail2ban, actualizaciones, usuario `deploy`, PAM+2FA, instalación Docker/Compose, estructura `/opt/urbany` y `/var/backups/urbany`).
  - `server/urbany.service` (systemd para arranque automático de Compose).
  - `server/manage-urbany.sh` (script de gestión start/stop/restart/logs/ps).
  - `server/backup.sh` (dump de Postgres y empaquetado de static/media; cron sugerido).
- Variables de entorno y documentación:
  - `.env.example` actualizado (CORS, throttling, USE_POSTGRES y seguridad HTTPS).
  - `DEPLOYMENT.md` y `SERVER_SETUP.md` ampliados (TLS, Nginx, systemd, backups, monitoreo).

## 3) Plan de Aplicación en el VPS (178.156.143.222)

Ejecutar en orden:

1. Hardening y dependencias:
```
scp Urbany/server/setup-server.sh root@178.156.143.222:/root/setup-server.sh
ssh root@178.156.143.222
chmod +x /root/setup-server.sh
ADMIN_USER=deploy SSH_PORT=22 APP_DIR=/opt/urbany BACKUP_DIR=/var/backups/urbany /root/setup-server.sh
passwd root
su - deploy && google-authenticator
```

2. Certificados TLS:
```
ssh root@178.156.143.222 "mkdir -p /etc/nginx/certs"
scp fullchain.pem root@178.156.143.222:/etc/nginx/certs/
scp privkey.pem root@178.156.143.222:/etc/nginx/certs/
```

3. Variables y proyecto:
```
# Ajustar .env local con producción y copiar
scp Urbany/.env root@178.156.143.222:/opt/urbany/.env
scp -r Urbany root@178.156.143.222:/opt/urbany
```

4. Despliegue (opción build en VPS):
```
ssh root@178.156.143.222 "cd /opt/urbany && docker compose -f docker-compose.yml build && docker compose -f docker-compose.yml up -d"
```

5. Arranque automático (systemd):
```
scp Urbany/server/urbany.service root@178.156.143.222:/etc/systemd/system/
ssh root@178.156.143.222 "systemctl daemon-reload && systemctl enable urbany.service && systemctl start urbany.service"
```

## 4) Verificaciones Posteriores

- Puertos y servicios:
```
Test-NetConnection -ComputerName 178.156.143.222 -Port 80
Test-NetConnection -ComputerName 178.156.143.222 -Port 443
ssh root@178.156.143.222 "cd /opt/urbany && docker compose -f docker-compose.prod.yml ps"
```

- Nginx y TLS:
```
ssh root@178.156.143.222 "docker compose -f /opt/urbany/docker-compose.prod.yml exec nginx nginx -t"
openssl s_client -connect 178.156.143.222:443 -servername 178.156.143.222 -showcerts
curl -I http://178.156.143.222/
curl -I https://178.156.143.222/
```

- Endpoints y documentación:
```
https://178.156.143.222/api/docs/
https://178.156.143.222/api/redoc/
# Probar JWT (Authorization: Bearer <token>) en endpoints protegidos
```

- CORS y rate limiting:
```
# Desde frontend en origen permitido, verificar headers CORS en respuestas
# Generar tráfico acelerado y observar respuestas 429 en DRF y limit_req de Nginx
```

- Logs y monitoreo:
```
ssh root@178.156.143.222 "docker compose -f /opt/urbany/docker-compose.prod.yml logs -f web"
tail -f /var/log/nginx/error.log
```

## 5) DNS y Configuración de Dominio

- Crear registro `A` del dominio hacia `178.156.143.222` (y `AAAA` si aplica IPv6).
- Ajustar `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` con el dominio final.
- Validar:
```
nslookup <tu-dominio>
dig A <tu-dominio>
```

## 6) Seguridad y Firewall

- UFW (ejecutado por setup-server.sh):
```
ufw default deny incoming
ufw default allow outgoing
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw limit 22/tcp
yes | ufw enable
ufw status verbose
```

- fail2ban:
```
fail2ban-client status sshd
```

- Endurecimiento adicional recomendado:
  - Deshabilitar login SSH de `root` (`PermitRootLogin no`) tras habilitar `deploy`.
  - `AuthenticationMethods publickey,keyboard-interactive` en `sshd_config` (clave + 2FA).
  - Cookies seguras y HSTS activos (variables ya configuradas en `.env`).

## 7) Backups y Automatización

- Instalar y programar backups:
```
scp Urbany/server/backup.sh root@178.156.143.222:/usr/local/bin/backup-urbany.sh
ssh root@178.156.143.222 "chmod +x /usr/local/bin/backup-urbany.sh"
ssh root@178.156.143.222 'echo "0 2 * * * root /usr/local/bin/backup-urbany.sh" > /etc/cron.d/urbany-backup'
```
- Verificar contenido en `/var/backups/urbany`.

## 8) Resultados Esperados (Estado Final)

- Puertos `80/443` accesibles externamente.
- `nginx` escuchando y proxyeando a `web:8000` (Daphne ASGI).
- TLS operativo con certificados válidos y HSTS activo.
- Documentación accesible en `/api/docs` y `/api/redoc`.
- Autenticación JWT y permisos `IsAuthenticated` por defecto en DRF.
- CORS restringido a dominios definidos; rate limiting activo.
- Logs visibles en Nginx y contenedor `web`.
- Backups diarios generados y cron activo.
- Arranque automático a través de `systemd` (`urbany.service`).

---

## 9) Apéndice: Cambios de Proyecto

- Archivos creados/actualizados:
  - `docker/nginx.conf`
  - `docker-compose.prod.yml`
  - `core/settings.py`, `core/urls.py`
  - `server/setup-server.sh`, `server/urbany.service`, `server/manage-urbany.sh`, `server/backup.sh`
  - `.env.example`
  - `DEPLOYMENT.md`, `SERVER_SETUP.md`

- Notas YAML:
  - `docker-compose.prod.yml` sin atributo `version` (Compose v2 lo ignora). Estructura validada; `security_opt: [ no-new-privileges:true ]` en `web`.

---

## 10) Registro de Ejecución (para completar en el VPS)

Tras ejecutar las acciones, copie aquí extractos relevantes:

- `docker compose ps` (estado de servicios)
- `nginx -t` (validación OK)
- `openssl s_client -connect 178.156.143.222:443 -showcerts` (cadena de certificados)
- Respuestas de `curl -I http://...` y `curl -I https://...`
- Salida de `ufw status verbose` y `fail2ban-client status sshd`
- Acceso a `/api/docs` y `/api/redoc` (HTTP 200)

> Al finalizar, suba este `varios.md` al servidor en `/opt/urbany/varios.md` para auditoría y trazabilidad.

Fin del informe.