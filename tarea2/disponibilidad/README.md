# Disponibilidad REST API

API REST para el servicio de disponibilidad de libros en la biblioteca.

## Descripción

El servicio de Disponibilidad gestiona el estado de préstamo de los libros en la biblioteca. Cada libro tiene un registro de disponibilidad que indica si puede ser prestado o no, junto con la razón de su indisponibilidad (si aplica).

## Modelo de Datos

### Disponibilidad

Representa el estado actual de disponibilidad de un libro específico.

```json
{
  "disponibilidadId": 1,
  "bookId": 42,
  "available": true,
  "reason": "LOANED",
  "lastUpdated": "2026-04-30T10:30:00"
}
```

**Campos:**
- `disponibilidadId` (int): Identificador único de la disponibilidad (generado automáticamente)
- `bookId` (int, requerido): ID del libro al que pertenece esta disponibilidad
- `available` (bool, requerido): Estado de disponibilidad del libro
- `reason` (string, opcional): Razón de indisponibilidad si `available` es `false`
- `lastUpdated` (datetime): Fecha y hora de la última actualización (generado automáticamente)

**Valores posibles para `reason`:**
- `LOANED` - El libro está prestado
- `RESTORATION` - El libro está en restauración
- `HIGH_VALUE` - Libro de alto valor, no disponible para préstamo
- `UNIQUE_COPY` - Única copia disponible, no se presta
- `LOST` - El libro se ha extraviado
- `OTHER` - Otra razón no especificada

## Endpoints

### 1. Crear disponibilidad para un libro

**POST** `/disponibilidad/<book_id>`

Crea un nuevo registro de disponibilidad para un libro específico.

**Parámetros de ruta:**
- `book_id` (int): ID del libro

**Body (JSON):**
```json
{
  "bookId": 42,
  "available": true,
  "reason": null
}
```

**Ejemplo de solicitud:**
```bash
curl -X POST http://localhost:5000/disponibilidad/42 \
  -H "Content-Type: application/json" \
  -d '{
    "bookId": 42,
    "available": true
  }'
```

**Respuesta exitosa (201 Created):**
```json
{
  "disponibilidadId": 21,
  "bookId": 42,
  "available": true,
  "reason": null,
  "lastUpdated": "2026-04-30T14:23:15.123456"
}
```

**Respuesta de error (400 Bad Request):**
```json
{
  "bookId": ["Missing data for required field."],
  "available": ["Missing data for required field."]
}
```

---

### 2. Obtener disponibilidad de un libro

**GET** `/disponibilidad/<book_id>`

Obtiene el registro de disponibilidad de un libro específico.

**Parámetros de ruta:**
- `book_id` (int): ID del libro

**Ejemplo de solicitud:**
```bash
curl -X GET http://localhost:5000/disponibilidad/42
```

**Respuesta exitosa (200 OK):**
```json
{
  "disponibilidadId": 5,
  "bookId": 42,
  "available": false,
  "reason": "LOANED",
  "lastUpdated": "2026-04-29T10:15:30.456789"
}
```

**Respuesta de error (404 Not Found):**
```json
{
  "message": "Disponibilidad no encontrada para el bookId dado."
}
```

---

### 3. Obtener todas las disponibilidades

**GET** `/disponibilidad/`

Obtiene todos los registros de disponibilidad en el sistema.

**Ejemplo de solicitud:**
```bash
curl -X GET http://localhost:5000/disponibilidad/
```

**Respuesta exitosa (200 OK):**
```json
[
  {
    "disponibilidadId": 1,
    "bookId": 1,
    "available": true,
    "reason": null,
    "lastUpdated": "2026-04-28T08:00:00.000000"
  },
  {
    "disponibilidadId": 2,
    "bookId": 2,
    "available": false,
    "reason": "RESTORATION",
    "lastUpdated": "2026-04-29T15:30:00.000000"
  },
  {
    "disponibilidadId": 3,
    "bookId": 3,
    "available": false,
    "reason": "LOANED",
    "lastUpdated": "2026-04-30T09:45:00.000000"
  }
]
```

---

### 4. Actualizar disponibilidad de un libro

**PUT** `/disponibilidad/<book_id>`

Actualiza el registro de disponibilidad de un libro. Admite actualizaciones parciales.

