# Ownership & Boundaries

Who owns the status of the book? Which context is the source of truth? The catalog
Who owns the status of the loan? Which context is the source of truth? The lending


- So if any context needs to request information from the loan (returnDate, loanId, booksLoaned), it needs to request it from the lending context
- If any context needs to request information from any book (id, status, metadata), it needs to request it from the catalog context

Should contexts modify the other's data? 

- No. Return context should not access the loans or the books status.
- Samewise, the lending context should not have access to the catalog data.

# Triggers & Events

What actions can a user or system take in this context?

- Lending context: users can request a loan of a set of books
- Return context: user can processed a return or ask for return date.
- Catalog: users directly don't have access to this context, but they consult the availability of books through the lending context.

What facts does this context need to announce to the rest of the world when something happens?

- Lending context: when a loan is created, when a loan is getting close to its due date and when it is overdue.
- Return context: a return has beeen processed or a fine was issued.
- catalog context: if a book has been added, removed or updated in the inventory and if a book is available or not.

What events from other contexts does this context need to react to?

- Lending context: reacciona a cambios en el inventario: libros retirados, metadata actualizada o libros agregados para mostrar a los users.
- Return context: no reacciona a ningún evento de otro contexto.
- Catalog context: reacciona a prestamos hechos para quitar el status de available a un libro y reacciona a cuando un libro se devuelve para ponerle available

Is this something that happened (an event) or something being requested (a command)?

- Lending: Knowing if a book is available at a lending procedure is an inmediate request to the catalog. Removing the loan can be done later, so it is a event.
- Return context: Asking if a loan is still pending is a request. Asking the due date is a request. Both to the lending context. A return processed can be done later, so it's an event.
- Catalog context: poner un libro available o not available es un evento. el catalogo no le hace requests a nadie.

# API Design

Who are the consumers of this context's API — other services, a frontend, or both?

- Catalog context: disponibilidad del libro: consumidor? el contexto de lending
- Lending context: verificación del prestamo, request del due date: consumidor? return context. Cancelar prestamo, lo pide el request.
- Request context: no tiene una API?

What does a consumer need to query from this context, and what do they need to change?

- Catalog context: disponibilidad del libro (query)
- Lending context: verificación del prestamo (query) request del due date (query) cancel loan (change)
- Request context: no tiene una API?

Should this be a synchronous request-response, or is it fine for it to be asynchronous?

- disponibilidad del libro, verificación del prestamo, request del due date son sincrónicas porque hay que responderle al usuario. Cancel loan se puede hacer después.

# Data & Consistency

What is the minimum data each context needs to do its job, without borrowing from another context's model?

- catalog context: for a book (available status, id, title, ISBN, author, etc)
- lending context: a loan (client, books_ids, dueDate, id)
- return context: return (loan_id, id, client) fine (client, loan_id, fine_amount)

When two contexts talk about the same real-world thing (like a "book"), do they mean exactly the same thing, or do they each care about different aspects of it?

- Catalog: a book is an object that lives in the inventory and is available or not available.
- lending: a book is an object that is part of a loan and has a date to be brought back.
- return: a book is an object that's been brought back and might incur in a fine depending on the date it's being processed.

What happens if a message between contexts is delayed or lost — does the system end up in an inconsistent state?

If a message is delayed or lost in the requests, the loans can't be processed. If an event is not received, then the system ends up ina insconsistent state.

