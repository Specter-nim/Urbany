# ENDPOINTS - CRM URBANY API

**Base URL**: `http://127.0.0.1:8000` | **Autenticación**: JWT Bearer Token | **Formato**: JSON

## 📊 Resumen de estado actual (Producción)

Fecha: 2025-11-10 | Entorno: `https://178.156.143.222/api/`

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

Notas:
- Los endpoints marcados como “401/200” requieren token para 200 OK; sin token responden 401.
- Las raíces públicas en inglés se habilitaron para pruebas de disponibilidad; los sub-endpoints de negocio mantienen controles de acceso.

## 🔎 Pruebas rápidas con curl

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

## 🛠 Plan de corrección y notas de implementación

1. Asegurar inclusión y orden de rutas en `core/urls.py` para alias en inglés y raíces públicas de prueba.
2. Verificar `urls.py` de módulos para exponer `path('', ...)` correcto.
3. Reconstruir la imagen `web` y reiniciar `web/nginx` tras cambios en código.
4. Implementar pruebas de humo (curl/Postman) para los 12 endpoints clave.
5. Optimizar vistas con posible timeout (`dashboard/metrics`) y asegurar autorización en `reports/summary`.

## 🧾 Historial de cambios

- 2025-11-10 — Se añadió resumen de estado, pruebas rápidas y plan de corrección (Responsable: Asistente AI).
- 2025-11-10 — Se verificó comportamiento en VPS y se ajustaron notas de autenticación (Responsable: Equipo Backend).


## 🔧 Configuración Completa de Postman

### Variables de Entorno
Crear una nueva colección en Postman y configurar las siguientes variables:

```json
{
  "base_url": "http://127.0.0.1:8000",
  "access_token": "",
  "refresh_token": "",
  "user_id": "",
  "admin_email": "admin@urbany.com",
  "admin_password": "admin123"
}
```

### Headers Globales
Configurar los siguientes headers a nivel de colección:
- `Content-Type: application/json`
- `Authorization: Bearer {{access_token}}`

### Script de Auto-Login
**Pre-request Script para Auto-Login:**
```javascript
// Auto-login si no hay token
if (!pm.environment.get("access_token")) {
    pm.sendRequest({
        url: pm.environment.get("base_url") + "/api/auth/login/",
        method: 'POST',
        header: {
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                email: pm.environment.get("admin_email"),
                password: pm.environment.get("admin_password")
            })
        }
    }, function (err, response) {
        if (response.code === 200) {
            const data = response.json();
            pm.environment.set("access_token", data.tokens.access);
            pm.environment.set("refresh_token", data.tokens.refresh);
        }
    });
}
```

### Script Post-Response para Login
**Agregar al endpoint de Login:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("access_token", response.tokens.access);
    pm.environment.set("refresh_token", response.tokens.refresh);
    pm.environment.set("user_id", response.user.id);
    console.log("Tokens guardados exitosamente");
}
```

### Credenciales de Prueba
- **Superusuario**: `admin@urbany.com` / `admin123`
- **Usuario de prueba**: `test@example.com` / `testpass123`

### URLs Importantes
- **API Base**: `http://127.0.0.1:8000/api/`
- **Documentación Swagger**: `http://127.0.0.1:8000/swagger/`
- **API Docs**: `http://127.0.0.1:8000/api/docs/`
- **Panel Admin**: `http://127.0.0.1:8000/admin/`
- **Health Check**: `http://127.0.0.1:8000/api/auth/health/`

### Códigos de Respuesta
- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Datos inválidos
- **401 Unauthorized**: Token no válido o faltante
- **403 Forbidden**: Sin permisos suficientes
- **404 Not Found**: Recurso no encontrado
- **405 Method Not Allowed**: Método HTTP no permitido

### Troubleshooting
- **Error 401**: Verificar token, puede haber expirado
- **Error 405**: Verificar método HTTP correcto
- **Error 400**: Verificar formato JSON y campos requeridos

---

## 🔐 AUTENTICACIÓN

### Registro de Usuario
```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "contraseña123",
  "password_confirm": "contraseña123",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```
**Respuesta (201)**:
```json
{
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "first_name": "Juan",
    "last_name": "Pérez"
  }
}
```

### Inicio de Sesión
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "contraseña123"
}
```
**Respuesta (200)**:
```json
{
  "message": "Login exitoso",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com"
  }
}
```

### Cerrar Sesión
```http
POST /api/auth/logout/
Authorization: Bearer {{access_token}}

{
  "refresh": "{{refresh_token}}"
}
```
**Respuesta (200)**:
```json
{
  "message": "Logout exitoso"
}
```

### Recuperación de Contraseña
```http
POST /api/auth/password-recovery/
Content-Type: application/json

{
  "email": "usuario@ejemplo.com"
}
```
**Respuesta (200)**:
```json
{
  "message": "Email de recuperación enviado"
}
```

### Verificación 2FA
```http
POST /api/auth/two-factor/
Authorization: Bearer {{access_token}}