**Parámetros de ruta:**
- `book_id` (int): ID del libro

**Body (JSON):**

Actualización completa:
```json
{
  "bookId": 42,
  "available": false,
  "reason": "LOANED"
}
```

Actualización parcial (solo disponibilidad):
```json
{
  "available": true
}
```

Actualización parcial (solo razón):
```json
{
  "reason": "RESTORATION"
}
```

**Ejemplo de solicitud:**
```bash
curl -X PUT http://localhost:5000/disponibilidad/42 \
  -H "Content-Type: application/json" \
  -d '{
    "available": false,
    "reason": "LOANED"
  }'
```

**Respuesta exitosa (200 OK):**
```json
{
  "disponibilidadId": 5,
  "bookId": 42,
  "available": false,
  "reason": "LOANED",
  "lastUpdated": "2026-04-30T14:35:22.789012"
}
```

**Notas:**
- El campo `lastUpdated` se actualiza automáticamente al momento de la modificación
- Si `available` se cambia a `true`, se recomienda limpiar el campo `reason` (establecer a `null`)

**Respuesta de error (404 Not Found):**
```json
{
  "message": "Disponibilidad no encontrada para el bookId dado."
}
```

**Respuesta de error (400 Bad Request):**
```json
{
  "reason": ["Must be one of: LOANED, RESTORATION, HIGH_VALUE, UNIQUE_COPY, LOST, OTHER."]
}
```

---

### 5. Eliminar disponibilidad de un libro

**DELETE** `/disponibilidad/<book_id>`

Elimina el registro de disponibilidad de un libro.

**Parámetros de ruta:**
- `book_id` (int): ID del libro

**Ejemplo de solicitud:**
```bash
curl -X DELETE http://localhost:5000/disponibilidad/42
```

**Respuesta exitosa (200 OK):**
```json
{
  "message": "Disponibilidad eliminada."
}
```

**Respuesta de error (404 Not Found):**
```json
{
  "message": "Disponibilidad no encontrada para el bookId dado."
}
```

---

## Ejemplos de Uso Completos

### Caso 1: Crear y marcar un libro como prestado

```bash
# 1. Crear disponibilidad inicial (libro disponible)
curl -X POST http://localhost:5000/disponibilidad/100 \
  -H "Content-Type: application/json" \
  -d '{
    "bookId": 100,
    "available": true
  }'

# 2. Marcar libro como prestado
curl -X PUT http://localhost:5000/disponibilidad/100 \
  -H "Content-Type: application/json" \
  -d '{
    "available": false,
    "reason": "LOANED"
  }'

# 3. Verificar estado
curl -X GET http://localhost:5000/disponibilidad/100
```

### Caso 2: Marcar libro en restauración

```bash
# Actualizar a estado de restauración
curl -X PUT http://localhost:5000/disponibilidad/42 \
  -H "Content-Type: application/json" \
  -d '{
    "available": false,
    "reason": "RESTORATION"
  }'
```

### Caso 3: Devolver un libro (marcarlo como disponible)

```bash
# Actualizar a disponible
curl -X PUT http://localhost:5000/disponibilidad/42 \
  -H "Content-Type: application/json" \
  -d '{
    "available": true,
    "reason": null
  }'
```

### Caso 4: Consultar todos los libros disponibles

```bash
# Obtener todas las disponibilidades y filtrar en el cliente
curl -X GET http://localhost:5000/disponibilidad/ | jq '.[] | select(.available == true)'
```
---

## Validaciones

- `bookId`: Debe ser un entero positivo (requerido al crear)
- `available`: Debe ser un booleano `true` o `false` (requerido al crear)
- `reason`: Debe ser uno de los valores permitidos o `null` (opcional)
- Si `available` es `true`, se recomienda que `reason` sea `null`

---

## Integración con Otros Servicios

Este servicio es consumido por:
- **Servicio de Préstamos**: Para verificar disponibilidad antes de crear un préstamo

---

## Notas Adicionales

- La base de datos es en memoria, por lo que los datos se pierden al reiniciar el servidor
- El campo `lastUpdated` se actualiza automáticamente en formato ISO 8601
- El `disponibilidadId` se genera automáticamente de forma incremental
- El servidor corre por defecto en el puerto `5000`