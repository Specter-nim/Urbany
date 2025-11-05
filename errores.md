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