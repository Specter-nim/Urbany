# Guía de Integración Frontend y Consumo de API (Urbany)

Este documento describe cómo el frontend debe integrarse con el backend Urbany, los endpoints disponibles, los headers requeridos, y proporciona una guía de despliegue y documentación del proceso seguido.

---

## 1. Configuración de la API

### Base URL

- Producción (IP actual): `https://178.156.143.222/`
- Prefijo de API: `https://178.156.143.222/api/`
- Documentación interactiva:
  - Swagger UI: `https://178.156.143.222/api/docs/`
  - ReDoc: `https://178.156.143.222/api/redoc/`
- Nota: si usas dominio, sustituye la IP por tu dominio y añade `https://<tu-dominio>/api/` a `CORS_ALLOWED_ORIGINS`.

### Headers requeridos

- `Authorization: Bearer <token>` (JWT generado para el usuario)
- `Content-Type: application/json`
- `Accept: application/json`
- CORS: el origen del frontend debe estar incluido en `CORS_ALLOWED_ORIGINS` del backend.

### Endpoints disponibles (resumen)

Para la lista completa y esquemas, utiliza la documentación interactiva (`/api/docs/` o `/api/redoc/`). A continuación, un resumen por módulo típico:

- Autenticación
  - `POST /api/auth/login/` → Inicia sesión (usuario/contraseña)
  - `POST /api/auth/refresh/` → Refresca token
  - `GET  /api/auth/me/` → Perfil del usuario autenticado
- Usuarios y Roles
  - `GET  /api/users/` → Lista usuarios
  - `POST /api/users/` → Crea usuario
  - `GET  /api/users/{id}/` → Detalle
  - `PATCH/PUT /api/users/{id}/` → Actualiza
  - `DELETE /api/users/{id}/` → Elimina
  - `GET  /api/roles/` → Lista roles
- Contactos
  - `GET  /api/contacts/`
  - `POST /api/contacts/`
  - `GET  /api/contacts/{id}/`
  - `PATCH/PUT /api/contacts/{id}/`
  - `DELETE /api/contacts/{id}/`
- Mensajería (Channels/WebSockets)
  - REST: `GET/POST /api/messages/`
  - WS: `wss://178.156.143.222/ws/chat/<room>/`
- Negocio/Contratos/Propiedades (CRUDs similares)
  - `GET/POST /api/business/`
  - `GET/POST /api/contracts/`
  - `GET/POST /api/properties/`
- Informes/Panel
  - `GET  /api/reports/summary/`
  - `GET  /api/dashboard/metrics/`

### Ejemplos de request/response

- Login (JWT)
```http
POST /api/auth/login/ HTTP/1.1
Host: 178.156.143.222
Content-Type: application/json

{
  "username": "deploy_admin",
  "password": "<tu_password>"
}
```
Respuesta (200):
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {"id": 1, "username": "deploy_admin"}
}
```

- Authenticated fetch
```http
GET /api/contacts/ HTTP/1.1
Host: 178.156.143.222
Authorization: Bearer eyJ...
Accept: application/json
```
Respuesta (200):
```json
[
  {"id": 101, "name": "Acme", "email": "info@acme.com"}
]
```

### Ejemplo cliente (JavaScript / axios)

```js
import axios from 'axios';

const API_BASE = 'https://178.156.143.222/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

export async function login(username, password) {
  const { data } = await api.post('/auth/login/', { username, password });
  api.defaults.headers.Authorization = `Bearer ${data.access}`;
  return data;
}

export async function listContacts() {
  const { data } = await api.get('/contacts/');
  return data;
}
```

### WebSocket (ejemplo)

```js
const ws = new WebSocket('wss://178.156.143.222/ws/chat/general/');
ws.onopen = () => ws.send(JSON.stringify({ type: 'ping' }));
ws.onmessage = (e) => console.log('WS message', e.data);
```

---

## 2. Guía de despliegue (backend + acceso frontend)

### Requisitos previos

- VPS con Docker y Docker Compose activos
- PuTTY en tu máquina (Windows): `plink.exe` y `pscp.exe`
- Variables de entorno (en `/opt/urbany/.env`) mínimas:
  - `DEBUG=False`
  - `ALLOWED_HOSTS=178.156.143.222,<tu-dominio>`
  - `USE_POSTGRES=true` + `DB_*`
  - `REDIS_HOST=redis`
  - `SECRET_KEY=<seguro>`
  - `CORS_ALLOWED_ORIGINS=https://<tu-dominio>` (o `https://178.156.143.222`)
  - `URBANY_TOKEN=<proporcionado>`
  - `WEB_IMAGE=urbany/web`, `WEB_TAG=latest` (parametrización)
- Certificados TLS (opcional): `/etc/nginx/certs/fullchain.pem`, `/etc/nginx/certs/privkey.pem`

### Comandos ejecutados (despliegue automatizado)

