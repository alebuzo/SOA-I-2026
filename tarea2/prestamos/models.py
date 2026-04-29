from typing import Optional, List
from pydantic import BaseModel
from datetime import date

class Prestamo(BaseModel):
    """
    Represents a book loan in the library system.

    Attributes:
        loanId (int): Unique identifier for the loan.
        user (str): The name or ID of the user who borrowed the books.
        books (list[str]): List of book IDs that were borrowed.
        loanDueDate (date): The due date for returning the books.
        status (str): Current state of the loan (e.g., "active", "returned").
    """
    loanId: int
    user: str
    books: list[str]
    loanDueDate: date
    status: str

############################
# Base de datos en memoria #
############################

prestamos_list: List[Prestamo] = []
_prestamos_id_counter = 1

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