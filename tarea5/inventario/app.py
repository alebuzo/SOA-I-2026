import os
import uuid
import requests
import logging
from flasgger import Swagger, swag_from
from flask import Flask, request, jsonify, g
from marshmallow import Schema, fields, ValidationError
from model import Book, books_list, next_book_id_get
from schema import book_schema


app = Flask(__name__)

disp_service = os.getenv("DISP_SERVICE")



##################
# Correlation ID #
##################

class CorrelationIdFilter(logging.Filter):
    """Filtro de logging para incluir el Correlation ID en cada mensaje de log."""

    def filter(self, record) -> bool:
        # Agrega el Correlation ID al registro de log. Si no existe, usa "N/A".
        record.correlation_id = getattr(g, "correlation_id", "N/A")
        return True

# Crear el handler de logging con el filtro de Correlation ID
handler = logging.StreamHandler()
handler.addFilter(CorrelationIdFilter())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - cid-[%(correlation_id)s] %(message)s",
    handlers=[handler]
)

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

#########
# Hooks #
#########

@app.before_request
def set_correlation_id() -> None:
    """Hook que se ejecuta antes de cada petición HTTP para establecer el Correlation ID."""
    correlation_id = request.headers.get(
        "X-Correlation-ID") or str(uuid.uuid4())
    g.correlation_id = correlation_id
    logging.info(
        "Petición recibida - Correlation ID: %s (origen: %s)",
        g.correlation_id,
        "Header Entrante" if correlation_id else "Header Generado",
    )

@app.after_request
def attach_correlation_id(response):
    """Hook que se ejecuta después de cada petición HTTP para adjuntar el Correlation ID a la respuesta."""
    response.headers["X-Correlation-ID"] = g.correlation_id
    return response

def propagate_correlation_id() -> dict:
    """Función para propagar el Correlation ID a servicios downstream."""
    return {"X-Correlation-ID": g.correlation_id}


############################
# Endpoints del inventario #
############################

@app.route('/books', methods=['GET'])
@swag_from('swagger/get_books.yaml')
def get_books():
    logging.info("Llamando al servicio de disponibilidad para obtener todos los libros")
    response = requests.get(f"{disp_service}/disponibilidad", headers=propagate_correlation_id())
    if response.status_code == 200:
        availability_data = response.json()
        for book in books_list:
            availability_info = next((av for av in availability_data if av['bookId'] == book.bookId), None)
            book.available = availability_info['available'] if availability_info else None
        return jsonify([book.dict() for book in books_list])
    else:
        logging.error("No se pudo recuperar la información de disponibilidad de los libros: %s", response.text)
        return jsonify({"error": "No se pudo recuperar la información de disponibilidad"}), response.status_code

@app.route('/books/available', methods=['GET'])
@swag_from('swagger/get_books_available.yaml')
def get_books_available():
    logging.info("Llamando al servicio de disponibilidad para obtener libros disponibles")
    response = requests.get(f"{disp_service}/disponibilidad", headers=propagate_correlation_id())
    if response.status_code == 200:
        availability_data = response.json()
        available_ids = {av['bookId'] for av in availability_data if av['available']}
        available_books = [book for book in books_list if book.bookId in available_ids]
        for book in available_books:
            book.available = True
        logging.info("Libros disponibles encontrados: %d", len(available_books))
        return jsonify([book.dict() for book in available_books])
    else:
        logging.error("No se pudo recuperar la información de disponibilidad de los libros: %s", response.text)
        return jsonify({"error": "No se pudo recuperar la información de disponibilidad"}), response.status_code


@app.route('/books', methods=['POST'])
@swag_from('swagger/add_book.yaml')
def add_book():
    try:
        loaded_data = book_schema.load(request.get_json())
        loaded_data['bookId'] = next_book_id_get()
        new_book = Book(**loaded_data)
        books_list.append(new_book)
        logging.info("Libro con id %d creado", new_book.bookId)
        return book_schema.dump(new_book.dict()), 201
    except ValidationError as err:
        logging.error("Error de validación: %s", err.messages)
        return jsonify(err.messages), 400


@app.route('/books/<int:book_id>', methods=['GET'])
@swag_from('swagger/get_book.yaml')
def get_book(book_id: int):
    book = next((b for b in books_list if b.bookId == book_id), None)
    if book is not None:
        logging.info("Llamando al servicio de disponibilidad para bookId %d", book_id)
        response = requests.get(f"{disp_service}/disponibilidad/{book_id}", headers=propagate_correlation_id())
        if response.status_code == 200:
            availability_info = response.json()
            book.available = availability_info.get('available')
            return book_schema.dump(book.dict()), 200
        logging.error("No se pudo obtener disponibilidad para bookId %d: %s", book_id, response.text)
        return jsonify({"error": "No se pudo obtener la disponibilidad del libro"}), response.status_code
    logging.info("Libro con id %d no encontrado", book_id)
    return jsonify({"message": "Libro no encontrado"}), 404

@app.route('/books/<int:book_id>', methods=['PUT'])
@swag_from('swagger/update_book.yaml')
def update_book(book_id: int):
    book = next((b for b in books_list if b.bookId == book_id), None)
    if not book:
        logging.info("Libro con id %d no encontrado", book_id)
        return jsonify({"message": "Libro no encontrado"}), 404

    try:
        loaded_data = book_schema.load(request.get_json(), partial=True)
        for key, value in loaded_data.items():
            setattr(book, key, value)
        logging.info("Libro con id %d actualizado", book_id)
        return book_schema.dump(book.dict()), 200
    except ValidationError as err:
        logging.error("Error de validación: %s", err.messages)
        return jsonify(err.messages), 400

@app.route('/books/<int:book_id>', methods=['DELETE'])
@swag_from('swagger/delete_book.yaml')
def delete_book(book_id: int):
    book = next((b for b in books_list if b.bookId == book_id), None)
    if book:
        # Remover la disponibilidad asociada al libro antes de eliminarlo del inventario
        response = requests.delete(f"{disp_service}/disponibilidad/{book_id}", headers=propagate_correlation_id())
        if response.status_code != 200:
            logging.error("Error al eliminar la disponibilidad para bookId %d: %s", book_id, response.text)
            return jsonify({"error": "No se pudo eliminar la disponibilidad del libro"}), response.status_code
        logging.info("Disponibilidad para bookId %d eliminada", book_id)
        books_list[:] = [b for b in books_list if b.bookId != book_id]
        logging.info("Libro con id %d eliminado", book_id)
        return jsonify({"message": "Libro eliminado."}), 200
    logging.info("Libro con id %d no encontrado", book_id)
    return jsonify({"message": "Libro no encontrado"}), 404

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)