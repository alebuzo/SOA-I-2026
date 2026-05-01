from flask import Flask, jsonify, request
from faker import Faker
from flasgger import Swagger, swag_from
from marshmallow import Schema, fields, ValidationError
from typing import Optional

app = Flask(__name__)

# Definición del esquema de validación para un libro
class BookSchema(Schema):
    bookId = fields.Int(required=True, metadata={"example": 42})
    title = fields.Str(required=True, metadata={"example": "How I live Now"})
    author = fields.Str(required=True, metadata={"example": "Meg Rosoff"})
    isbn = fields.Str(required=True, metadata={"example": "978-0-14-138075-9"})
    edition = fields.Int(required=True, metadata={"example": 1})
    notes = fields.Str(required=False, metadata={"example": "Libro en buen estado"})

# Instanciamos el esquema para validación mas adelante
book_schema = BookSchema()

def marshmallow_to_swagger(schema_class):
    """Convierte un esquema de Marshmallow a una definición de Swagger."""
    _type_map = {
        fields.Str: "string",
        fields.Int: "integer",
        fields.Float: "number",
        fields.Bool: "boolean",
    }
    properties = {}
    required_fields = []
    for field_name, field_obj in schema_class._declared_fields.items():
        swagger_type = next(
            (t for cls, t in _type_map.items() if isinstance(field_obj, cls)),
            "string",
        )
        prop = {"type": swagger_type}
        example = (field_obj.metadata or {}).get("example")
        if example is not None:
            prop["example"] = example
        properties[field_name] = prop
        if field_obj.required:
            required_fields.append(field_name)
    definition = {"type": "object", "properties": properties}
    if required_fields:
        definition["required"] = required_fields
    return definition

swagger_template = {
    "info": {
        "title": "API del Inventario",
        "version": "1.0",
        "description": "Un API para manejar el inventario de libros en la biblioteca.",
        "termsOfService": "https://catoftheday.com/",
        "contact": {
            "responsibleOrganization": "Cat of the Day",
            "responsibleDeveloper": "Alexa Buzo",
            "email": "al.cbuzo@gmail.com",
            "url": "https://catoftheday.com/",
        },
    },
    "definitions": {
        "Book": marshmallow_to_swagger(BookSchema),
    }
}

swagger = Swagger(app, template=swagger_template)


##################################################
# Base de datos en memoria para el inventario
##################################################

faker = Faker()
INVENTARIO: list[dict] = []
for i in range(1, 20):
    INVENTARIO.append({
        "bookId": i,
        "title": faker.sentence(nb_words=4),
        "author": faker.name(),
        "isbn": faker.isbn13(),
        "edition": faker.random_int(min=1, max=5),
        "notes": faker.sentence(nb_words=6)
    })

################################################

# Rutas del API

@app.route('/books', methods=['GET'])
@swag_from('swagger/get_books.yml', validation=False)
def get_books():
    return jsonify(INVENTARIO)