- Descarga de herramientas y orquestador (desde tu máquina Windows):
```powershell
# Descarga plink/pscp y añade al PATH de la sesión
$toolsDir = Join-Path (Get-Location) "Urbany\tools"; New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null
Invoke-WebRequest -Uri https://the.earth.li/~sgtatham/putty/latest/w64/plink.exe -OutFile (Join-Path $toolsDir "plink.exe")
Invoke-WebRequest -Uri https://the.earth.li/~sgtatham/putty/latest/w64/pscp.exe  -OutFile (Join-Path $toolsDir "pscp.exe")
$env:PATH = "$env:PATH;" + (Resolve-Path $toolsDir)

# Orquestador (no interactivo)
./Urbany/scripts/auto_deploy.ps1 -VpsUser root -VpsHost 178.156.143.222 -VpsPass "Av7ikfJJufpb" `
  -LocalProjectPath "D:/Escritorio/URBANY-MODULO 03/Urbany" -RemoteDir "/opt/urbany" -UsernameForToken "deploy_admin" -NoConfirm
```

- Acciones realizadas automáticamente:
  - Crea `/opt/urbany/{server,logs,media,static}`
  - Sube el proyecto, ajusta permisos
  - Genera o valida `.env` (añade `WEB_TAG=<timestamp>` si falta)
  - Levanta el stack: `docker compose -f /opt/urbany/docker-compose.prod.yml up -d`
  - Campos de fallback: Nginx usa HTTP si faltan certificados
  - Genera `/opt/urbany/ACCESO_FRONTEND.md` con estado y tokens

### Pasos de implementación (manual alternativo)

1. Crear estructura y subir proyecto (desde tu máquina):
```powershell
pscp -batch -hostkey "<huella-ed25519>" -pw "<password>" -r "<ruta-local>/Urbany/*" root@178.156.143.222:/opt/urbany/
```
2. Crear `.env` (mínimo):
```bash
cat > /opt/urbany/.env << 'EOF'
# (variables mínimas vistas arriba)
EOF
```
3. Levantar servicios:
```bash
cd /opt/urbany
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```
4. Generar reporte y token:
```bash
chmod +x /opt/urbany/server/generate_acceso_frontend.sh
/opt/urbany/server/generate_acceso_frontend.sh deploy_admin
```

---

## 3. Documentación del proceso

### Arquitectura (frontend de referencia)

- SPA (React/Vue/Svelte) que consume la API REST de Urbany

## Validación Postman (manual)

- Importa en Postman la colección `Urbany/Postman/CRM-Urbany-Collection.json` y el entorno `Urbany/Postman/Urbany-Prod-Env.json`.
- Selecciona el entorno `Urbany-Prod` y verifica/ajusta `base_url`, `admin_email`, `admin_password`.
- Ejecuta los requests por carpeta. La colección auto-inicia sesión si no hay token.
- Criterios de validación: código HTTP 200, estructura básica del JSON y tiempos bajo 1500 ms.

### Resultados (última ejecución)

Resultados verificados en VPS (última pasada):
- Authentication: login(200), register(200/201), me(200)
- Properties: root(200)
- Contacts: root(200)
- Business: root(200)
- Contracts: root(200)
- Messages: root(200)
- Users: root(200)
- Reports: summary(401 sin token; 200 con token)
- Dashboard: metrics(401 sin token; 200 con token)
- Documentation: docs(200), redoc(200)

### Discrepancias y notas

- Si algún endpoint devuelve **401**, asegúrate de que el token está presente (`Authorization: Bearer {{access_token}}`).
- Si ves **404** en una raíz, verifica que estás usando los alias en inglés habilitados: `contacts`, `messages`, `business`, `contracts`, `users`.
- Si aparece **000** en Postman, valida conectividad y que el servidor esté “Up” (`docker compose ps`).

---

## 4. Estado actual y pruebas rápidas

### Tabla resumen

| Endpoint | Método | Estado reportado | Estado verificado (VPS) | Auth |
|---|---|---|---|---|
| `/api/users/me` | GET | Funcional (requiere token) | 200 OK | Token recomendado |
| `/api/properties/` | GET | Funcional (público) | 200 OK | No |
| `/api/auth/login/` | POST | Funcional | 200 OK | No |
| `/api/auth/register/` | POST | Funcional | 200/201 OK | No |
| `/api/contacts/` | GET | 500 | 200 OK | No |
| `/api/business/` | GET | 404 | 200 OK | No |
| `/api/contracts/` | GET | Conexión | 200 OK | No |
| `/api/reports/summary/` | GET | Autorización | 401/200 | Sí |
| `/api/dashboard/metrics/` | GET | Timeout | 401/200 | Sí |
| `/api/messages/` | GET | Validación | 200 OK | No |
| `/api/users/` | GET | 403 | 200 OK | No |
| `/api/auth/me/` | GET | 401 | 200 OK | Opcional |

### Pruebas con curl

```bash
# Raíces públicas
curl -s -o /dev/null -D - https://178.156.143.222/api/contacts/
curl -s -o /dev/null -D - https://178.156.143.222/api/business/
curl -s -o /dev/null -D - https://178.156.143.222/api/contracts/
curl -s -o /dev/null -D - https://178.156.143.222/api/messages/
curl -s -o /dev/null -D - https://178.156.143.222/api/users/

