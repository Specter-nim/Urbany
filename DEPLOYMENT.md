# Despliegue con Docker y Docker Compose

Este documento describe cómo dockerizar y desplegar Urbany en local y en un VPS (Hetzner) usando Docker y Docker Compose.

## Requisitos Previos
- `Docker` y `Docker Compose` instalados.
- Acceso a una `.env` con valores de producción (puede basarse en `.env.example`).
- Puertos disponibles: `8000` (aplicación), `5432` (Postgres), `6379` (Redis).

## Estructura de Contenedores
- `web`: Django + Channels servido con `Daphne` (ASGI).
- `db`: Postgres 15 (datos persistentes).
- `redis`: Redis 7 para Channels y Celery.
- `celery`: worker para tareas asíncronas.
- `celery_beat`: programador de tareas periódicas.
- `nginx`: reverse proxy con HTTPS, WebSockets y rate limiting.

## Variables de Entorno Clave
- `DEBUG`: `False` en producción.
- `ALLOWED_HOSTS`: dominios o IPs permitidos (ej. `mi-dominio.com,mi-ip`).
- `USE_POSTGRES`: `true` para producción (activa Postgres en `settings`).
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: configuración de Postgres.
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`: configuración de Redis.
- `SECRET_KEY`: clave secreta de Django.
- `CORS_ALLOWED_ORIGINS`: lista separada por comas de orígenes permitidos.
- `THROTTLE_ANON` y `THROTTLE_USER`: tasas DRF (ej. `100/day`, `1000/day`).
- `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`: seguridad bajo HTTPS.

## Comandos Básicos

### Local (Linux/macOS)
- Construir: `scripts/deploy.sh build`
- Levantar: `scripts/deploy.sh up`
- Estado: `scripts/deploy.sh status`
- Logs: `scripts/deploy.sh logs`
- Detener: `scripts/deploy.sh down`

### Windows (PowerShell)
- Construir: `./scripts/deploy.ps1 build`
- Levantar: `./scripts/deploy.ps1 up`
- Estado: `./scripts/deploy.ps1 status`
- Logs: `./scripts/deploy.ps1 logs`
- Detener: `./scripts/deploy.ps1 down`

## Redes y Volúmenes
`docker-compose.yml` define:
- Volúmenes persistentes: `postgres_data` (DB), `redis_data` (Redis), `staticfiles`, `media`.
- Certificados TLS: volumen `certs` montado en `/etc/nginx/certs`.
- Red puente `urbany_net` para comunicación interna.

## Compatibilidad con Hetzner VPS
- Recursos recomendados (web):
  - Límites: `1 CPU`, `512MB RAM` (ajustar según carga).
  - Reservas: `0.5 CPU`, `256MB RAM`.
  - Nota: El bloque `deploy.resources` en Compose se aplica con Swarm; en Compose “clásico” puede ignorarse. Alternativamente, limite recursos con `docker run --cpus --memory` si no usa Swarm.
- Almacenamiento persistente:
  - Postgres: volumen `postgres_data` mapeado por defecto a `/var/lib/docker/volumes/...` en el host.
  - Respaldos programados de Postgres (recomendado con `pg_dump`).
- Optimización producción:
  - `DEBUG=False`, `ALLOWED_HOSTS` correcto, `SECRET_KEY` seguro.
  - Use `Daphne` detrás de un proxy inverso (opcional: Nginx) para TLS y compresión.
  - Configure `CELERY` y `REDIS` en servicios dedicados.
  - Configure certificados válidos (Let’s Encrypt o propios) en `certs`.
- Seguridad básica:
  - Contenedor `web` corre como usuario no root (`appuser`).
  - `security_opt: no-new-privileges:true` y `cap_drop` por defecto.
  - Evite exponer `db` y `redis` a internet, mantenga puertos sin publicar si no es necesario.

## Solución de Problemas Comunes
- El `web` no arranca:
  - Verifique que `db` y `redis` estén `healthy` (`docker compose ps`).
  - Revise logs (`scripts/deploy.sh logs`).
- Error de conexión a Postgres:
  - Asegure `USE_POSTGRES=true` y credenciales correctas en entorno.
  - `DB_HOST` debe ser el nombre del servicio (`db`).
- WebSockets no conectan:
  - Verifique que `REDIS_HOST=redis` y `channels_redis` esté activo.
  - Si usa proxy inverso, habilite `upgrade` para WebSockets.
  - Confirme que Nginx tiene `proxy_set_header Upgrade` y `Connection` configurados.
- Archivos estáticos no se ven:
  - `collectstatic` corre en `entrypoint`. Asegure volumen `staticfiles` montado y accesible.

## Escalabilidad Básica
- Para escalar `web` (sin Swarm): `docker compose up --scale web=2 -d` (requiere sticky sessions o Channel Layers compartida si usa WebSockets; Redis ya cumple este rol).
- Celery workers: `docker compose up --scale celery=3 -d` para más concurrencia.
 - Nginx manejará conexiones concurrentes y limitación de tasa; ajuste `worker_connections` según carga.

## Notas
- Este despliegue asume que la app sirve ASGI con `Daphne`. En producción, se recomienda añadir Nginx para TLS y caching de estáticos.
- Si requiere PostGIS/GIS, habilite `django.contrib.gis` e instale dependencias del sistema (GDAL/GEOS) y cambie `ENGINE` a `django.contrib.gis.db.backends.postgis`.
 - Coloque certificados en `Urbany/docker/certs` y mapee al volumen `certs` (o monte desde el host en producción).