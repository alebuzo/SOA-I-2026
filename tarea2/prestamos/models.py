from pydantic import BaseModel
from datetime import date

class Prestamo(BaseModel):
    """
    Represents a book loan in the library system.

    Attributes:
        loanId (int): Unique identifier for the loan.
        user (str): The name or ID of the user who borrowed the books.
        books (list[str]): List of book titles or IDs that were borrowed.
        loanDueDate (date): The due date for returning the books.
        status (str): Current state of the loan (e.g., "active", "returned").
    """
    loanId: int
    user: str
    books: list[str]
    loanDueDate: date
    status: str