{
  "code": "123456"
}
```
**Respuesta (200)**:
```json
{
  "message": "2FA verificado exitosamente",
  "verified": true
}
```

### Health Check
```http
GET /api/auth/health/
```
**Respuesta (200)**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-06T14:48:25.123456Z"
}
```

---

## 👥 USUARIOS

### Lista de Usuarios
```http
GET /api/users/?page=1&search=juan
Authorization: Bearer {{access_token}}
```
**Respuesta (200)**:
```json
{
  "count": 25,
  "next": "http://127.0.0.1:8000/api/users/?page=2",
  "results": [
    {
      "id": 1,
      "email": "usuario@ejemplo.com",
      "first_name": "Juan",
      "last_name": "Pérez",
      "is_active": true
    }
  ]
}
```

### Crear Usuario
```http
POST /api/users/
Authorization: Bearer {{access_token}}

{
  "email": "nuevo@ejemplo.com",
  "password": "contraseña123",
  "first_name": "Nuevo",
  "last_name": "Usuario"
}
```
**Respuesta (201)**:
```json
{
  "id": 2,
  "email": "nuevo@ejemplo.com",
  "first_name": "Nuevo",
  "last_name": "Usuario",
  "is_active": true
}
```

### Detalle de Usuario
```http
GET /api/users/1/
Authorization: Bearer {{access_token}}
```
**Respuesta (200)**:
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+52 55 1234 5678",
  "profile": {
    "date_of_birth": "1990-01-01",
    "gender": "M",
    "city": "Ciudad de México"
  }
}
```

### Actualizar Usuario
```http
PUT /api/users/1/
Authorization: Bearer {{access_token}}

{
  "first_name": "Juan Carlos",
  "last_name": "Pérez García"
}
```
**Respuesta (200)**:
```json
{
  "id": 1,
  "first_name": "Juan Carlos",
  "last_name": "Pérez García",
  "email": "usuario@ejemplo.com"
}
```

### Eliminar Usuario
```http
DELETE /api/users/1/
Authorization: Bearer {{access_token}}
```
**Respuesta (204)**: Sin contenido

### Mi Perfil
```http
GET /api/users/me/
Authorization: Bearer {{access_token}}
```
**Respuesta (200)**:
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "roles": ["user"]
}
```

### Cambiar Contraseña
```http
POST /api/users/change-password/
Authorization: Bearer {{access_token}}

{
  "old_password": "contraseña123",
  "new_password": "nuevaContraseña456",
  "new_password_confirm": "nuevaContraseña456"
}
```
**Respuesta (200)**:
```json
{
  "message": "Contraseña actualizada exitosamente"
}
```

### Asignar Rol
```http
POST /api/users/1/assign-role/
Authorization: Bearer {{access_token}}

{
  "role_id": 2
}
```
**Respuesta (200)**:
```json
{
  "message": "Rol asignado exitosamente",
  "user_role": {
    "user": 1,
    "role": "Manager",
    "assigned_at": "2025-01-06T14:48:25.123456Z"
  }
}
```

### Estadísticas de Usuarios
```http
GET /api/users/stats/
Authorization: Bearer {{access_token}}
```
**Respuesta (200)**:
```json
{
  "total_users": 150,
  "active_users": 142,
  "new_users_this_month": 12,
  "users_by_role": {
    "admin": 5,
    "manager": 15,
    "user": 130
  }
}
```

---

## 🔑 ROLES Y PERMISOS

### Lista de Roles
```http
GET /api/roles/
Authorization: Bearer {{access_token}}
```
**Respuesta (200)**:
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Admin",
      "description": "Administrador del sistema",
      "permissions_count": 15,
      "users_count": 5
    }
  ]
}
```

### Crear Rol
```http
POST /api/roles/
Authorization: Bearer {{access_token}}

{
  "name": "Manager",
  "description": "Gestor de propiedades"
}
```
**Respuesta (201)**:
```json
{
  "id": 2,
  "name": "Manager",
  "description": "Gestor de propiedades",
  "permissions": [],
  "created_at": "2025-01-06T14:48:25.123456Z"
}
```

### Detalle de Rol
```http
GET /api/roles/1/
Authorization: Bearer {{access_token}}
```
**Respuesta (200)**:
```json
{
  "id": 1,
  "name": "Admin",
  "description": "Administrador del sistema",
  "permissions": [
    {
      "id": 1,
      "name": "Can manage users",
      "codename": "manage_users"
    }
  ],
  "users": [
    {
      "id": 1,
      "email": "admin@ejemplo.com",
      "first_name": "Admin"
    }
  ]
}
```

### Actualizar Rol
```http
PUT /api/roles/1/
Authorization: Bearer {{access_token}}

