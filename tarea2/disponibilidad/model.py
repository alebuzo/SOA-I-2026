from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class Disponibilidad(BaseModel):
    """
    Disponibilidad model representa el status de un libro en la
    biblioteca
    """
    disponibilidadId: int = Field(..., example=100)
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

disponibilidad_list: List[Disponibilidad] = []
_disponibilidad_id_counter = 1

#################################
# Helpers para la base de datos #
#################################

def next_disponibilidad_id_get() -> int:
    """
    Returns next Disponibilidad id
    """
    global _disponibilidad_id_counter
    current_id = _disponibilidad_id_counter
    _disponibilidad_id_counter += 1
    return current_id