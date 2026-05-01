# Inventario API

API REST para gestionar el inventario de libros en la biblioteca. Integrado con el servicio de Disponibilidad para obtener información actualizada sobre la disponibilidad de libros.

## Book Schema

El modelo `Book` representa una copia física de un libro en la biblioteca.

### Estructura

| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `bookId` | integer | ✓ (auto) | ID único del libro (auto-generado) | `42` |
| `title` | string | ✓ | Título del libro | `"How I Live Now"` |
| `author` | string | ✓ | Autor del libro | `"Meg Rosoff"` |
| `isbn` | string | ✓ | ISBN del libro | `"978-0-14-138075-9"` |
| `edition` | integer | ✓ | Edición del libro | `2` |
| `notes` | string | ✗ | Notas adicionales sobre el libro | `"Libro en buen estado"` |
| `available` | boolean | ✗ | Disponibilidad del libro (consultado desde el servicio de Disponibilidad) | `true` / `false` / `null` |

### Ejemplo JSON

```json
{
  "bookId": 1,
  "title": "How I Live Now",
  "author": "Meg Rosoff",
  "isbn": "978-0-14-138075-9",
  "edition": 2,
  "notes": "Libro en buen estado",
  "available": true
}
```

## Endpoints

### 1. Obtener todos los libros

**GET** `/books`

Retorna la lista completa de libros con su información de disponibilidad actualizada consultando el servicio de Disponibilidad.

#### Ejemplo cURL

```bash
curl -X GET "http://localhost:5001/books" \
  -H "accept: application/json"
```

#### Respuesta (200 OK)

```json
[
  {
    "bookId": 1,
    "title": "How I Live Now",
    "author": "Meg Rosoff",
    "isbn": "978-0-14-138075-9",
    "edition": 2,
    "notes": "Libro en buen estado",
    "available": true
  },
  {
    "bookId": 2,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "978-0-7432-7356-5",
    "edition": 1,
    "notes": null,
    "available": false
  }
]
```

---

### 2. Obtener libros disponibles

**GET** `/books/available`

Retorna solo los libros que están actualmente disponibles (según el servicio de Disponibilidad).

#### Ejemplo cURL

```bash
curl -X GET "http://localhost:5001/books/available" \
  -H "accept: application/json"
```

#### Respuesta (200 OK)

```json
[
  {
    "bookId": 1,
    "title": "How I Live Now",
    "author": "Meg Rosoff",
    "isbn": "978-0-14-138075-9",
    "edition": 2,
    "notes": "Libro en buen estado",
    "available": true
  }
]
```

---

### 3. Obtener un libro por ID

**GET** `/books/{bookId}`

Retorna los detalles de un libro específico con su disponibilidad actualizada.

#### Parámetros

- `bookId` (path, requerido): ID del libro a consultar

#### Ejemplo cURL

```bash
curl -X GET "http://localhost:5001/books/1" \
  -H "accept: application/json"
```

#### Respuesta (200 OK)

```json
{
  "bookId": 1,
  "title": "How I Live Now",
  "author": "Meg Rosoff",
  "isbn": "978-0-14-138075-9",
  "edition": 2,
  "notes": "Libro en buen estado",
  "available": true
}
```

#### Respuesta (404 Not Found)

```json
{
  "message": "Libro no encontrado"
}
```

---

### 4. Crear un libro

**POST** `/books`

Crea un nuevo libro en el inventario. El `bookId` se asigna automáticamente.

#### Body (JSON)

```json
{
  "title": "The Hobbit",
  "author": "J.R.R. Tolkien",
  "isbn": "978-0-547-92822-8",
  "edition": 3,
  "notes": "Primera copia"
}
```

#### Ejemplo cURL

```bash
curl -X POST "http://localhost:5001/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "isbn": "978-0-547-92822-8",
    "edition": 3,
    "notes": "Primera copia"
  }'
```

#### Respuesta (201 Created)

```json
{
  "bookId": 20,
  "title": "The Hobbit",
  "author": "J.R.R. Tolkien",
  "isbn": "978-0-547-92822-8",
  "edition": 3,
  "notes": "Primera copia",
  "available": null
}
```

#### Respuesta (400 Bad Request)

```json
{
  "title": ["Missing data for required field."],
  "author": ["Missing data for required field."]
}
```

---

### 5. Actualizar un libro

**PUT** `/books/{bookId}`

Actualiza los detalles de un libro existente (actualización parcial).

#### Parámetros

- `bookId` (path, requerido): ID del libro a actualizar

#### Body (JSON) - Solo los campos a actualizar

```json
{
  "notes": "Libro en excelente estado",
  "edition": 4
}
```

#### Ejemplo cURL

```bash
curl -X PUT "http://localhost:5001/books/1" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Libro en excelente estado",
    "edition": 4
  }'
```

#### Respuesta (200 OK)

```json
{
  "bookId": 1,
  "title": "How I Live Now",
  "author": "Meg Rosoff",
  "isbn": "978-0-14-138075-9",
  "edition": 4,
  "notes": "Libro en excelente estado",
  "available": true
}
```

#### Respuesta (404 Not Found)

```json
{
  "message": "Libro no encontrado"
}
```

---

### 6. Eliminar un libro

**DELETE** `/books/{bookId}`

Elimina un libro del inventario.

#### Parámetros

- `bookId` (path, requerido): ID del libro a eliminar

#### Ejemplo cURL

```bash
curl -X DELETE "http://localhost:5001/books/1" \
  -H "accept: application/json"
```

#### Respuesta (200 OK)

```json
{
  "message": "Libro eliminado."
}
```

#### Respuesta (404 Not Found)

```json
{
  "message": "Libro no encontrado"
}
```

---

## Integración con otros servicios

### Servicio de Disponibilidad

Este servicio consulta automáticamente el endpoint `/disponibilidad` del servicio de Disponibilidad para obtener información actualizada sobre la disponibilidad de libros.

- **URL del servicio**: Variable de entorno `DISP_SERVICE`
- **Endpoints consultados**:
  - `GET /disponibilidad` - Para obtener todos los libros y su disponibilidad
  - `GET /disponibilidad/{bookId}` - Para obtener la disponibilidad de un libro específico

### Servicio de Préstamos

El servicio de Préstamos consulta este servicio para verificar si los libros están disponibles antes de crear un préstamo.

- **URL de este servicio**: Variable de entorno `INVENTARIO_SERVICE` (en otros servicios)
- **Endpoints consultados**:
  - `GET /books/available` - Para obtener libros disponibles

---