{
  "name": "Super Admin",
  "description": "Administrador principal del sistema"
}
```
**Respuesta (200)**:
```json
{
  "id": 1,
  "name": "Super Admin",
  "description": "Administrador principal del sistema"
}
```

### Eliminar Rol
```http
DELETE /api/roles/1/
Authorization: Bearer {{access_token}}
```
**Respuesta (204)**: Sin contenido

### Agregar Permiso a Rol
```http
POST /api/roles/1/add-permission/
Authorization: Bearer {{access_token}}

{
  "permission_id": 3
}
```
**Respuesta (200)**:
```json
{
  "message": "Permiso agregado exitosamente",
  "role": "Admin",
  "permission": "Can edit properties"
}
```

### Remover Permiso de Rol
```http
POST /api/roles/1/remove-permission/
Authorization: Bearer {{access_token}}

{
  "permission_id": 3
}
```
**Respuesta (200)**:
```json
{
  "message": "Permiso removido exitosamente"
}
```

### Lista de Permisos
```http
GET /api/permissions/
Authorization: Bearer {{access_token}}
```
**Respuesta (200)**:
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Can manage users",
      "codename": "manage_users",
      "description": "Permite gestionar usuarios del sistema"
    }
  ]
}
```

### Crear Permiso
```http
POST /api/permissions/
Authorization: Bearer {{access_token}}

{
  "name": "Can view reports",
  "codename": "view_reports",
  "description": "Permite ver reportes del sistema"
}
```
**Respuesta (201)**:
```json
{
  "id": 11,
  "name": "Can view reports",
  "codename": "view_reports",
  "description": "Permite ver reportes del sistema"
}
```

### Estadísticas de Roles
```http
GET /api/roles/stats/
Authorization: Bearer {{access_token}}
```
**Respuesta (200)**:
```json
{
  "total_roles": 5,
  "total_permissions": 20,
  "most_assigned_role": "User",
  "roles_distribution": {
    "Admin": 5,
    "Manager": 15,
    "User": 130
  }
}
```

---

## 📚 DOCUMENTACIÓN API

### Esquema OpenAPI
```http
GET /api/schema/
```
**Respuesta (200)**: Esquema OpenAPI completo en formato JSON

### Swagger UI
```http
GET /swagger/
```
**Respuesta (200)**: Interfaz Swagger interactiva

### API Docs
```http
GET /api/docs/
```
**Respuesta (200)**: Documentación API interactiva

### ReDoc
```http
GET /redoc/
```
**Respuesta (200)**: Documentación ReDoc

---

## 📄 MÓDULO 4: CONTRATOS Y MENSAJERÍA

### 🏢 CONTRATOS - `/api/contratos/`

#### 1. Listar Contratos
**GET** `/api/contratos/`

**Descripción**: Obtiene lista paginada de contratos del usuario

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Query Parameters**:
- `page`: Número de página (default: 1)
- `page_size`: Elementos por página (default: 20)
- `search`: Búsqueda por título, cliente, dirección
- `contract_type`: Filtrar por tipo (Sale, Rent, Lease, Management)
- `status`: Filtrar por estado (Draft, Active, Signed, Completed, Cancelled, Expired)
- `priority`: Filtrar por prioridad (Low, Medium, High, Urgent)
- `ordering`: Ordenar por campo (-created_at, contract_value, etc.)

**Ejemplo**: `/api/contratos/?search=casa&status=Active&page=1`

**Respuesta Exitosa (200)**:
```json
{
  "count": 25,
  "next": "http://127.0.0.1:8000/api/contratos/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "contract_number": "CON-2025-001",
      "title": "Venta Casa Residencial",
      "contract_type": "Sale",
      "status": "Active",
      "priority": "High",
      "client_name": "Juan Pérez",
      "agent": "admin@urbany.com",
      "property_address": "Av. Principal 123, Ciudad",
      "contract_value": "2500000.00",
      "commission_rate": "3.50",
      "commission_amount": "87500.00",
      "start_date": "2025-01-01",
      "end_date": "2025-06-01",
      "signed_date": null,
      "created_at": "2025-01-06T10:30:00Z",
      "updated_at": "2025-01-06T10:30:00Z"
    }
  ]
}
```

---

#### 2. Crear Contrato
**POST** `/api/contratos/`

