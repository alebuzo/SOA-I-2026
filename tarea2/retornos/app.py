from flask import Flask, jsonify, request
from faker import Faker
from flasgger import Swagger, swag_from
from marshmallow import Schema, fields, ValidationError
from typing import Optional

app = Flask(__name__)

# Definición del esquema de validación para un retorno
class RetornoSchema(Schema):
    returnId = fields.Int(required=True, metadata={"example": 1674})
    loanId = fields.Int(required=True, metadata={"example": 42})
    user = fields.Str(required=True, metadata={"example": "Carla Manchado"})