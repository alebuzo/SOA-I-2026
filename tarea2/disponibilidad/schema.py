from marshmallow import Schema, fields, validate

class DisponibilidadSchema(Schema):
    """Schema de Disponibilidad"""
    disponibilidadId = fields.Int(dump_only=True, metadata={"example": 100})
    bookId = fields.Int(required=True, metadata={"example": 42})
    available = fields.Bool(required=True, metadata={"example": True})
    reason = fields.Str(
        allow_none=True,
        validate=validate.OneOf(['LOANED', 'RESTORATION', 'HIGH_VALUE', 'UNIQUE_COPY', 'LOST', 'OTHER']),
        metadata={"example": "LOANED"}
    )
    lastUpdated = fields.DateTime(dump_only=True)

# Instancias del schema de Disponibilidad
disponibilidad_schema = DisponibilidadSchema()