**Descripción**: Crea un nuevo contrato

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "title": "Arrendamiento Oficina Centro",
  "contract_type": "Lease",
  "status": "Draft",
  "priority": "Medium",
  "client_name": "Empresa ABC S.A.",
  "client_email": "contacto@empresaabc.com",
  "client_phone": "+52 55 1234 5678",
  "property_address": "Torre Corporativa, Piso 15",
  "property_type": "Oficina",
  "property_size": "250.00",
  "contract_value": "50000.00",
  "commission_rate": "5.00",
  "start_date": "2025-02-01",
  "end_date": "2025-02-01",
  "terms_and_conditions": "Contrato de arrendamiento por 12 meses..."
}
```

**Respuesta Exitosa (201)**:
```json
{
  "id": 26,
  "contract_number": "CON-2025-026",
  "title": "Arrendamiento Oficina Centro",
  "contract_type": "Lease",
  "status": "Draft",
  "priority": "Medium",
  "client_name": "Empresa ABC S.A.",
  "agent": "admin@urbany.com",
  "property_address": "Torre Corporativa, Piso 15",
  "contract_value": "50000.00",
  "commission_rate": "5.00",
  "commission_amount": "2500.00",
  "start_date": "2025-02-01",
  "end_date": "2025-02-01",
  "signed_date": null,
  "created_at": "2025-01-06T15:30:00Z",
  "updated_at": "2025-01-06T15:30:00Z"
}
```

---

#### 3. Detalle de Contrato
**GET** `/api/contratos/{id}/`

**Descripción**: Obtiene detalles completos de un contrato incluyendo pagos, documentos y notas

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Ejemplo**: `/api/contratos/1/`

**Respuesta Exitosa (200)**:
```json
{
  "id": 1,
  "contract_number": "CON-2025-001",
  "title": "Venta Casa Residencial",
  "contract_type": "Sale",
  "status": "Active",
  "priority": "High",
  "client_name": "Juan Pérez",
  "client_email": "juan@email.com",
  "client_phone": "+52 55 1234 5678",
  "agent": "admin@urbany.com",
  "property_address": "Av. Principal 123, Ciudad",
  "property_type": "Casa",
  "property_size": "180.50",
  "contract_value": "2500000.00",
  "commission_rate": "3.50",
  "commission_amount": "87500.00",
  "start_date": "2025-01-01",
  "end_date": "2025-06-01",
  "signed_date": null,
  "terms_and_conditions": "Términos y condiciones del contrato...",
  "payments": [
    {
      "id": 1,
      "payment_type": "Enganche",
      "amount": "500000.00",
      "due_date": "2025-01-15",
      "paid_date": null,
      "status": "Pending"
    }
  ],
  "documents": [
    {
      "id": 1,
      "document_type": "Contrato",
      "title": "Contrato Principal",
      "file": "/media/contracts/contrato_001.pdf",
      "uploaded_at": "2025-01-06T10:30:00Z"
    }
  ],
  "notes": [
    {
      "id": 1,
      "note_type": "General",
      "content": "Cliente interesado en cerrar pronto",
      "created_by": "admin@urbany.com",
      "created_at": "2025-01-06T11:00:00Z"
    }
  ],
  "created_at": "2025-01-06T10:30:00Z",
  "updated_at": "2025-01-06T10:30:00Z"
}
```

---

#### 4. Actualizar Contrato
**PUT** `/api/contratos/{id}/`

**Descripción**: Actualiza completamente un contrato

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "title": "Venta Casa Residencial - Actualizado",
  "status": "Signed",
  "priority": "High",
  "signed_date": "2025-01-06",
  "terms_and_conditions": "Términos actualizados..."
}
```

**Respuesta Exitosa (200)**:
```json
{
  "id": 1,
  "contract_number": "CON-2025-001",
  "title": "Venta Casa Residencial - Actualizado",
  "status": "Signed",
  "signed_date": "2025-01-06",
  "updated_at": "2025-01-06T16:00:00Z"
}
```

---

#### 5. Estadísticas de Contratos
**GET** `/api/contratos/stats/`

**Descripción**: Obtiene estadísticas generales de contratos del usuario

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "total_contracts": 25,
  "by_status": {
    "Draft": 5,
    "Active": 12,
    "Signed": 6,
    "Completed": 2,
    "Cancelled": 0,
    "Expired": 0
  },
  "by_type": {
    "Sale": 8,
    "Rent": 2,
    "Lease": 9,
    "Management": 6
  },
  "total_value": "15750000.00",
  "total_commission": "578750.00",
  "avg_commission_rate": "3.67",
  "contracts_this_month": 25,
  "expiring_soon": 3
}
```

---

#### 6. Contratos Próximos a Vencer
**GET** `/api/contratos/expiring/`

**Descripción**: Obtiene contratos que vencen en los próximos 30 días

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Query Parameters**:
- `days`: Días hacia adelante (default: 30)

**Ejemplo**: `/api/contratos/expiring/?days=15`

**Respuesta Exitosa (200)**:
```json
{
  "count": 3,
  "contracts": [
    {
      "id": 5,
      "contract_number": "CON-2025-005",
      "title": "Renta Departamento",
      "client_name": "Ana López",
      "end_date": "2025-01-20",
      "days_to_expire": 14,
      "status": "Active"
    }
  ]
}
```

---

#### 7. Generar Datos de Prueba
**POST** `/api/contratos/generate-mock/`

**Descripción**: Genera contratos de prueba (solo desarrollo)

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "count": 10
}
```

**Respuesta Exitosa (201)**:
```json
{
  "message": "10 contratos de prueba creados exitosamente",
  "contracts_created": 10,
  "total_contracts": 35
}
```

---

### 💬 MENSAJERÍA - `/api/mensajes/`

