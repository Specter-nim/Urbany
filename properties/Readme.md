# Endpoints de Properties

## TipoPropiedad

### Listar tipos de propiedad
- **URL:** `/api/properties/tipo-propiedad/`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de todos los tipos de propiedad registrados.
- **Autenticación:** JWT requerida (Authorization: Bearer <token>)
- **Respuesta ejemplo:**
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"nombre": "Campo"
		}
	]
}
```

### Crear tipo de propiedad
- **URL:** `/api/properties/tipo-propiedad/`
- **Método:** `POST`
- **Descripción:** Crea un nuevo tipo de propiedad.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"nombre": "Departamento"
}
```
- **Respuesta ejemplo:**
```json
{
	"nombre": "Departamento"
}
```

### Detalle, actualizar y eliminar tipo de propiedad
- **URL:** `/api/properties/tipo-propiedad/{id}/`
- **Métodos:** `GET`, `PUT`, `DELETE`
- **Descripción:** Permite ver, actualizar o eliminar un tipo de propiedad específico.
- **Autenticación:** JWT requerida

## Propiedad

### Listar propiedades
- **URL:** `/api/properties/propiedad/`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de todas las propiedades registradas.
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"tipo_propiedad": 1,
			"tipo_operacion": "venta",
			"amoblado": false,
			"permuta": false,
			"descripcion": "Casa amplia con jardín",
			"estado": "activa",
			"sitio_web": "https://ejemplo.com",
			"video_url": null,
			"es_borrador": false,
			"fecha_creacion": "2025-10-13T12:00:00Z",
			"publicada": true,
			"precio": 120000.00,
			"precio_mantenimiento": 500.00,
			"id_inmobiliaria": 1
		}
	]
}
```

### Crear propiedad
- **URL:** `/api/properties/propiedad/`
- **Método:** `POST`
- **Descripción:** Crea una nueva propiedad. Debes enviar todos los campos obligatorios.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"tipo_propiedad": 1,
	"tipo_operacion": "venta",
	"amoblado": false,
	"permuta": false,
	"descripcion": "Casa amplia con jardín",
	"estado": "activa",
	"sitio_web": "https://ejemplo.com",
	"video_url": null,
	"es_borrador": false,
	"publicada": true,
	"precio": 120000.00,
	"precio_mantenimiento": 500.00,
	"id_inmobiliaria": 1
}
```

### Detalle, actualizar y eliminar propiedad
- **URL:** `/api/properties/propiedad/{id}/`
- **Métodos:** `GET`, `PUT`, `PATCH`, `DELETE`
- **Descripción:** Permite ver, actualizar o eliminar una propiedad específica.
- **Autenticación:** JWT requerida


## UbicacionPropiedad

### Listar ubicaciones de propiedad
- **URL:** `/api/properties/ubicacion-propiedad/`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de ubicaciones de propiedades.
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"id_propiedad": 1,
			"direccion": "Av. Siempre Viva 123",
			"departamento": "Lima",
			"provincia": "Lima",
			"distrito": "Miraflores"
		}
	]
}
```

### Crear ubicación de propiedad
- **URL:** `/api/properties/ubicacion-propiedad/`
- **Método:** `POST`
- **Descripción:** Crea una nueva ubicación para una propiedad.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"id_propiedad": 1,
	"direccion": "Av. Siempre Viva 123",
	"departamento": "Lima",
	"provincia": "Lima",
	"distrito": "Miraflores"
}
```

---

## SuperficiePropiedad

### Listar superficies de propiedad
- **URL:** `/api/properties/superficie-propiedad/`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de superficies de propiedades (casas, departamentos, oficinas, etc.).
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"id_propiedad": 1,
			"area_techada": 120.5,
			"area_total": 150.0,
			"area_descubierta": 20.0,
			"area_terreno": 200.0,
			"area_semicubierta": 10.0
		}
	]
}
```

### Crear superficie de propiedad
- **URL:** `/api/properties/superficie-propiedad/`
- **Método:** `POST`
- **Descripción:** Crea una nueva superficie para una propiedad.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"id_propiedad": 1,
	"area_techada": 120.5,
	"area_total": 150.0,
	"area_descubierta": 20.0,
	"area_terreno": 200.0,
	"area_semicubierta": 10.0
}
```

---

## SuperficieTerreno

