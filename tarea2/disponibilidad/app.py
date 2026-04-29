from faker import Faker
from datetime import datetime
from flasgger import Swagger, swag_from
from flask import Flask, request, jsonify
from marshmallow import Schema, fields, ValidationError
from model import Disponibilidad, disponibilidad_list, next_disponibilidad_id_get
from schema import disponibilidad_schema


opciones = ['LOANED', 'RESTORATION', 'HIGH_VALUE', 'UNIQUE_COPY', 'LOST', 'OTHER']

app = Flask(__name__)

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
        "title": "API de Disponibilidad",
        "version": "1.0",
        "description": "Un API para manejar la disponibilidad de libros en la biblioteca.",
        "termsOfService": "https://catoftheday.com/",
        "contact": {
            "responsibleOrganization": "Cat of the Day",
            "responsibleDeveloper": "Alexa Buzo",
            "email": "al.cbuzo@gmail.com",
            "url": "https://catoftheday.com/",
        },
    },
    "definitions": {
        "Disponibilidad": marshmallow_to_swagger(disponibilidad_schema),
    }
}

swagger = Swagger(app, template=swagger_template)

##################################
# Llenar base de datos con Faker #
##################################

faker = Faker()
for i in range(1, 20):
    disponibilidad_list.append(Disponibilidad(
        disponibilidadId=faker.random_int(min=1, max=20),
        bookId=i,
        available=faker.boolean(),
        reason=faker.random_element(elements=opciones),
        lastUpdated=faker.date_time_this_year()
    ))

############################
# Endpoints del inventario #
############################


@app.route('/disponibilidad/<int:book_id>', methods=['POST'])
@swag_from('swagger/add_disponibilidad.yml')
def add_disponibilidad(book_id: int):
    try:
        loaded_data = disponibilidad_schema.load(request.get_json())
        new_disponibilidad = Disponibilidad(**loaded_data)
        new_disponibilidad.disponibilidadId = next_disponibilidad_id_get()
        disponibilidad_list.append(new_disponibilidad)
        return disponibilidad_schema.dump(new_disponibilidad), 201
    except ValidationError as err:
        return jsonify(err.messages), 400


@app.route('/disponibilidad/<int:book_id>', methods=['GET'])
@swag_from('swagger/get_disponibilidad.yml')
def get_disponibilidad(book_id: int):
    for disponibilidad in disponibilidad_list:
        if disponibilidad.bookId == book_id:
            return disponibilidad_schema.dump(disponibilidad), 200
    return jsonify({"message": "Disponibilidad no encontrada para el bookId dado."}), 404


@app.route('/disponibilidad/', methods=['GET'])
@swag_from('swagger/get_all_disponibilidad.yml')
def get_all_disponibilidad():
    return jsonify([disponibilidad_schema.dump(d) for d in disponibilidad_list]), 200


@app.route('/disponibilidad/<int:book_id>', methods=['PUT'])
@swag_from('swagger/update_disponibilidad.yml')
def update_disponibilidad(book_id: int):
    try:
        # Use partial=True to allow partial updates
        updated_data = disponibilidad_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

     # Buscamos el objeto una sola vez
    disponibilidad = next((d for d in disponibilidad_list if d.bookId == book_id), None)
    if disponibilidad:
        for key, value in updated_data.items():
            if hasattr(disponibilidad, key):
                setattr(disponibilidad, key, value)

        disponibilidad.lastUpdated = datetime.now()
        return disponibilidad_schema.dump(disponibilidad), 200
    return jsonify({"message": "Disponibilidad no encontrada para el bookId dado."}), 404


@app.route('/disponibilidad/<int:book_id>', methods=['DELETE'])
@swag_from('swagger/delete_disponibilidad.yml')
def delete_disponibilidad(book_id: int):
    disponibilidad = next((d for d in disponibilidad_list if d.bookId == book_id), None)
    if disponibilidad:
        disponibilidad_list.remove(disponibilidad)
        return jsonify({"message": "Disponibilidad eliminada."}), 200
    return jsonify({"message": "Disponibilidad no encontrada para el bookId dado."}), 404


# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)