#### 1. Listar Conversaciones
**GET** `/api/mensajes/conversations/`

**Descripción**: Obtiene lista de conversaciones del usuario

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Query Parameters**:
- `page`: Número de página (default: 1)
- `conversation_type`: Filtrar por tipo (direct, group, support, announcement)
- `search`: Búsqueda por título o participantes

**Ejemplo**: `/api/mensajes/conversations/?conversation_type=direct`

**Respuesta Exitosa (200)**:
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Conversación con María García",
      "conversation_type": "direct",
      "participants": [
        {
          "id": 1,
          "email": "admin@urbany.com",
          "first_name": "Admin",
          "last_name": "User"
        },
        {
          "id": 2,
          "email": "maria@urbany.com",
          "first_name": "María",
          "last_name": "García"
        }
      ],
      "last_message": {
        "id": 25,
        "content": "¿Podemos revisar el contrato mañana?",
        "sender": "maria@urbany.com",
        "created_at": "2025-01-06T14:30:00Z"
      },
      "unread_count": 2,
      "is_active": true,
      "created_at": "2025-01-06T10:00:00Z"
    }
  ]
}
```

---

#### 2. Crear Conversación
**POST** `/api/mensajes/conversations/`

**Descripción**: Crea una nueva conversación

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "title": "Proyecto Casa Modelo",
  "conversation_type": "group",
  "participants": [2, 3, 4]
}
```

**Respuesta Exitosa (201)**:
```json
{
  "id": 16,
  "title": "Proyecto Casa Modelo",
  "conversation_type": "group",
  "participants": [
    {
      "id": 1,
      "email": "admin@urbany.com",
      "first_name": "Admin",
      "last_name": "User"
    },
    {
      "id": 2,
      "email": "maria@urbany.com",
      "first_name": "María",
      "last_name": "García"
    }
  ],
  "created_by": "admin@urbany.com",
  "is_active": true,
  "created_at": "2025-01-06T16:00:00Z"
}
```

---

#### 3. Mensajes de Conversación
**GET** `/api/mensajes/conversations/{id}/messages/`

**Descripción**: Obtiene mensajes de una conversación específica

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Query Parameters**:
- `page`: Número de página (default: 1)
- `page_size`: Mensajes por página (default: 50)

**Ejemplo**: `/api/mensajes/conversations/1/messages/`

**Respuesta Exitosa (200)**:
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "sender": {
        "id": 1,
        "email": "admin@urbany.com",
        "first_name": "Admin",
        "last_name": "User"
      },
      "message_type": "text",
      "content": "Hola, ¿cómo estás?",
      "attachment": null,
      "reply_to": null,
      "reactions": [
        {
          "user": "maria@urbany.com",
          "reaction_type": "like"
        }
      ],
      "is_read": true,
      "read_at": "2025-01-06T10:05:00Z",
      "time_ago": "hace 6 horas",
      "created_at": "2025-01-06T10:00:00Z"
    }
  ]
}
```

---

#### 4. Enviar Mensaje
**POST** `/api/mensajes/conversations/{id}/messages/`

**Descripción**: Envía un nuevo mensaje a la conversación

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "message_type": "text",
  "content": "Perfecto, nos vemos mañana a las 10 AM",
  "reply_to": 25
}
```

**Respuesta Exitosa (201)**:
```json
{
  "id": 160,
  "sender": {
    "id": 1,
    "email": "admin@urbany.com",
    "first_name": "Admin",
    "last_name": "User"
  },
  "message_type": "text",
  "content": "Perfecto, nos vemos mañana a las 10 AM",
  "attachment": null,
  "reply_to": {
    "id": 25,
    "content": "¿Podemos revisar el contrato mañana?",
    "sender": "maria@urbany.com"
  },
  "reactions": [],
  "is_read": false,
  "read_at": null,
  "time_ago": "ahora",
  "created_at": "2025-01-06T16:30:00Z"
}
```

---

#### 5. Agregar Reacción
**POST** `/api/mensajes/messages/{id}/reactions/`

**Descripción**: Agrega una reacción a un mensaje

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "reaction_type": "love"
}
```

**Respuesta Exitosa (201)**:
```json
{
  "message": "Reacción agregada exitosamente",
  "reaction": {
    "user": "admin@urbany.com",
    "reaction_type": "love",
    "created_at": "2025-01-06T16:35:00Z"
  }
}
```

---

#### 6. Estadísticas de Mensajería
**GET** `/api/mensajes/stats/`

**Descripción**: Obtiene estadísticas de mensajería del usuario

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "total_conversations": 15,
  "unread_messages": 5,
  "messages_sent_today": 8,
  "messages_received_today": 12,
  "top_contacts": [
    {
      "user": "maria@urbany.com",
      "name": "María García",
      "message_count": 25
    },
    {
      "user": "carlos@urbany.com", 
      "name": "Carlos López",
      "message_count": 18
    }
  ],
  "conversation_types": {
    "direct": 4,
    "group": 3,
    "support": 4,
    "announcement": 4
  }
}
```

