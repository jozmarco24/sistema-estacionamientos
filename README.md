# Sistema Distribuido de Estacionamientos Inteligentes

Sistema de microservicios distribuido desarrollado con **FastAPI**, **PostgreSQL** y **Docker Compose**.

---

## 🏛️ Arquitectura del Sistema

El sistema está compuesto por **4 microservicios backend independientes**, un **Frontend unificado servido por Nginx Reverse Proxy** y **1 contenedor de Base de Datos PostgreSQL 15**:

| Servicio / Componente | Puerto Externo | Esquema PostgreSQL | Descripción |
|---|---|---|---|
| **Frontend Nginx Proxy** | `8080` | N/A | Interfaz web unificada y Gateway Reverse Proxy hacia los microservicios (`/api/...`). |
| **PostgreSQL 15** | `5432` | Base `db_sistema_estacionamientos` | Base relacional con esquemas aislados por dominio. |
| **Usuarios** | `8001` | `db_usuarios` | Gestión de usuarios, autenticación JWT, roles (`conductor`, `propietario`, `operador`, `admin`), planes SaaS. |
| **Estacionamientos** | `8002` | `db_estacionamientos` | Sedes geolocalizadas (Haversine), espacios diferenciados por vehículo (`auto`, `moto`), tarifas día/noche e incidencias. |
| **Reservas** | `8003` | `db_reservas` | Bloqueo atómico pesimista (`SELECT FOR UPDATE`), cotización centralizada UTC-5 Lima, expiración automática en background y timeout de cliente. |
| **Pagos** | `8004` | `db_pagos` | Integración directa con pasarela **Culqi (Modo Pruebas)**, credenciales cifradas con Fernet por propietario, cobros de reservas y suscripciones SaaS con reintentos resilientes. |

---

## 🔒 Mecanismo de Concurrencia y Exclusión Mutua

Para evitar inconsistencias y *race conditions* (por ejemplo, que dos usuarios reserven el mismo espacio simultáneamente):
1. **Llamada REST Inter-Servicio**: El servicio de `reservas` invoca el endpoint `/espacios/{espacio_id}/reservar_atomico` del servicio de `estacionamientos` protegido con `X-Internal-Key`.
2. **Bloqueo Pesimista (`SELECT FOR UPDATE`)**: El servicio de `estacionamientos` abre una transacción PostgreSQL y ejecuta `SELECT ... FOR UPDATE` sobre el espacio solicitado. Si el estado es `libre`, lo cambia a `reservado` de manera atómica. Si ya está reservado u ocupado, devuelve inmediatamente `409 Conflict`.
3. **Validación de Solapamiento Temporal**: El servicio de `reservas` también verifica y bloquea consultas concurrentes de reservas en `db_reservas`.
4. **Manejo Centralizado de Horarios (UTC-5 Lima)**: Módulo `time_utils` para garantizar cálculo homogéneo de tarifas diurnas vs nocturnas en cotizaciones.
5. **Reintentos Resilientes en Pagos**: Tras cobrar exitosamente con Culqi, el servicio de Pagos ejecuta hasta 3 reintentos automáticos para confirmar la reserva en el microservicio de Reservas.

---

## 🚀 Cómo Ejecutar el Proyecto

### Requisitos Previos
- Docker Desktop / Docker Engine instalado y ejecutándose.
- Docker Compose.

### Paso 1: Levantar todos los servicios con Docker Compose
```bash
docker compose up --build -d
```

