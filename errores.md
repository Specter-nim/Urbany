# Informe de Errores en el Despliegue de Urbany

Este documento resume todos los **errores** encontrados durante el despliegue de Urbany en el VPS y las soluciones aplicadas para corregirlos.

---

## 1) Error en `ALLOWED_HOSTS` de Django

### **Descripción del error:**
El contenedor `web` muestra el siguiente error:

Invalid HTTP_HOST header: 'localhost:8000'. You may need to add 'localhost' to ALLOWED_HOSTS.

markdown
Copiar código

### **Causa:**
Este error ocurre porque Django no reconoce `localhost:8000` como un host permitido en la configuración de `ALLOWED_HOSTS`.

### **Solución:**
1. Abre el archivo `settings.py` en tu proyecto Django.
2. Encuentra la configuración `ALLOWED_HOSTS`.
3. Añade `localhost` y la IP pública de tu VPS (en este caso `178.156.143.222`):

```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '178.156.143.222']
Guarda el archivo y reinicia el contenedor web:

bash
Copiar código
docker compose -f docker-compose.prod.yml restart web
2) Error en Celery: ProgrammingError: relation "users_user" does not exist
Descripción del error:
Los contenedores celery y celery_beat muestran el siguiente error relacionado con la base de datos:

arduino
Copiar código
django.db.utils.ProgrammingError: relation "users_user" does not exist
Causa:
Este error ocurre porque las migraciones de Django no se han aplicado correctamente, y la tabla users_user (que probablemente es parte de tu modelo de usuarios) no existe en la base de datos.

Solución:
Detén y levanta nuevamente los contenedores para asegurarte de que la configuración de Celery esté correcta:

bash
Copiar código
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
Aplica las migraciones manualmente para crear las tablas necesarias en la base de datos:

bash
Copiar código
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
Reinicia los contenedores de Celery para aplicar los cambios:

bash
Copiar código
docker compose -f docker-compose.prod.yml restart celery celery_beat
3) Error en Celery: Unable to load celery application
Descripción del error:
El contenedor celery muestra el siguiente error al intentar iniciar:

pgsql
Copiar código
Error: Invalid value for '-A' / '--app': Unable to load celery application.
Module 'core' has no attribute 'celery'
Causa:
Este error se debe a que Celery no encuentra el archivo de configuración adecuado en el módulo core. Probablemente, no tienes un archivo celery.py dentro de tu directorio core o la configuración está mal.

Solución:
Crea el archivo celery.py en el directorio core/ con el siguiente contenido:

python
Copiar código
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establece el valor de la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Usar la configuración de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas de Django
app.autodiscover_tasks()
En el archivo core/__init__.py, asegúrate de que haya una línea para importar la aplicación Celery:

python
Copiar código
from __future__ import absolute_import, unicode_literals

# Esto asegura que la aplicación Celery se ejecute al iniciar el proyecto
from .celery import app as celery_app

__all__ = ('celery_app',)
Reinicia los contenedores de Celery:

bash
Copiar código
docker compose -f docker-compose.prod.yml restart celery celery_beat
4) Error en las Migraciones de Celery Beat
Descripción del error:
El contenedor celery_beat muestra el siguiente error relacionado con las migraciones:

arduino
Copiar código
psycopg2.errors.UndefinedTable: relation "users_user" does not exist
Causa:
Este error es el mismo que el error de Celery, y ocurre porque las migraciones no se han ejecutado correctamente.

Solución:
Aplica las migraciones manualmente en el contenedor web:

bash
Copiar código
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
Después, reinicia los contenedores de Celery y Celery Beat:

bash
Copiar código
docker compose -f docker-compose.prod.yml restart celery celery_beat
5) Error en la Base de Datos: relation "users_user" does not exist
Descripción del error:
Este error en la base de datos indica que la tabla users_user no existe. Es probable que las migraciones necesarias no se hayan ejecutado o que no se haya creado correctamente la base de datos.

Causa:
Este error está relacionado con el hecho de que la base de datos no tiene las tablas necesarias. Las migraciones de Django no se han ejecutado completamente o la base de datos está en un estado inconsistente.

Solución:
Verifica que la base de datos esté activa y que el contenedor db esté corriendo:

bash
Copiar código
docker compose -f docker-compose.prod.yml ps
Reaplica las migraciones en el contenedor web:

bash
Copiar código
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
Si las migraciones siguen sin ejecutarse correctamente, intenta crear la base de datos desde cero o elimina el contenedor de la base de datos y vuelve a crear las migraciones:

bash
Copiar código
docker compose -f docker-compose.prod.yml down
docker volume prune  # Elimina volúmenes para limpiar la base de datos
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
6) Otros Errores de Configuración y Soluciones
Error en el contenedor celery_beat y celery relacionados con la aplicación no cargada correctamente:
pgsql
Copiar código
Error: Invalid value for '-A' / '--app': Unable to load celery application.
Module 'core' has no attribute 'celery'
Solución:
Verifica que el archivo celery.py esté correctamente ubicado en el directorio core/ y que se haga correctamente la importación desde el archivo __init__.py.
# README de Errores — Estado actual de Endpoints API

Fecha: 2025-11-10
Entorno: Producción (VPS 178.156.143.222)

Este documento registra el estado actual de los endpoints de la API, discrepancias observadas, instrucciones de prueba, errores conocidos con posibles soluciones y el plan de corrección. Incluye un historial de cambios con fechas y responsables.

## Tabla resumen de estado

| Endpoint | Método | Estado reportado | Estado verificado (VPS) | Requisitos | Notas |
|---|---|---|---|---|---|
| `http://178.156.143.222/api/users/me` | GET | Funcional (requiere token) | 200 OK | Token recomendado | Sin token devuelve `authenticated:false`; con token devuelve perfil. |
| `http://178.156.143.222/api/properties/` | GET | Funcional (público) | 200 OK | Público | Raíz accesible; CRUD puede requerir token. |
| `http://178.156.143.222/api/auth/login/` | POST | Funcional (autenticación) | 200 OK | Público | Devuelve tokens JWT y datos mínimos del usuario. |
| `http://178.156.143.222/api/auth/register/` | POST | Funcional (registro) | 200/201 OK | Público | Dependiendo de validación, puede responder 200 o 201. |
| `http://178.156.143.222/api/contacts/` | GET | Error 500 | 200 OK | Público | Raíz pública añadida; endpoints CRUD pueden requerir token. |
| `http://178.156.143.222/api/business/` | GET | Error 404 | 200 OK | Público | Raíz pública añadida; CRUD protegido. |
| `http://178.156.143.222/api/contracts/` | GET | Error de conexión | 200 OK | Público | Servicio operativo tras rebuild; CRUD protegido. |
| `http://178.156.143.222/api/reports/summary/` | GET | Error de autorización | 401 Unauthorized | Token requerido | Protegido; requiere `Authorization: Bearer <token>`. |
| `http://178.156.143.222/api/dashboard/metrics/` | GET | Error de timeout | 401 Unauthorized | Token requerido | Protegido; con token responde 200. |
| `http://178.156.143.222/api/messages/` | GET | Error de validación | 200 OK | Público | Raíz pública; rutas POST/CRUD requieren token. |
| `http://178.156.143.222/api/users/` | GET | Error 403 | 200 OK | Público | Raíz pública; listado completo suele requerir token/rol. |
| `http://178.156.143.222/api/auth/me/` | GET | Error 401 | 200 OK | Token opcional | Sin token: estado; con token: perfil. |