---

#### 7. Buscar Mensajes
**GET** `/api/mensajes/search/`

**Descripción**: Busca mensajes en todas las conversaciones del usuario

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Query Parameters**:
- `q`: Término de búsqueda (requerido)
- `conversation_id`: Buscar solo en conversación específica
- `message_type`: Filtrar por tipo de mensaje

**Ejemplo**: `/api/mensajes/search/?q=contrato&conversation_id=1`

**Respuesta Exitosa (200)**:
```json
{
  "count": 3,
  "results": [
    {
      "id": 25,
      "content": "¿Podemos revisar el contrato mañana?",
      "sender": "maria@urbany.com",
      "conversation": {
        "id": 1,
        "title": "Conversación con María García"
      },
      "created_at": "2025-01-06T14:30:00Z"
    }
  ]
}
```

---

#### 8. Estado de Usuario
**GET** `/api/mensajes/status/`

**Descripción**: Obtiene el estado actual del usuario

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "user": "admin@urbany.com",
  "status": "online",
  "last_seen": "2025-01-06T16:40:00Z",
  "custom_message": "Disponible para consultas"
}
```

---

#### 9. Actualizar Estado
**POST** `/api/mensajes/status/`

**Descripción**: Actualiza el estado del usuario

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "status": "busy",
  "custom_message": "En reunión hasta las 18:00"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "user": "admin@urbany.com",
  "status": "busy",
  "last_seen": "2025-01-06T16:45:00Z",
  "custom_message": "En reunión hasta las 18:00",
  "updated_at": "2025-01-06T16:45:00Z"
}
```

---

#### 10. Usuarios En Línea
**GET** `/api/mensajes/online-users/`

**Descripción**: Obtiene lista de usuarios actualmente en línea

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "count": 3,
  "users": [
    {
      "user": "maria@urbany.com",
      "name": "María García",
      "status": "online",
      "last_seen": "2025-01-06T16:45:00Z",
      "custom_message": "Disponible"
    },
    {
      "user": "carlos@urbany.com",
      "name": "Carlos López", 
      "status": "away",
      "last_seen": "2025-01-06T16:30:00Z",
      "custom_message": "Regreso en 15 min"
    }
  ]
}
```

---

## 📋 CÓDIGOS DE ESTADO HTTP

- **200**: OK - Solicitud exitosa
- **201**: Created - Recurso creado exitosamente  
- **204**: No Content - Solicitud exitosa sin contenido
- **400**: Bad Request - Datos inválidos
- **401**: Unauthorized - No autenticado
- **403**: Forbidden - Sin permisos
- **404**: Not Found - Recurso no encontrado
- **500**: Internal Server Error - Error del servidor

## 🚀 Script Postman para Autenticación Automática

```javascript
// En el endpoint de login, agregar en "Tests":
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("access_token", response.tokens.access);
    pm.environment.set("refresh_token", response.tokens.refresh);
    pm.environment.set("user_id", response.user.id);
}
```
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "email": "nuevo@ejemplo.com",
  "password": "contraseña123",
  "first_name": "María",
  "last_name": "García",
  "phone": "+52 55 9876 5432",
  "role": "user"
}
```

**Respuesta Exitosa (201)**:
```json
{
  "id": 2,
  "email": "nuevo@ejemplo.com",
  "first_name": "María",
  "last_name": "García",
  "phone": "+52 55 9876 5432",
  "is_active": true,
  "date_joined": "2025-01-06T14:48:25.123456Z",
  "role": "user"
}
```

---

### 3. Detalle de Usuario
**GET** `/api/users/{id}/`

**Descripción**: Obtiene detalles de un usuario específico

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Ejemplo**: `/api/users/1/`

**Respuesta Exitosa (200)**:
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+52 55 1234 5678",
  "is_active": true,
  "date_joined": "2025-01-06T14:48:25.123456Z",
  "last_login": "2025-01-06T14:48:25.123456Z",
  "role": "user",
  "permissions": ["view_user", "change_own_profile"]
}
```

---

### 4. Actualizar Usuario
**PUT** `/api/users/{id}/`

**Descripción**: Actualiza completamente un usuario

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "email": "usuario_actualizado@ejemplo.com",
  "first_name": "Juan Carlos",
  "last_name": "Pérez López",
  "phone": "+52 55 1234 5678",
  "is_active": true
}
```

**Respuesta Exitosa (200)**:
```json
{
  "id": 1,
  "email": "usuario_actualizado@ejemplo.com",
  "first_name": "Juan Carlos",
  "last_name": "Pérez López",
  "phone": "+52 55 1234 5678",
  "is_active": true,
  "date_joined": "2025-01-06T14:48:25.123456Z",
  "role": "user"
}
```

---

### 5. Actualización Parcial de Usuario
**PATCH** `/api/users/{id}/`