### Paso 2: Acceso a la Plataforma Web
- 🌐 **Portal Web Completo**: [http://localhost:8080](http://localhost:8080)
  - Conductor: Búsqueda interactiva en mapa Leaflet, selección de espacio, cotización y pago con Culqi.
  - Propietario: Gestión de llaves Culqi, sedes, slots, empleados y suscripciones SaaS.
  - Operador: Caseta de control, validación de QR y tickets.
  - Admin: Auditoría global, gestión de planes y monitoreo de salud.

---

## 🧪 Ejecución de Pruebas Automatizadas

El proyecto cuenta con una suite integral de pruebas con **pytest**:

```bash
pytest tests/test_culqi_flow.py -v
```
*Cubre salud de servicios, seguridad inter-servicio, credenciales Culqi, cotizador de tarifas diurna/nocturna, bloqueo atómico, expiración de reservas, órdenes de suscripción y manejo de zonas horarias.*

---

## 🌐 Documentación Swagger (Interactive API Docs)

Cada microservicio expone su propia documentación interactiva en los siguientes enlaces:

- 👤 **Usuarios**: [http://localhost:8001/docs](http://localhost:8001/docs) o [http://localhost:8080/api/usuarios/docs](http://localhost:8080/api/usuarios/docs)
- 🅿️ **Estacionamientos**: [http://localhost:8002/docs](http://localhost:8002/docs) o [http://localhost:8080/api/estacionamientos/docs](http://localhost:8080/api/estacionamientos/docs)
- 📅 **Reservas**: [http://localhost:8003/docs](http://localhost:8003/docs) o [http://localhost:8080/api/reservas/docs](http://localhost:8080/api/reservas/docs)
- 💳 **Pagos**: [http://localhost:8004/docs](http://localhost:8004/docs) o [http://localhost:8080/api/pagos/docs](http://localhost:8080/api/pagos/docs)

---

## 🧪 Guía Paso a Paso para Probar los Endpoints (Ejemplos cURL)

### 1. Registrar y Loguear un Usuario (Servicio Usuarios - 8001)

#### Registrar un Usuario Conductor:
```bash
curl -X POST "http://localhost:8001/usuarios/registro" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Carlos Perez",
    "email": "carlos@example.com",
    "password": "password123",
    "rol": "conductor"
  }'
```

#### Iniciar Sesión para obtener Token JWT:
```bash
curl -X POST "http://localhost:8001/usuarios/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "carlos@example.com",
    "password": "password123"
  }'
```

---

### 2. Crear Sede y Espacios (Servicio Estacionamientos - 8002)

#### Crear una Sede:
```bash
curl -X POST "http://localhost:8002/sedes/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Sede Central Javier Prado",
    "direccion": "Av. Javier Prado Este 1234",
    "latitud": -12.0912,
    "longitud": -77.0256
  }'
```

#### Crear un Espacio en la Sede (sede_id: 1):
```bash
curl -X POST "http://localhost:8002/espacios/" \
  -H "Content-Type: application/json" \
  -d '{
    "sede_id": 1,
    "numero": "A-101",
    "estado": "libre"
  }'
```

#### Consultar Disponibilidad del Espacio (espacio_id: 1):
```bash
curl -X GET "http://localhost:8002/espacios/1/disponibilidad"
```

---

### 3. Crear una Reserva y Verificar Exclusión Mutua (Servicio Reservas - 8003)

#### Realizar Reserva del Espacio 1:
```bash
curl -X POST "http://localhost:8003/reservas/" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 1,
    "espacio_id": 1,
    "fecha_inicio": "2026-09-01T10:00:00Z",
    "fecha_fin": "2026-09-01T12:00:00Z",
    "monto_pago": 25.50,
    "metodo_pago": "tarjeta"
  }'
```
*Respuesta esperada:* HTTP 201 Created. El estado del espacio en el servicio de estacionamientos cambia automáticamente a `"reservado"` y se genera un pago pendiente en el servicio de pagos.

#### Intentar Reservar el Mismo Espacio Nuevamente (Prueba de Exclusión Mutua):
```bash
curl -X POST "http://localhost:8003/reservas/" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 2,
    "espacio_id": 1,
    "fecha_inicio": "2026-09-01T10:00:00Z",
    "fecha_fin": "2026-09-01T12:00:00Z",
    "monto_pago": 25.50,
    "metodo_pago": "tarjeta"
  }'
```
*Respuesta esperada:* **HTTP 409 Conflict** (`El espacio no está disponible. Ya ha sido reservado u ocupado por otro usuario.`).

---

### 4. Consultar y Procesar el Pago (Servicio Pagos - 8004)

#### Consultar el Pago Generado para la Reserva 1:
```bash
curl -X GET "http://localhost:8004/pagos/reserva/1"
```

#### Procesar/Confirmar el Pago (pago_id: 1):
```bash
curl -X PUT "http://localhost:8004/pagos/1/procesar" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "pagado"
  }'
```

---

### 5. Cancelar una Reserva y Liberar Espacio

#### Cancelar Reserva (reserva_id: 1):
```bash
curl -X PUT "http://localhost:8003/reservas/1/cancelar"
```
*Respuesta esperada:* La reserva pasa a `"cancelada"` y hace una llamada REST automática a `estacionamientos` para colocar el estado del espacio de vuelta en `"libre"`.

---

## 🛑 Cómo Detener el Proyecto

```bash
docker compose down
```
Para eliminar también los volúmenes de datos de PostgreSQL:
```bash
docker compose down -v
```
