from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date

class Prestamo(BaseModel):
    """
    Represents a book loan in the library system.
    """
    loanId: int = Field(..., description="Identificador único del préstamo")
    user: str = Field(..., description="Nombre o ID del usuario que solicitó el préstamo")
    books: list[str] = Field(..., description="Lista de IDs de libros prestados")
    loanDueDate: date = Field(..., description="Fecha de vencimiento del préstamo (formato: YYYY-MM-DD)")
    status: str = Field(..., description="Estado actual del préstamo (ACTIVE, ARCHIVED, FINALIZED)")

############################
# Base de datos en memoria #
############################

prestamos_list: List[Prestamo] = []
_prestamos_id_counter = 2

prestamo_1 = Prestamo(
    loanId=1,
    user="Xavier Benitez",
    books=["4"],
    loanDueDate=date(2026, 12, 31),
    status="active"
)

# Agregar préstamos iniciales a la lista
prestamos_list.append(prestamo_1)

#################################
# Helpers para la base de datos #
#################################

def next_prestamo_id_get() -> int:
    """
    Returns next Prestamo id
    """
    global _prestamos_id_counter
    current_id = _prestamos_id_counter
    _prestamos_id_counter += 1
    return current_id