**Descripción**: Actualiza parcialmente un usuario

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "first_name": "Juan Carlos"
}
```

---

### 6. Eliminar Usuario
**DELETE** `/api/users/{id}/`

**Descripción**: Elimina un usuario (solo administradores)

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (204)**: Sin contenido

---

### 7. Cambiar Contraseña
**POST** `/api/users/{id}/change-password/`

**Descripción**: Cambia la contraseña de un usuario

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "old_password": "contraseña_actual",
  "new_password": "nueva_contraseña123",
  "new_password_confirm": "nueva_contraseña123"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "message": "Contraseña actualizada exitosamente"
}
```

---

### 8. Estadísticas de Usuarios
**GET** `/api/users/statistics/`

**Descripción**: Obtiene estadísticas generales de usuarios

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "total_users": 150,
  "active_users": 142,
  "inactive_users": 8,
  "new_users_this_month": 25,
  "users_by_role": {
    "admin": 5,
    "manager": 15,
    "user": 130
  }
}
```

---

## 🔑 ROLES Y PERMISOS (`/api/roles/`)

### 1. Lista de Roles
**GET** `/api/roles/`

**Descripción**: Obtiene lista de todos los roles

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Administrador",
      "description": "Acceso completo al sistema",
      "permissions": [
        {
          "id": 1,
          "name": "add_user",
          "content_type": "user",
          "codename": "add_user"
        }
      ],
      "user_count": 5,
      "created_at": "2025-01-06T14:48:25.123456Z"
    }
  ]
}
```

---

### 2. Crear Rol
**POST** `/api/roles/`

**Descripción**: Crea un nuevo rol

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "name": "Vendedor",
  "description": "Rol para agentes de ventas",
  "permissions": [1, 2, 3]
}
```

**Respuesta Exitosa (201)**:
```json
{
  "id": 4,
  "name": "Vendedor",
  "description": "Rol para agentes de ventas",
  "permissions": [
    {
      "id": 1,
      "name": "view_property",
      "content_type": "property",
      "codename": "view_property"
    }
  ],
  "user_count": 0,
  "created_at": "2025-01-06T14:48:25.123456Z"
}
```

---

### 3. Detalle de Rol
**GET** `/api/roles/{id}/`

**Descripción**: Obtiene detalles de un rol específico

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "id": 1,
  "name": "Administrador",
  "description": "Acceso completo al sistema",
  "permissions": [
    {
      "id": 1,
      "name": "add_user",
      "content_type": "user",
      "codename": "add_user"
    }
  ],
  "users": [
    {
      "id": 1,
      "email": "admin@ejemplo.com",
      "first_name": "Admin",
      "last_name": "Sistema"
    }
  ],
  "user_count": 5,
  "created_at": "2025-01-06T14:48:25.123456Z",
  "updated_at": "2025-01-06T14:48:25.123456Z"
}
```

---

### 4. Actualizar Rol
**PUT** `/api/roles/{id}/`

**Descripción**: Actualiza completamente un rol

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "name": "Administrador General",
  "description": "Acceso completo al sistema con permisos especiales",
  "permissions": [1, 2, 3, 4, 5]
}
```

---

### 5. Eliminar Rol
**DELETE** `/api/roles/{id}/`

**Descripción**: Elimina un rol (solo si no tiene usuarios asignados)

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (204)**: Sin contenido

**Error (400)**:
```json
{
  "error": "No se puede eliminar un rol que tiene usuarios asignados"
}
```

---

### 6. Agregar Permiso a Rol
**POST** `/api/roles/{id}/add-permission/`

**Descripción**: Agrega un permiso específico a un rol

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "permission_id": 5
}
```

**Respuesta Exitosa (200)**:
```json
{
  "message": "Permiso agregado exitosamente",
  "role": {
    "id": 1,
    "name": "Administrador",
    "permissions_count": 6
  }
}
```

---

### 7. Remover Permiso de Rol
**POST** `/api/roles/{id}/remove-permission/`

**Descripción**: Remueve un permiso específico de un rol

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {{access_token}}"
}
```

**Body (JSON)**:
```json
{
  "permission_id": 5
}
```

**Respuesta Exitosa (200)**:
```json
{
  "message": "Permiso removido exitosamente",
  "role": {
    "id": 1,
    "name": "Administrador",
    "permissions_count": 5
  }
}
```

---

### 8. Lista de Permisos
**GET** `/api/roles/permissions/`

**Descripción**: Obtiene lista de todos los permisos disponibles

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Can add user",
      "content_type": "user",
      "codename": "add_user"
    },
    {
      "id": 2,
      "name": "Can change user",
      "content_type": "user",
      "codename": "change_user"
    }
  ]
}
```

---

### 9. Estadísticas de Roles
**GET** `/api/roles/statistics/`

**Descripción**: Obtiene estadísticas de roles y permisos

