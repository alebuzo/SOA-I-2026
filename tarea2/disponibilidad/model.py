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
    lastUpdated: datetime = Field(default_factory=datetime.now())

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

############################
# Base de datos en memoria #
############################

disponibilidad_list: List[Disponibilidad] = []
_disponibilidad_id_counter = 1

disponibilidad_1 = Disponibilidad(
    disponibilidadId=5,
    bookId=1,
    available=True,
    reason=None,
    lastUpdated=datetime.now()
)
disponibilidad_2 = Disponibilidad(
    disponibilidadId=6,
    bookId=3,
    available=True,
    reason=None,
    lastUpdated=datetime.now()
)
disponibilidad_3 = Disponibilidad(
    disponibilidadId=3,
    bookId=4,
    available=False,
    reason="ON LOAN",
    lastUpdated=datetime.now()
)
# Agregar disponibilidades iniciales a la lista
disponibilidad_list.extend([disponibilidad_1, disponibilidad_2, disponibilidad_3])

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