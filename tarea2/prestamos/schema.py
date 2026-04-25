import logging
import strawberry
from datetime import date
from typing import Optional
from strawberry.experimental.pydantic import type as pydantic_type

from models import Prestamo


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


@pydantic_type(model=Prestamo, all_fields=True)
class PrestamoGraphQL:
    pass

@strawberry.input
class CrearPrestamoInput:
    user: str
    books: list[str]
    loanDueDate: date

@strawberry.input
class ActualizarEstadoPrestamoInput:
    loanId: int
    status: str

PRESTAMOS: list[Prestamo] = []
_next_id = 1

@strawberry.type
class QueryPrestamo:
    @strawberry.field
    def prestamo(self, loanId: int) -> Optional[PrestamoGraphQL]:
        for p in PRESTAMOS:
            if p.loanId == loanId:
                logging.info("Prestamo con id %d encontrado", loanId)
                return PrestamoGraphQL.from_pydantic(p)
        logging.info("Prestamo con id %d NO encontrado", loanId)
        return None

@strawberry.type
class MutatePrestamo:
    @strawberry.mutation
    def crear_prestamo(self, input: CrearPrestamoInput) -> PrestamoGraphQL:
        global _next_id
        nuevo_prestamo = Prestamo(
            loanId=_next_id,
            user=input.user,
            books=input.books,
            loanDueDate=input.loanDueDate,
            status="active"
        )
        _next_id += 1
        PRESTAMOS.append(nuevo_prestamo)
        logging.info("Prestamo con id %d creado para usuario %s", nuevo_prestamo.loanId, nuevo_prestamo.user)
        return PrestamoGraphQL.from_pydantic(nuevo_prestamo)

    @strawberry.mutation
    def actualizar_estado_prestamo(self, input: ActualizarEstadoPrestamoInput) -> Optional[PrestamoGraphQL]:
        for p in PRESTAMOS:
            if p.loanId == input.loanId:
                p.status = input.status
                logging.info("Prestamo con id %d actualizado a estado %s", input.loanId, input.status)
                return PrestamoGraphQL.from_pydantic(p)
        logging.info("Prestamo con id %d NO encontrado para actualizar", input.loanId)
        return None

schema = strawberry.Schema(query=QueryPrestamo, mutation=MutatePrestamo)