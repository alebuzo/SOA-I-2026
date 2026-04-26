from marshmallow import Schema, fields, validate

class AvailabilitySchema(Schema):
    """Schema de Availability"""
    availabilityId = fields.Int(dump_only=True, metadata={"example": 100})
    bookId = fields.Int(required=True, metadata={"example": 42})
    available = fields.Bool(required=True, metadata={"example": True})
    reason = fields.Str(
        allow_none=True,
        validate=validate.OneOf(['LOANED', 'RESTORATION', 'HIGH_VALUE', 'UNIQUE_COPY']),
        metadata={"example": "LOANED"}
    )
    lastUpdated = fields.DateTime(dump_only=True)

class BookSchema(Schema):
    """Schema para Book (sin availability)"""
    bookId = fields.Int(dump_only=True, metadata={"example": 42})
    title = fields.Str(required=True, metadata={"example": "How I live Now"})
    author = fields.Str(required=True, metadata={"example": "Meg Rosoff"})
    isbn = fields.Str(required=True, metadata={"example": "978-0-14-138075-9"})
    edition = fields.Int(required=True, metadata={"example": 1})
    notes = fields.Str(required=False, metadata={"example": "Libro en buen estado"})

class BookWithAvailabilitySchema(BookSchema):
    """Schema extendido de Book con availability"""
    availability = fields.Nested(AvailabilitySchema, dump_only=True)

# Instancias de los schemas
availability_schema = AvailabilitySchema()
book_schema = BookSchema()
book_with_availability_schema = BookWithAvailabilitySchema()
books_with_availability_schema = BookWithAvailabilitySchema(many=True)