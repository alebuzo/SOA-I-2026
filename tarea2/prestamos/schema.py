import os
import logging
import strawberry
import requests
from faker import Faker
from datetime import date
from typing import Optional
from datetime import datetime
from strawberry.experimental.pydantic import type as pydantic_type

from models import Prestamo, prestamos_list, next_prestamo_id_get


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

disp_service = os.getenv('DISP_SERVICE')

##################################
# Llenar base de datos con Faker #
##################################

faker = Faker()
for i in range(1, 7):
    prestamos_list.append(Prestamo(
        loanId=next_prestamo_id_get(),
        user=faker.name(),
        books=[str(faker.random_int(min=1, max=100)) for _ in range(faker.random_int(min=1, max=5))],
        loanDueDate=faker.date_between(start_date='today', end_date='+30d'),
        status=faker.random_element(elements=["ACTIVE", "ARCHIVED", "FINALIZED"])
    ))


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

@strawberry.input
class GetSoonToExpirePrestamosInput:
    time: int


@strawberry.type
class QueryPrestamo:
    @strawberry.field
    def prestamo(self, loanId: int) -> Optional[PrestamoGraphQL]:
        for p in prestamos_list:
            if p.loanId == loanId:
                logging.info("Prestamo con id %d encontrado", loanId)
                return PrestamoGraphQL.from_pydantic(p)
        logging.info("Prestamo con id %d NO encontrado", loanId)
        return None

    @strawberry.field
    def prestamos(self) -> list[PrestamoGraphQL]:
        return [PrestamoGraphQL.from_pydantic(p) for p in prestamos_list]

    @strawberry.field
    def prestamos_by_user(self, user: str) -> list[PrestamoGraphQL]:
        resultados = []
        prestamos_de_user = [p for p in prestamos_list if p.user == user]
        resultados = [PrestamoGraphQL.from_pydantic(p) for p in prestamos_de_user]
        logging.info("Prestamos para usuario %s encontrados: %d", user, len(resultados))
        return resultados

    @strawberry.field
    def get_soon_to_expire_prestamos(self, input: GetSoonToExpirePrestamosInput) -> list[PrestamoGraphQL]:
        resultados = []
        today = datetime.now().date()
        for p in prestamos_list:
            if p.loanDueDate:
                days_until_due = (p.loanDueDate - today).days
                if 0 <= days_until_due <= input.time and p.status == "ACTIVE":
                    logging.info("Prestamo con id %d pronto a expirar", p.loanId)
                    resultados.append(PrestamoGraphQL.from_pydantic(p))
        logging.info("Prestamos pronto a expirar encontrados: %d", len(resultados))
        return resultados

@strawberry.type
class MutatePrestamo:
    @strawberry.mutation
    def add_prestamo(self, input: CrearPrestamoInput) -> PrestamoGraphQL:
        # Verificar que los libros estén disponibles antes de crear el préstamo
        for book_id in input.books:
            response = requests.get(f"{disp_service}/disponibilidad/{book_id}")
            if response.status_code != 200:
                logging.error("Error al verificar disponibilidad del libro con id %s: %s", book_id, response.text)
                raise Exception(f"Error al verificar disponibilidad del libro con id {book_id}")
            disponibilidad_info = response.json()
            if not disponibilidad_info.get('available', False):
                logging.warning("Libro con id %s no disponible para préstamo", book_id)
                raise Exception(f"Libro con id {book_id} no disponible para préstamo")
        nuevo_prestamo = Prestamo(
            loanId=next_prestamo_id_get(),
            user=input.user,
            books=input.books,
            loanDueDate=input.loanDueDate,
            status="active"
        )
        prestamos_list.append(nuevo_prestamo)
        logging.info("Prestamo con id %d creado para usuario %s", nuevo_prestamo.loanId, nuevo_prestamo.user)
        return PrestamoGraphQL.from_pydantic(nuevo_prestamo)

    @strawberry.mutation
    def update_status_prestamo(self, input: ActualizarEstadoPrestamoInput) -> Optional[PrestamoGraphQL]:
        prestamo = next((p for p in prestamos_list if p.loanId == input.loanId), None)
        if prestamo:
            prestamo.status = input.status
            logging.info("Prestamo con id %d actualizado a estado %s", input.loanId, input.status)
            return PrestamoGraphQL.from_pydantic(prestamo)
        logging.info("Prestamo con id %d NO encontrado", input.loanId)
        return None

    @strawberry.mutation
    def delete_prestamo(self, loanId: int) -> bool:
        prestamo = next((p for p in prestamos_list if p.loanId == loanId), None)
        if prestamo:
            prestamos_list.remove(prestamo)
            logging.info("Prestamo con id %d eliminado", loanId)
            return True
        logging.info("Prestamo con id %d NO encontrado", loanId)
        return False

schema = strawberry.Schema(query=QueryPrestamo, mutation=MutatePrestamo)