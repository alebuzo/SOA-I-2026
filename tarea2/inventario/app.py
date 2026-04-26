from flask import Blueprint, request, jsonify
from models import Book, Availability, books_list, availability_list, next_book_id_get, next_availability_id_get
from schemas import book_schema, book_with_availability_schema, books_with_availability_schema, availability_schema


inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

###########
# Swagger #
###########

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
        "Book": marshmallow_to_swagger(book_schema),
    }
}

swagger = Swagger(app, template=swagger_template)


##################################
# Llenar base de datos con Faker #
##################################

for i in range(1, 20):
    books_list.append({
        "bookId": i,
        "title": faker.sentence(nb_words=4),
        "author": faker.name(),
        "isbn": faker.isbn13(),
        "edition": faker.random_int(min=1, max=5),
        "notes": faker.sentence(nb_words=6)
    })

for i in range(1, 20):
    availability_list

@inventory_bp.route('/books', methods=['GET'])
def get_books():