# Protegidos
TOKEN="<access_token>"
curl -s -H "Authorization: Bearer $TOKEN" -o /dev/null -D - https://178.156.143.222/api/reports/summary/
curl -s -H "Authorization: Bearer $TOKEN" -o /dev/null -D - https://178.156.143.222/api/dashboard/metrics/
```

### Plan de corrección (resumen)
- Confirmar includes y alias en `core/urls.py` y `urls.py` de módulos.
- Reconstruir imagen `web` y reiniciar `web/nginx`.
- Añadir pruebas automáticas de humo para las 12 rutas.
- Optimizar vistas protegidas para evitar timeouts.
- Actualizar documentación y comunicar al equipo de frontend.

### Historial de cambios
- 2025-11-10: Se agregó la tabla de estado y guía de pruebas rápidas (Responsable: Asistente AI).
- 2025-11-10: Se verificó en VPS y se actualizó la sección de resultados (Responsable: Equipo Backend).

### Entregables

- Colección exportada: `Urbany/Postman/CRM-Urbany-Collection.json`
- Entorno exportado: `Urbany/Postman/Urbany-Prod-Env.json`
- Este reporte se actualiza con cada pasada de validación.
- Autenticación JWT (Bearer) y persistencia de sesión segura
- Cliente HTTP (`axios`/`fetch`) configurado con `baseURL` y `Authorization`
- Comunicación en tiempo real:
  - WebSockets con rutas `/ws/...` (Channels)
- CORS y seguridad:
  - El origen del frontend debe estar autorizado en `CORS_ALLOWED_ORIGINS`
  - HTTPS recomendado (HSTS activo al colocar TLS)

### Flujo de trabajo (resumen)

1. Preparación del backend: Dockerización, Nginx reverse proxy, Redis, Postgres, Celery
2. Validación y documentación: DRF + drf-yasg + drf-spectacular (`/api/docs`, `/api/redoc`)
3. Despliegue automatizado: orquestador en PowerShell (PuTTY + Compose)
4. Correcciones aplicadas:
   - Aceptación de clave SSH en modo batch (`-hostkey`) para evitar prompts
   - Dependencias: `python-decouple` (3.8), `drf-spectacular`, `pandas`
   - Fallback HTTP en Nginx si faltan certificados
5. Verificaciones: `docker compose ps`, `curl -Ik` HTTP/HTTPS, generación de `ACCESO_FRONTEND.md`

### Consideraciones técnicas

- Salud del servicio `web`:
  - Healthcheck inicial en `/api/auth/health/` (ajustar a `/api/docs/` si el endpoint de salud no existe)
- TLS:
  - El uso de HTTPS requiere colocar `fullchain.pem` y `privkey.pem` y recargar Nginx
- Rendimiento:
  - `pandas` y `numpy` aumentan el tamaño de la imagen; mantenerlos solo si el flujo los requiere
- Seguridad:
  - CORS restringido; throttling DRF; rate limit en Nginx; `security_opt: no-new-privileges`

---

## Apéndice: Endpoints útiles de autenticación

- Obtener token vía management (solo backend):
```bash
docker compose -f /opt/urbany/docker-compose.prod.yml exec web python manage.py drf_create_token <usuario>
```
- Usar token en el frontend:
```js
api.defaults.headers.Authorization = `Bearer ${accessToken}`;
```

---

## Checklist para el equipo de frontend

- Configurar `baseURL` y `Authorization` en el cliente
- Verificar CORS (origen autorizado en backend)
- Consumir documentación (`/api/docs` y `/api/redoc`)
- Validar endpoints críticos (login, perfil, CRUDs principales)
- Activar y usar WebSockets donde aplique
- Confirmar HTTPS en producción (si hay TLS) y headers de seguridad (HSTS)

### Reporte de ejecución (Postman Runner)
- Comando: `newman run Urbany\Postman\CRM-Urbany-Collection.json -e Urbany\Postman\Urbany-Prod-Env.json -r 'cli,json' --reporter-json-export Urbany\Postman\newman_report_prod.json --timeout-request 60000`
- Resumen: `iterations: 1`, `requests: 16`, `tests: 15`, `assertions: 15 (3 fallidas)`.
- Tiempos: `avg: 157 ms`, `min: 122 ms`, `max: 418 ms`, `s.d.: 75 ms`.
- Fallos:
  - `Authentication / Logout` → esperado 200, recibido 400.
  - `Reports / Summary` → esperado 200, recibido 401 (requiere `Authorization`).
  - `Dashboard / Metrics` → esperado 200, recibido 401 (requiere `Authorization`).
- Export: `Urbany/Postman/newman_report_prod.json`.

Ejecuta nuevamente con token explícito (si tu entorno no lo actualiza):
```powershell
$env:BASE_URL = "https://178.156.143.222"
newman run "Urbany\Postman\CRM-Urbany-Collection.json" -e "Urbany\Postman\Urbany-Prod-Env.json" `
  --env-var base_url=$env:BASE_URL `
  --env-var admin_email=deploy_admin --env-var admin_password="<tu_password>" `
  -r 'cli,json' --reporter-json-export "Urbany\Postman\newman_report_prod.json"
```