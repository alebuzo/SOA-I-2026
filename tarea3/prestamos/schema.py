import os
import logging
import strawberry
import requests
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

inventario_service = os.getenv('INVENTARIO_SERVICE')

@pydantic_type(model=Prestamo, all_fields=True, description="Representa un préstamo de libros en el sistema de la biblioteca")
class PrestamoGraphQL:
    pass

@strawberry.input(description="Input para crear un nuevo préstamo")
class CrearPrestamoInput:
    user: str = strawberry.field(description="Nombre o ID del usuario que solicita el préstamo")
    books: list[str] = strawberry.field(description="Lista de IDs de libros a prestar")
    loanDueDate: date = strawberry.field(description="Fecha de vencimiento del préstamo (formato: YYYY-MM-DD)")

@strawberry.input(description="Input para actualizar el estado de un préstamo existente")
class ActualizarEstadoPrestamoInput:
    loanId: int = strawberry.field(description="ID único del préstamo a actualizar")
    status: str = strawberry.field(description="Nuevo estado del préstamo (ACTIVE, ARCHIVED, FINALIZED)")

@strawberry.input(description="Input para consultar préstamos próximos a expirar")
class GetSoonToExpirePrestamosInput:
    time: int = strawberry.field(description="Número de días para considerar 'próximo a expirar' (ej: 7 = próximos 7 días)")


@strawberry.type(description="Consultas disponibles para el servicio de préstamos")
class QueryPrestamo:
    @strawberry.field(description="Obtiene un préstamo específico por su ID. Retorna null si no existe.")
    def prestamo(self, loanId: int) -> Optional[PrestamoGraphQL]:
        for p in prestamos_list:
            if p.loanId == loanId:
                logging.info("Prestamo con id %d encontrado", loanId)
                return PrestamoGraphQL.from_pydantic(p)
        logging.info("Prestamo con id %d NO encontrado", loanId)
        return None

    @strawberry.field(description="Obtiene todos los préstamos existentes en el sistema")
    def prestamos(self) -> list[PrestamoGraphQL]:
        return [PrestamoGraphQL.from_pydantic(p) for p in prestamos_list]

    @strawberry.field(description="Obtiene todos los préstamos asociados a un usuario específico")
    def prestamos_by_user(self, user: str) -> list[PrestamoGraphQL]:
        resultados = []
        prestamos_de_user = [p for p in prestamos_list if p.user == user]
        resultados = [PrestamoGraphQL.from_pydantic(p) for p in prestamos_de_user]
        logging.info("Prestamos para usuario %s encontrados: %d", user, len(resultados))
        return resultados

    @strawberry.field(description="Obtiene todos los préstamos próximos a expirar en time días o menos")
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

@strawberry.type(description="Mutaciones disponibles para el servicio de préstamos")
class MutatePrestamo:
    @strawberry.mutation(description="Crea un nuevo préstamo de libros. Verifica que los libros solicitados estén disponibles antes de crear el préstamo.")
    def add_prestamo(self, input: CrearPrestamoInput) -> PrestamoGraphQL:
        # Verificar que existe una copia del libro en el inventario, tomar su bookId y consultar su disponibilidad
        response = requests.get(f'{inventario_service}/books/available')
        if response.status_code != 200:
            logging.error("Error al verificar los libros disponibles: %s", response.text)
            raise Exception("Error al verificar los libros disponibles en la biblioteca")
        # Comparar input.books con los libros disponibles y verificar que todos los libros solicitados estén disponibles
        available_books = response.json()
        for book_id in input.books:
            if not any(str(book['bookId']) == book_id for book in available_books):
                logging.info("Libro con id %s no disponible para préstamo", book_id)
                raise Exception(f"Libro con id {book_id} no disponible para préstamo")
        # Si todos los libros están disponibles, crear el préstamo
        nuevo_prestamo = Prestamo(
            loanId=next_prestamo_id_get(),
            user=input.user,
            books=input.books,
            loanDueDate=input.loanDueDate,
            status="ACTIVE"
        )
        prestamos_list.append(nuevo_prestamo)
        logging.info("Prestamo con id %d creado para usuario %s", nuevo_prestamo.loanId, nuevo_prestamo.user)
        return PrestamoGraphQL.from_pydantic(nuevo_prestamo)

    @strawberry.mutation(description="Actualiza el estado de un préstamo existente")
    def update_status_prestamo(self, input: ActualizarEstadoPrestamoInput) -> Optional[PrestamoGraphQL]:
        prestamo = next((p for p in prestamos_list if p.loanId == input.loanId), None)
        if prestamo:
            prestamo.status = input.status
            logging.info("Prestamo con id %d actualizado a estado %s", input.loanId, input.status)
            return PrestamoGraphQL.from_pydantic(prestamo)
        logging.info("Prestamo con id %d NO encontrado", input.loanId)
        return None

    @strawberry.mutation(description="Elimina un préstamo existente")
    def delete_prestamo(self, loanId: int) -> bool:
        prestamo = next((p for p in prestamos_list if p.loanId == loanId), None)
        if prestamo:
            prestamos_list.remove(prestamo)
            logging.info("Prestamo con id %d eliminado", loanId)
            return True
        logging.info("Prestamo con id %d NO encontrado", loanId)
        return False

schema = strawberry.Schema(query=QueryPrestamo,
                           mutation=MutatePrestamo)