### Listar superficies de terreno
- **URL:** `/api/properties/superficie-terreno/`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de superficies de terrenos (campos, fincas, etc.).
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"id_propiedad": 1,
			"metros_frente": 30.0,
			"metros_fondo": 50.0,
			"area_total": 1500.0,
			"area_construible": 1200.0,
			"forma_terreno": "regular"
		}
	]
}
```

### Crear superficie de terreno
- **URL:** `/api/properties/superficie-terreno/`
- **Método:** `POST`
- **Descripción:** Crea una nueva superficie de terreno para una propiedad.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"id_propiedad": 1,
	"metros_frente": 30.0,
	"metros_fondo": 50.0,
	"area_total": 1500.0,
	"area_construible": 1200.0,
	"forma_terreno": "regular"
}
```

---

## InformacionExtraPropiedad

### Listar información extra de propiedad
- **URL:** `/api/properties/informacion-extra-propiedad/`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de información extra de propiedades.
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"id_propiedad": 1,
			"antiguedad": "a estrenar",
			"años_antiguedad": null
		}
	]
}
```

### Crear información extra de propiedad
- **URL:** `/api/properties/informacion-extra-propiedad/`
- **Método:** `POST`
- **Descripción:** Crea información extra para una propiedad.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"id_propiedad": 1,
	"antiguedad": "otro",
	"años_antiguedad": 15
}
```

## Ambientes

### Listar ambientes
- **URL:** `/api/properties/ambientes/`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de ambientes disponibles (ejemplo: dormitorio, baño, cocina, etc.).
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"count": 2,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"nombre": "Dormitorio"
		},
		{
			"id": 2,
			"nombre": "Baño"
		}
	]
}
```

### Crear ambiente
- **URL:** `/api/properties/ambientes/`
- **Método:** `POST`
- **Descripción:** Crea un nuevo ambiente.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"nombre": "Cocina"
}
```

---

## AmbientePropiedad

### Listar ambientes de propiedad
- **URL:** `/api/properties/ambiente-propiedad/`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de ambientes asociados a propiedades.
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"id_propiedad": 1,
			"id_ambiente": 2,
			"cantidad": 3
		}
	]
}
```

### Crear ambiente de propiedad
- **URL:** `/api/properties/ambiente-propiedad/`
- **Método:** `POST`
- **Descripción:** Asocia un ambiente a una propiedad.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"id_propiedad": 1,
	"id_ambiente": 2,
	"cantidad": 3
}
```

## ImagenesPropiedad

### Listar imágenes de propiedad
- **URL:** `	`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de imágenes asociadas a propiedades.
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"id_propiedad": 1,
			"imagen": "http://localhost:8000/media/imagenes_propiedades/ejemplo.jpg"
		}
	]
}
```

### Crear imagen de propiedad (multipart/form-data)
- **URL:** `/api/properties/imagenes-propiedad/`
- **Método:** `POST`
- **Descripción:** Sube una imagen asociada a una propiedad. Se debe enviar el archivo como multipart/form-data.
- **Autenticación:** JWT requerida
- **Body ejemplo (form-data):**
| Key           | Value                | Type  |
|---------------|----------------------|-------|
| id_propiedad  | 1                    | Text  |
| imagen        | [archivo.jpg/.png]   | File  |

---

## Servicios

### Listar servicios
- **URL:** `/api/properties/servicios/`
- **Método:** `GET`
- **Descripción:** Devuelve una lista paginada de servicios disponibles (ejemplo: agua, luz, gas, internet, etc.).
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"count": 2,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"nombre": "Agua"
		},
		{
			"id": 2,
			"nombre": "Internet"
		}
	]
}
```

### Crear servicio
- **URL:** `/api/properties/servicios/`
- **Método:** `POST`
- **Descripción:** Crea un nuevo servicio.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"nombre": "Gas"
}
```
## PrecioPropiedad

### Consultar precio de propiedad
- **URL:** `/api/properties/precio-propiedad/{id}/`
- **Método:** `GET`
- **Descripción:** Devuelve el id, precio y precio de mantenimiento de una propiedad específica.
- **Autenticación:** JWT requerida
- **Respuesta ejemplo:**
```json
{
	"id": 1,
	"precio": 120000.00,
	"precio_mantenimiento": 500.00
}
```

### Actualizar precio de propiedad
- **URL:** `/api/properties/precio-propiedad/{id}/`
- **Método:** `PATCH`
- **Descripción:** Actualiza el precio y/o precio de mantenimiento de una propiedad existente.
- **Autenticación:** JWT requerida
- **Body ejemplo:**
```json
{
	"precio": 130000.00
}
```
- **Respuesta ejemplo:**
```json
{
	"id": 1,
	"precio": 130000.00,
	"precio_mantenimiento": 500.00
}
```
---