**Headers**:
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "total_roles": 5,
  "total_permissions": 20,
  "roles_with_users": 3,
  "empty_roles": 2,
  "most_used_role": {
    "name": "Usuario",
    "user_count": 120
  },
  "permissions_distribution": {
    "user": 8,
    "role": 4,
    "permission": 3,
    "other": 5
  }
}
```

---

## 📋 DOCUMENTACIÓN API

### 1. Esquema OpenAPI
**GET** `/api/schema/`

**Descripción**: Obtiene el esquema completo de la API en formato OpenAPI

**Headers**: Ninguno requerido

**Respuesta**: Esquema JSON de la API

---

### 2. Documentación Swagger UI
**GET** `/api/docs/`

**Descripción**: Interfaz interactiva de documentación Swagger

**Acceso**: Navegador web - `http://127.0.0.1:8000/api/docs/`

---

### 3. Documentación ReDoc
**GET** `/api/redoc/`

**Descripción**: Documentación alternativa con ReDoc

**Acceso**: Navegador web - `http://127.0.0.1:8000/api/redoc/`

---

## 🔧 CÓDIGOS DE ESTADO HTTP

### Códigos de Éxito
- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `204 No Content`: Solicitud exitosa sin contenido de respuesta

### Códigos de Error del Cliente
- `400 Bad Request`: Datos inválidos o malformados
- `401 Unauthorized`: No autenticado o token inválido
- `403 Forbidden`: Sin permisos para realizar la acción
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto con el estado actual del recurso

### Códigos de Error del Servidor
- `500 Internal Server Error`: Error interno del servidor

---

## 🚀 COLECCIÓN ORGANIZADA DE POSTMAN

### Estructura Recomendada

Para facilitar las pruebas, organizar la colección de Postman de la siguiente manera:

```
📁 CRM URBANY API
├── 📁 Authentication
│   ├── Health Check (GET)
│   ├── Register (POST)
│   ├── Login (POST) ← Agregar script post-response
│   ├── Logout (POST)
│   └── Password Recovery (POST)
├── 📁 Users (Requieren Auth)
│   ├── List Users (GET)
│   ├── My Profile (GET)
│   ├── Update Profile (PUT)
│   ├── Change Password (POST)
│   └── Assign Role (POST)
├── 📁 Roles (Requieren Auth)
│   ├── List Roles (GET)
│   ├── Create Role (POST)
│   ├── Get Role by ID (GET)
│   ├── Update Role (PUT)
│   ├── Delete Role (DELETE)
│   └── Role Statistics (GET)
└── 📁 Documentation
    ├── Swagger UI (GET)
    ├── API Docs (GET)
    └── ReDoc (GET)
```

### Configuración Rápida

1. **Importar Variables de Entorno**:
   ```json
   {
     "base_url": "http://127.0.0.1:8000",
     "access_token": "",
     "refresh_token": "",
     "user_id": "",
     "admin_email": "admin@urbany.com",
     "admin_password": "admin123"
   }
   ```

2. **Headers a Nivel de Colección**:
   - `Content-Type: application/json`
   - `Authorization: Bearer {{access_token}}`

3. **Script de Auto-Login** (Pre-request a nivel de colección):
   ```javascript
   if (!pm.environment.get("access_token")) {
       pm.sendRequest({
           url: pm.environment.get("base_url") + "/api/auth/login/",
           method: 'POST',
           header: { 'Content-Type': 'application/json' },
           body: {
               mode: 'raw',
               raw: JSON.stringify({
                   email: pm.environment.get("admin_email"),
                   password: pm.environment.get("admin_password")
               })
           }
       }, function (err, response) {
           if (response.code === 200) {
               const data = response.json();
               pm.environment.set("access_token", data.tokens.access);
               pm.environment.set("refresh_token", data.tokens.refresh);
           }
       });
   }
   ```

### Tests Automatizados

**Test Script para Login:**
```javascript
pm.test("Login successful", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    pm.expect(response).to.have.property("tokens");
    pm.environment.set("access_token", response.tokens.access);
});
```

**Test Script para Endpoints Protegidos:**
```javascript
pm.test("Authenticated request successful", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    const response = pm.response.json();
    pm.expect(response).to.be.an("object");
});
```

---

## 📋 VERIFICACIÓN DE INSTALACIÓN

### Comandos de Verificación Rápida

```bash
# 1. Verificar Health Check
curl http://127.0.0.1:8000/api/auth/health/

# 2. Probar Registro
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123", "password_confirm": "testpass123", "first_name": "Test", "last_name": "User"}'

# 3. Probar Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@urbany.com", "password": "admin123"}'
```

---

## 🎯 FLUJO DE TRABAJO RECOMENDADO

1. **Configurar Postman** con variables y headers
2. **Ejecutar Health Check** para verificar conectividad
3. **Hacer Login** para obtener tokens
4. **Probar endpoints protegidos** con autenticación automática
5. **Usar Swagger UI** para explorar la API interactivamente

---

*Documentación actualizada - Octubre 2025*