Notas:
- “Estado verificado” se obtuvo con `curl` desde el VPS, vía Nginx (`http://127.0.0.1/...`) y, cuando aplica, directamente al contenedor web.
- Las rutas de raíz en inglés (`contacts`, `messages`, `business`, `contracts`, `users`) fueron habilitadas como públicas para pruebas de disponibilidad; los sub-endpoints de negocio siguen protegidos.

## Instrucciones para probar los endpoints

### Curl rápido (sin token)

```bash
# Probar raíces públicas
curl -s -o /dev/null -D - http://178.156.143.222/api/contacts/
curl -s -o /dev/null -D - http://178.156.143.222/api/business/
curl -s -o /dev/null -D - http://178.156.143.222/api/contracts/
curl -s -o /dev/null -D - http://178.156.143.222/api/messages/
curl -s -o /dev/null -D - http://178.156.143.222/api/users/

# Endpoints protegidos (esperar 401 si no hay token)
curl -s -o /dev/null -D - http://178.156.143.222/api/reports/summary/
curl -s -o /dev/null -D - http://178.156.143.222/api/dashboard/metrics/
```

### Obtener token y probar protegidos

```bash
# Obtener token (reemplazar credenciales)
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"deploy_admin","password":"<tu_password>"}' \
  http://178.156.143.222/api/auth/login/ | jq -r '.access'

# Usar el token
TOKEN="<access_token>"
curl -s -H "Authorization: Bearer $TOKEN" -o /dev/null -D - http://178.156.143.222/api/reports/summary/
curl -s -H "Authorization: Bearer $TOKEN" -o /dev/null -D - http://178.156.143.222/api/dashboard/metrics/
```

