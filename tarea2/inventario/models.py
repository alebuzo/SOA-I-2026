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
    availability: Optional['Availability'] = None 

    class Config:
        arbitrary_types_allowed = True

class Availability(BaseModel):
    """
    Availability model representa el status de un libro en la
    biblioteca
    """
    availabilityId: int = Field(..., example=100)
    bookId: int = Field(..., example=42)
    available: bool = Field(..., example=True)
    reason: Optional[str] = Field(None, example="ON LOAN")
    # Use current time
    lastUpdated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat()
            }


############################
# Base de datos en memoria #
############################

books_list: List[Book] = []
availability_list: List[Availability] = []

_book_id_counter = 1
_availability_id_counter = 1


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

def next_availability_id_get() -> int:
    """
    Returns next availability id
    """
    global _availability_id_counter
    current_id = _availability_id_counter
    _availability_id_counter += 1
    return current_id