# Endpoints - Inmobiliaria

Esta sección documenta los endpoints disponibles para la gestión de inmobiliarias y sus ubicaciones.


## Endpoints principales

### 1. Inmobiliarias

- **Listar inmobiliarias**
    - `GET /api/inmobiliaria/inmobiliarias/`
    - Respuesta:
        ```json
        {
            "count": 1,
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": 1,
                    "logo": "http://localhost:8000/media/logo_inmobiliaria/DFD_1.png",
                    "nombre": "Probando",
                    "telefono": "",
                    "celular": "",
                    "email": null,
                    "facebook": "https://facebook.com/ejemplo",
                    "instagram": "https://instagram.com/ejemplo",
                    "twitter": "https://twitter.com/ejemplo",
                    "youtube": "https://youtube.com/ejemplo",
                    "fecha_creacion": "2025-10-14T11:01:58.458055-06:00",
                    "fecha_actualizacion": "2025-10-14T12:43:38.470369-06:00"
                }
            ]
        }
        ```

- **Crear inmobiliaria**
    - `POST /api/inmobiliaria/inmobiliarias/`
    - Request (JSON):
        ```json
        {
            "logo": "DFD_1.png",
            "nombre": "Probando",
            "telefono": "",
            "celular": "",
            "email": "ejemplo@correo.com",
            "facebook": "https://facebook.com/ejemplo",
            "instagram": "https://instagram.com/ejemplo",
            "twitter": "https://twitter.com/ejemplo",
            "youtube": "https://youtube.com/ejemplo"
        }
        ```
    - Respuesta (JSON):
        ```json
        {
            "id": 2,
            "logo": "http://localhost:8000/media/logo_inmobiliaria/DFD_1.png",
            "nombre": "Probando",
            "telefono": "",
            "celular": "",
            "email": "ejemplo@correo.com",
            "facebook": "https://facebook.com/ejemplo",
            "instagram": "https://instagram.com/ejemplo",
            "twitter": "https://twitter.com/ejemplo",
            "youtube": "https://youtube.com/ejemplo",
            "fecha_creacion": "2025-10-14T13:00:00.000000-06:00",
            "fecha_actualizacion": "2025-10-14T13:00:00.000000-06:00"
        }
        ```

- **Actualizar inmobiliaria**
    - `PUT /api/inmobiliaria/inmobiliarias/{id}/`
    - Request (JSON):
        ```json
        {
            "logo": "DFD_1.png",
            "nombre": "Probando Actualizado",
            "telefono": "123456789",
            "celular": "987654321",
            "email": "nuevo@correo.com",
            "facebook": "https://facebook.com/nuevo",
            "instagram": "https://instagram.com/nuevo",
            "twitter": "https://twitter.com/nuevo",
            "youtube": "https://youtube.com/nuevo"
        }
        ```
    - Respuesta (JSON):
        ```json
        {
            "logo": "http://localhost:8000/media/logo_inmobiliaria/DFD_1.png",
            "nombre": "Probando Actualizado",
            "telefono": "123456789",
            "celular": "987654321",
            "email": "nuevo@correo.com",
            "facebook": "https://facebook.com/nuevo",
            "instagram": "https://instagram.com/nuevo",
            "twitter": "https://twitter.com/nuevo",
            "youtube": "https://youtube.com/nuevo",
            "fecha_creacion": "2025-10-14T11:01:58.458055-06:00",
            "fecha_actualizacion": "2025-10-14T14:00:00.000000-06:00"
        }
        ```
- **Eliminar inmobiliaria**
    - `DELETE /api/inmobiliaria/inmobiliarias/{id}/`
    - Descripción: Elimina la inmobiliaria con el id especificado. No requiere body, solo el id en la URL.
    - Respuesta (JSON):
        ```json
        {
            "detail": "Inmobiliaria eliminada correctamente."
        }
        ```


### 2. Ubicación de Inmobiliaria

- **Listar ubicaciones**
    - `GET /api/inmobiliaria/ubicaciones/`
    - Respuesta:
    ```json
    {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 1,
                "direccion": "Av. Principal 123",
                "departamento": "Lima",
                "ciudad": "Lima",
                "distrito": "Miraflores",
                "latitud": "-12.123456",
                "longitud": "-77.123456",
                "id_inmobiliaria": 1
            }
        ]
    }
    ```

- **Crear ubicación**
    - `POST /api/inmobiliaria/ubicaciones/`
    - Request (JSON):
        ```json
        {
            "id_inmobiliaria": 1,
            "direccion": "Av. Principal 123",
            "departamento": "Lima",
            "ciudad": "Lima",
            "distrito": "Miraflores",
            "latitud": -12.123456,
            "longitud": -77.123456
        }
        ```
    - Respuesta (JSON):
        ```json
        {
            "id": 2,
            "id_inmobiliaria": 1,
            "direccion": "Av. Principal 123",
            "departamento": "Lima",
            "ciudad": "Lima",
            "distrito": "Miraflores",
            "latitud": -12.123456,
            "longitud": -77.123456
        }
            ```

- **Actualizar ubicación**
    - `PUT /api/inmobiliaria/ubicaciones/{id}/`
    - Request (JSON):
        ```json
        {
            "id_inmobiliaria": 1,
            "direccion": "Av. Secundaria 456",
            "departamento": "Lima",
            "ciudad": "Lima",
            "distrito": "San Isidro",
            "latitud": -12.111111,
            "longitud": -77.111111
        }
        ```
    - Respuesta (JSON):
        ```json
        {
            "id": 1,
            "id_inmobiliaria": 1,
            "direccion": "Av. Secundaria 456",
            "departamento": "Lima",
            "ciudad": "Lima",
            "distrito": "San Isidro",
            "latitud": -12.111111,
            "longitud": -77.111111
        }
        ```

- **Eliminar ubicación**
    - `DELETE /api/inmobiliaria/ubicaciones/{id}/`
    - Descripción: Elimina la ubicación con el id especificado. No requiere body, solo el id en la URL.
    - Respuesta (JSON):
        ```json
        {
            "detail": "Ubicación eliminada correctamente."
        }
        ```

### 3. Redes Sociales de Inmobiliaria

- **Actualizar redes sociales**
    - `POST /api/inmobiliaria/inmobiliarias/{id}/redes-sociales/`
    - `PUT /api/inmobiliaria/inmobiliarias/{id}/redes-sociales/`
    - Request (JSON):
        ```json
        {
            "facebook": "https://facebook.com/nueva",
            "twitter": "https://twitter.com/nueva",
            "instagram": "https://instagram.com/nueva",
            "youtube": "https://youtube.com/nueva"
        }
        ```
    - Respuesta (JSON):
        ```json
        {
            "message": "Redes sociales actualizadas correctamente."
        }
        ```