### Postman
- Importar `Urbany/Postman/CRM-Urbany-Collection.json` y `Urbany/Postman/Urbany-Prod-Env.json`.
- Seleccionar entorno `Urbany-Prod` y ejecutar la colección; el pre-request hace login automáticamente si falta token.

## Errores conocidos y posibles soluciones

- `contacts/` (500 reportado):
  - Posible causa: vista o serializer disparando excepción.
  - Solución: revisar logs del contenedor web (`docker compose logs web`), validar `contacts/views.py` y tipos de datos.

- `business/` (404 reportado):
  - Posible causa: patrón de URL no incluido o conflicto de prefijos.
  - Solución: confirmar `core/urls.py` incluye `api/business/` y que `business/urls.py` expone raíz.

- `contracts/` (error de conexión reportado):
  - Posible causa: contenedor reiniciando o Nginx upstream caído.
  - Solución: `docker compose ps`, reiniciar `web` y `nginx`, verificar healthcheck.

- `reports/summary/` (autorización):
  - Comportamiento esperado: 401 sin token; 200 con `Authorization: Bearer` válido.
  - Solución: obtener token de `/api/auth/login/` y reenviar.

- `dashboard/metrics/` (timeout reportado):
  - Posible causa: consultas pesadas o índices faltantes.
  - Solución: validar la vista `MetricsListView`, añadir paginación/limit, revisar EXPLAIN si aplica.

- `messages/` (validación reportada):
  - Posible causa: cuerpo JSON inválido en POST.
  - Solución: revisar schema en `messaging/serializers.py`, enviar campos requeridos.

- `users/` (403 reportado):
  - Comportamiento esperado: listar usuarios requiere token y permisos.
  - Solución: usar token de admin/rol adecuado.

- `auth/me/` (401 reportado):
  - Comportamiento esperado: 200 sin token con `authenticated:false`; 200 con token y datos.
  - Solución: enviar `Authorization: Bearer <token>`.

## Plan de corrección

1. Revisar y asegurar inclusión de rutas en `core/urls.py` (raíces públicas y alias en inglés).
2. Verificar `urls.py` de módulos (`contacts`, `business`, `contracts`, `messaging`, `users`).
3. Reconstruir imagen `web` y redeploy (`docker compose -f docker-compose.prod.yml build web && up -d`).
4. Añadir pruebas de humo con `curl` y Postman (sin y con token) para los 12 endpoints.
5. Optimizar vistas protegidas (`reports/summary`, `dashboard/metrics`) para evitar timeouts.
6. Documentar cambios en `FRONTEND.MD` y `ENDPOINTS.md` con estado y requisitos de autenticación.

## Historial de cambios

- 2025-11-10 — Responsable: Asistente AI
  - Documentado estado actual y discrepancias reportadas vs. verificado.
  - Añadida tabla de estado, instrucciones de prueba y plan de corrección.

- 2025-11-10 — Responsable: Equipo Backend
  - Actualizadas rutas públicas de raíz en `core/urls.py`.
  - Reconstruida imagen `web` y verificados endpoints en VPS.