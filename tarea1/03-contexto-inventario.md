# Contexto delimitado: Inventario de libros

## Tabla de contenidos

- [Descripción](#descripción)
- [Responsabilidades](#responsabilidades)
  - [Lenguaje ubicuo](#lenguaje-ubicuo)
- [Modelo del dominio](#modelo-del-dominio)
  - [Entidad principal: Libro](#entidad-principal-libro)
  - [Entidad: Disponibilidad](#entidad-disponibilidad)
  - [Lo que el contexto no sabe](#lo-que-el-contexto-no-sabe)
- [Eventos](#eventos)
  - [Eventos emitidos](#eventos-emitidos-publicados-por-este-contexto)
  - [Eventos consumidos](#eventos-consumidos)
- [Diagramas](#diagramas)
  - [Comunicación interna del contexto](#comunicación-interna-del-contexto)
  - [Ciclo de estados de disponibilidad](#ciclo-de-estados-de-disponibilidad)
  - [Relación entre Libro y Disponibilidad](#relación-entre-libro-y-disponibilidad)
  - [Comunicación con otros contextos](#comunicación-con-otros-contextos)
- [Resumen](#resumen)


## Descripción

El inventario de libros maneja cuáles libros existen en la biblioteca. Define sus características o atributos y principalmente, les asigna un atributo que define si están disponibles para préstamos o no. Bajo este contexto, si el inventario define que un libro no está disponible, significa que el libro sigue siendo propiedad de la biblioteca y el libro físico existe pero no puede ser prestado. Algunas razones pueden ser el alto valor del libro, única copia en la biblioteca, en estado de préstamo, en restauración, etc. El contexto no sabe de usuarios de la biblioteca, no tiene visibilidad de préstamos pendientes ni retornos en proceso.

## Responsabilidades

- Definición y atributos de los libros (id, título, autor, isbn, edición, disponibilidad)
- Mantener el inventario de la totalidad de libros propiedad de la biblioteca.

### Lenguaje ubicuo

| Término           | Significado en este contexto                          |
| ----------------- | ----------------------------------------------------- |
| **Libro**         | Copia física de algún libro en la biblioteca          |
| **Disponibilidad**| Status de una copia. Si puede ser prestada o no       |
| **Búsqueda**      | Consulta sobre el inventario                          |

## Modelo del dominio

### Entidad principal: Libro

Un **Libro** es una copia física de un libro con cierto ISBN, edición, título, autor, etc.

```
Libro {
    id,
    titulo,
    autor,
    isbn,
    edicion,
    notas
}
```

### Entidad: Disponibilidad

La **Disponibilidad** representa el estado actual de préstamo de un libro específico.

```
Disponibilidad {
    id,
    libroId,  // FK to Libro.id
    disponible,   // True, False
    razon,    // LOANED, RESTORATION, HIGH_VALUE, etc.
    fechaActualizacion
}
```

### Lo que el contexto no sabe

- Usuarios con intención de préstamo.
- Usuarios con préstamos activos.
- Retornos procesados.
- Multas creadas y enviadas a usuarios.

## Eventos

### Eventos emitidos (publicados por este contexto)

| Evento                  | Descripción                                          | Consumidores típicos                     |
| ----------------------- | ---------------------------------------------------- | ---------------------------------------- |
| `BookAdded`             | Un nuevo libro está disponible en el inventario      | Préstamos (para mostrar al usuario)     |
| `BookInfoUpdated`       | Cambios en título, autor, ISBN, edición o disponibilidad | Préstamos (solo referencia)         |
| `BookRemoved`           | El libro es removido del inventario                  | Préstamos (evitar préstamos de libros removidos) |

### Eventos consumidos

| Evento           | Descripción                                          | Origen (contexto emisor)                 |
| ---------------- | ---------------------------------------------------- | ---------------------------------------- |
| `LoanIssued`     | Un libro ha sido prestado, dejando de estar disponible | Préstamos                                |
| `ReturnProcessed`| Un libro ha sido devuelto y vuelve a estar disponible | Retornos                                 |


## Diagramas

### Comunicación interna del contexto

```mermaid
flowchart TB
    subgraph Inventario["Contexto: Inventario de Libros"]
        direction TB
        A[Gestor de Libros] --> B[(Repositorio de Libros)]
        A --> C[Servicio de Disponibilidad]
        C --> D[(Repositorio de Disponibilidad)]
        E[Servicio de Búsqueda] --> B
        E --> D
        F[API Inventario] --> A
        F --> E
        G[Manejador de Eventos] --> C
        H[Publicador de Eventos] --> A
    end

    A -->|BookAdded / BookInfoUpdated / BookRemoved| H
    G -->|LoanIssued / ReturnProcessed| C
```

## Ciclo de estados de disponibilidad

```mermaid
stateDiagram-v2
    [*] --> Disponible: Libro agregado
    Disponible --> No_Disponible: LoanIssued
    No_Disponible --> Disponible: ReturnProcessed
    Disponible --> [*]: Libro removido
    No_Disponible --> [*]: Libro removido
```

## Relación entre Libro y Disponibilidad

```mermaid
erDiagram
    Libro {
        string id PK
        string titulo
        string autor
        string isbn
        string edicion
        string notas
    }

    Disponibilidad {
        string id PK
        string libroId FK
        boolean disponible
        string razon
        datetime fechaActualizacion
    }

    Libro ||--o{ Disponibilidad : "tiene"
```


## Comunicación con otros contextos

``` mermaid
sequenceDiagram
    participant Inventario as Inventario
    participant Prestamos as Préstamos
    participant Retornos as Retornos
    participant Bus as Bus de Eventos

    Inventario->>Bus: BookAdded, BookInfoUpdated, BookRemoved
    Bus->>Prestamos: (suscripción)
    Prestamos->>Inventario: API: Obtener disponibilidad de libros
    Prestamos->>Bus: LoanIssued
    Bus->>Inventario: Actualizar disponibilidad de libros (from LoanIssued)
    Retornos->>Bus: ReturnProcessed
    Bus->>Inventario: Actualizar disponibilidad de libros (from ReturnProcessed)
```

Los otros dos contextos, Retornos y Préstamos son los que emiten los eventos que actualizan la disponibilidad de un libro.

```mermaid
flowchart LR
    subgraph Inventario["Inventario de Libros"]
        API[API Consulta]
        EV[Eventos: LibroAdded, BookInfoUpdated, BookRemoved]
        D[Servicio de Disponibilidad]
    end

    subgraph Prestamos["Préstamos"]
        CP[Confirmar Prestamo]
        PV[Eventos: LoanIssued]
    end

    subgraph Retornos["Retornos"]
        GR[Gestionar Retorno]
        RV[Eventos: ReturnProcessed]
    end

    API -->|Consulta producto, precio, categoría| CP
    EV -->|Suscrito| CP
    D -->|Suscrito| RV
    D -->|Suscrito| PV
```

## Resumen

| Aspecto             | Detalle                                                                   |
| ------------------- | ------------------------------------------------------------------------- |
| **Responsabilidad** | Gestionar el inventario de libros y sus especificaciones y disponibilidad |
| **Libro**           | Copia física de un libro                                                  |
| **Comunicación**    | Emite eventos de cambios de información de los libros; expone API de consulta para Préstamos |
| **Independencia**   | La disponilidad depende de los contextos retornos y préstamos             |      

