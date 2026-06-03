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
    # Ref a clase Disponibilidad para obtener el estado de disponibilidad del libro
    available: Optional[bool] = None


############################
# Base de datos en memoria #
############################

books_list: List[Book] = []

_book_id_counter = 5

book_1 = Book(
    bookId=1,
    title="How I Live Now",
    author="Meg Rosoff",
    isbn="978-0-14-138075-9",
    edition=1,
    notes="Libro en buen estado",
    available=True
)

book_2 = Book(
    bookId=3,
    title="The Great Gatsby",
    author="F. Scott Fitzgerald",
    isbn="978-0-7432-7356-5",
    edition=2,
    notes="Libro con algunas páginas dobladas",
    available=True
)

book_3 = Book(
    bookId=4,
    title="To Kill a Mockingbird",
    author="Harper Lee",
    isbn="978-0-06-112008-4",
    edition=1,
    notes="Libro con la portada dañada",
    available=False
)

# Agregar libros iniciales a la lista
books_list.extend([book_1, book_2, book_3])
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
