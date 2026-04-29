from marshmallow import Schema, fields, validate


class BookSchema(Schema):
    """Schema para Book (sin availability)"""
    bookId = fields.Int(dump_only=True, metadata={"example": 42})
    title = fields.Str(required=True, metadata={"example": "How I live Now"})
    author = fields.Str(required=True, metadata={"example": "Meg Rosoff"})
    isbn = fields.Str(required=True, metadata={"example": "978-0-14-138075-9"})
    edition = fields.Int(required=True, metadata={"example": 1})
    notes = fields.Str(required=False, metadata={"example": "Libro en buen estado"})
    available = fields.Bool(required=False, allow_none=True, metadata={"example": True})

# Instancia del schema de Book
book_schema = BookSchema()