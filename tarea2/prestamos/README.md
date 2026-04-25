# Prestamo GraphQL API

API GraphQL para el servicio de préstamos de la biblioteca.

- **Endpoint:** `http://127.0.0.1:5002/graphql`
- **Run:** `python app.py`

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

## Mutaciones (Mutations)

### Crear un préstamo

```graphql
mutation {
  crearPrestamo(input: {
    user: "juan_perez",
    books: ["El Quijote", "Cien Años de Soledad"],
    loanDueDate: "2026-05-15"
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
- El préstamo creado se devuelve con su estado inicial.

### Actualizar el estado de un préstamo

```graphql
mutation {
  actualizarEstadoPrestamo(input: {
    loanId: 1,
    status: "returned"
  }) {
    loanId
    user
    status
  }
}
```

- Cambia el campo `status` del préstamo existente.
- Si el préstamo no existe, la mutación devuelve `null`.

## Notas

- El endpoint `/graphql` usa Strawberry y GraphQL introspection para explorar el esquema.
- Si quiere probar con una UI, utilice el navegador en `http://127.0.0.1:5002/graphql`.
