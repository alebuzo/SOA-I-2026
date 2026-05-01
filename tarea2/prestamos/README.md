# Prestamo GraphQL API

API GraphQL para el servicio de préstamos de la biblioteca.

## Esquema principal

### Tipos

- `PrestamoGraphQL`
  - `loanId: Int`
  - `user: String`
  - `books: [String!]`
  - `loanDueDate: Date`
  - `status: String`

### Inputs

- `CrearPrestamoInput`
  - `user: String!`
  - `books: [String!]!`
  - `loanDueDate: Date!`

- `ActualizarEstadoPrestamoInput`
  - `loanId: Int!`
  - `status: String!`

- `GetSoonToExpirePrestamosInput`
  - `time: Int!`

## Consultas (Queries)

### Obtener un préstamo por ID

```graphql
query {
  prestamo(loanId: 1) {
    loanId
    user
    books
    loanDueDate
    status
  }
}
```

- Devuelve un solo `PrestamoGraphQL` si existe.
- Si no existe, devuelve `null`.

**Ejemplo de respuesta:**
```json
{
  "data": {
    "prestamo": {
      "loanId": 1,
      "user": "Juan Pérez",
      "books": ["12", "45", "78"],
      "loanDueDate": "2026-05-15",
      "status": "ACTIVE"
    }
  }
}
```

### Obtener todos los préstamos

```graphql
query {
  prestamos {
    loanId
    user
    books
    loanDueDate
    status
  }
}
```

- Devuelve todos los préstamos existentes en el sistema.
- Si no hay préstamos, devuelve una lista vacía `[]`.

**Ejemplo de respuesta:**
```json
{
  "data": {
    "prestamos": [
      {
        "loanId": 1,
        "user": "Juan Pérez",
        "books": ["12", "45"],
        "loanDueDate": "2026-05-15",
        "status": "ACTIVE"
      },
      {
        "loanId": 2,
        "user": "María García",
        "books": ["33"],
        "loanDueDate": "2026-05-20",
        "status": "ARCHIVED"
      }
    ]
  }
}
```

### Obtener préstamos por usuario

```graphql
query {
  prestamosByUser(user: "Juan Pérez") {
    loanId
    books
    loanDueDate
    status
  }
}
```

- Devuelve todos los préstamos asociados a un usuario específico.
- El nombre del usuario debe coincidir exactamente.
- Si el usuario no tiene préstamos, devuelve una lista vacía `[]`.

**Ejemplo de respuesta:**
```json
{
  "data": {
    "prestamosByUser": [
      {
        "loanId": 1,
        "books": ["12", "45"],
        "loanDueDate": "2026-05-15",
        "status": "ACTIVE"
      },
      {
        "loanId": 5,
        "books": ["67"],
        "loanDueDate": "2026-05-25",
        "status": "FINALIZED"
      }
    ]
  }
}
```

### Obtener préstamos próximos a expirar

```graphql
query {
  getSoonToExpirePrestamos(input: {
    time: 7
  }) {
    loanId
    user
    books
    loanDueDate
    status
  }
}
```

- Devuelve préstamos activos (`status: "ACTIVE"`) que expiran en los próximos `time` días.
- `time`: número de días para considerar "próximo a expirar" (e.g., 7 = próximos 7 días).
- Solo incluye préstamos con estado "ACTIVE".

**Ejemplo de respuesta:**
```json
{
  "data": {
    "getSoonToExpirePrestamos": [
      {
        "loanId": 3,
        "user": "Carlos Ruiz",
        "books": ["22", "44"],
        "loanDueDate": "2026-05-05",
        "status": "ACTIVE"
      },
      {
        "loanId": 8,
        "user": "Ana López",
        "books": ["88"],
        "loanDueDate": "2026-05-07",
        "status": "ACTIVE"
      }
    ]
  }
}
```

