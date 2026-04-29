from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class Book(BaseModel):
    """
    Book model representa una copia física del libro en la biblioteca
    """
    bookId: int = Field(..., example=42)
    title: str = Field(..., example="How I Live Now")
    author: str = Field(..., example="Meg Rosoff")
    isbn: str = Field(..., example="978-0-14-138075-9")
    edition: int = Field(..., example=2)
    notes: Optional[str] = Field(None, example="Libro en buen estado")
    # Ref a clase Availability
    availability: Optional[str] = None


############################
# Base de datos en memoria #
############################

books_list: List[Book] = []

_book_id_counter = 1


#################################
# Helpers para la base de datos #
#################################

def next_book_id_get() -> int:
    """
    Returns next book id
    """
    global _book_id_counter
    current_id = _book_id_counter
    _book_id_counter += 1
    return current_id
