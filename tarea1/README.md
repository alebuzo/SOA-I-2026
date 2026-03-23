Tarea #1: Contextos delimitados (Préstamos, Retornos e Inventario)

Estos tres contextos pertenecen a un escenario de préstamo de libros en una biblioteca, donde cierto usuario tiene la posibilidad de obtener un préstamo de libros con cierto tiempo límite y debe realizar el retorno de los materiales antes de dicho tiempo límite. Los contextos se comunican por APIs para realizar consultas y eventos (publicación/suscripción). Cada contexto se describe a continuación.

## Tabla de contenidos

- [Contextos y documentación](#contextos-y-documentación)
- [Diagrama: interacción entre contextos](#diagrama-interacción-entre-contextos)
    - [Flujo de eventos](#flujos-de-eventos)
- [Eventos por contexto](#eventos-por-contexto)
- [Resumen de cada contexto](#resumen-de-cada-contexto)

## Contextos y documentación

| Contexto | Responsabilidad | Documentación |
|----------|-----------------|---------------|
| Préstamos| Crear y gestionar los préstamos de libros | [Contexto de Préstamos](./01-contexto-prestamos.md) |
| Retornos | Gestionar los retornos de los libros | [Contexto de Retornos](./02-contexto-retornos.md) |
| Inventario | Gestionar la disponibilidad de libros en la biblioteca | [Contexto de Inventario](./03-contexto-inventario.md) |

## Diagrama: interacción entre contextos

- Líneas sólidas: API (Préstamos consulta disponibilidad del libro al inventario, retornos consulta existencia del préstamo a préstamo)
- Líneas punteadas: eventos (Retornos -> Préstamos, Inventario -> Préstamos, Retornos -> Inventario).

``` mermaid
flowchart TD
    subgraph Inventario["Inventario de Libros"]
    I_API[API Consulta]
    I_Actualizar[Actualizar disponibilidad de libros]
    I_EV[Eventos: BookAdded, BookInfoUpdated, BookRemoved]
    end

    subgraph Prestamos["Préstamos"]
        P_API[API Consulta]
        P_Prestamo[Pedir préstamo de libros]
        P_EV[Eventos: LoanIssued, LoanDueDateWarningIssued, LoanDueDateReached]
    end

    subgraph Retornos["Retornos"]
    R_Retorno[Procesar retorno]
    R_EV[Eventos: ReturnProcessed, FineIssued]
    end

    I_API -->|consulta| P_Prestamo
    I_EV -.->|suscrito| P_Prestamo
    P_EV -.->|suscrito| I_Actualizar
    R_EV -.->|suscrito| I_Actualizar
    P_API -->|consulta| R_Retorno
```

## Flujo de eventos

```m̀ermaid
sequenceDiagram
    participant Inventario as Inventario
    participant Prestamos as Préstamos
    participant Retornos as Retornos
    participant Bus as Bus de Eventos
    participant Notificaciones as Notificaciones (Servicio)

    Inventario->>Bus: BookAdded, BookInfoUpdated, BookRemoved
    Bus->>Prestamos: (suscripción)
    Prestamos->>Inventario: API: Obtener disponibilidad de libros
    Prestamos->>Bus: LoanIssued
    Bus->>Inventario: Actualizar disponibilidad de libros (from LoanIssued)
    Prestamos->>Bus: LoanDueDateWarningIssued
    Bus->>Notificaciones: LoanDueDateWarningIssued
    Prestamos->>Bus: LoanDueDateReached
    Bus->>Notificaciones: LoanDueDateReached
    Retornos->>Prestamos: API: Obtener préstamo
    Retornos->>Bus: ReturnProcessed
    Bus->>Inventario: Actualizar disponibilidad de libros (from ReturnProcessed)
    Retornos->>Bus: FineIssued
    Bus->>Notificaciones: ReturnProcessed/FineIssued
```

## Eventos por contexto

| Contexto       | Emite                                                    | Consume                                 |
| -------------- | -------------------------------------------------------- | --------------------------------------- |
| **Inventario** | BookAdded, BookInfoUpdated, BookRemoved                  | LoanIssued, ReturnProcessed             |
| **Préstamos**  | LoanIssued, LoanDueDateWarningIssued, LoanDueDateReached | BookAdded, BookInfoUpdated, BookRemoved |
| **Retornos**   | ReturnProcessed, FineIssued                              | -                                       |


## Resumen de cada contexto

- **Inventario**: Libro = Propiedad disponible o no disponible en la biblioteca. Libro (`id`, `titulo`, `isbn`, `autor`). No sabe de préstamos o retornos, solo si el libro está o no. Estados: AVAILABLE o NOT_AVAILABLE
- **Préstamos**: Libro = Objeto fuera de la biblioteca. Compromete al usuario. `loanItem {loanId, client, books, loanDueDate}`
- **Retornos**: Libro = Objeto vuelve a la biblioteca. Libera al usuario y/o le genera multas. `returnItem {returnId, loanId, client, fineAmount}`.

El mismo concepto cambia de significado por contexto:

| Concepto     | Inventario    | Préstamos         | Retornos          |
| ------------ | ------------- | ----------------- | ----------------- |
| **Libro**    | Propiedad     | Item prestado     | Item devuelto     |
| **Cliente**  | Visitante     | Prestatario       | Deudor            |
| **Multa**    | Irrelevante   | Bloqueo           | Sanción por pagar |


**Microservicios típicos:** Inventory Service, Loan Service, Return Service, Notification Service.

Pregunta: un evento puede ser consumido por dos contextos o debería ser consumido por uno primero y luego ese genera algo que el segundo consuma?
**** Falta agregar el paso de Borrar el préstamo