**Ejemplo con 3 días:**
```graphql
query {
  getSoonToExpirePrestamos(input: {
    time: 3
  }) {
    loanId
    user
    loanDueDate
  }
}
```

## Mutaciones (Mutations)

### Crear un préstamo

```graphql
mutation {
  addPrestamo(input: {
    user: "Juan Pérez"
    books: ["1", "2"]
    loanDueDate: "2026-05-10"
  }) {
    loanId
    user
    books
    loanDueDate
    status
  }
}
```

- `loanId` se genera automáticamente en el servidor.
- `loanDueDate` debe usarse en formato ISO `YYYY-MM-DD`.
- El préstamo creado se devuelve con su estado inicial (`"ACTIVE"`).
- **Validación**: Verifica que todos los libros estén disponibles en el inventario antes de crear el préstamo.

**Ejemplo de respuesta exitosa:**
```json
{
  "data": {
    "addPrestamo": {
      "loanId": 7,
      "user": "Juan Pérez",
      "books": ["1", "2"],
      "loanDueDate": "2026-05-10",
      "status": "ACTIVE"
    }
  }
}
```

**Ejemplo de error (libro no disponible):**
```json
{
  "data": null,
  "errors": [
    {
      "message": "Libro con id 999 no disponible para préstamo",
      "path": ["addPrestamo"]
    }
  ]
}
```

### Crear préstamo con múltiples libros

```graphql
mutation {
  addPrestamo(input: {
    user: "María García"
    books: ["5", "12", "23", "45"]
    loanDueDate: "2026-06-01"
  }) {
    loanId
    user
    books
    status
  }
}
```

### Actualizar el estado de un préstamo

```graphql
mutation {
  updateStatusPrestamo(input: {
    loanId: 1,
    status: "FINALIZED"
  }) {
    loanId
    user
    status
  }
}
```

- Cambia el campo `status` del préstamo existente.
- Si el préstamo no existe, la mutación devuelve `null`.
- Posibles status: `"ACTIVE"`, `"ARCHIVED"`, `"FINALIZED"`

**Ejemplo de respuesta:**
```json
{
  "data": {
    "updateStatusPrestamo": {
      "loanId": 1,
      "user": "Juan Pérez",
      "status": "ACTIVE"
    }
  }
}
```

### Finalizar un préstamo

```graphql
mutation {
  updateStatusPrestamo(input: {
    loanId: 5,
    status: "FINALIZED"
  }) {
    loanId
    user
    books
    status
  }
}
```

### Eliminar un préstamo

```graphql
mutation {
  deletePrestamo(loanId: 10)
}
```

- Elimina permanentemente un préstamo del sistema.
- Devuelve `true` si el préstamo fue eliminado exitosamente.
- Devuelve `false` si el préstamo no existe.

**Ejemplo de respuesta exitosa:**
```json
{
  "data": {
    "deletePrestamo": true
  }
}
```

**Ejemplo de respuesta (préstamo no encontrado):**
```json
{
  "data": {
    "deletePrestamo": false
  }
}
```

## Estados de Préstamo

| Estado       | Descripción                                      |
|--------------|--------------------------------------------------|
| `ACTIVE`     | Préstamo activo, libros actualmente prestados    |
| `ARCHIVED`   | Préstamo archivado para referencia histórica     |
| `FINALIZED`  | Préstamo finalizado, libros devueltos            |

## Integración con Inventario

El servicio de préstamos se comunica con el servicio de inventario para:
- Verificar la disponibilidad de los libros antes de crear un préstamo
- Consultar el endpoint `GET /books/available` del servicio de inventario

## Notas

- El endpoint `/graphql` usa Strawberry y GraphQL introspection para explorar el esquema.
- La base de datos en memoria se inicializa con datos de prueba generados por Faker al arrancar el servicio.
- Los libros se referencian por su ID como strings en el array `books`.
- Las fechas usan formato ISO 8601: `YYYY-MM-DD`.