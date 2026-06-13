import uuid
import logging

from flask import Flask, request, g
from strawberry.flask.views import GraphQLView

from correlation import CorrelationIdFilter
from schema import schema

app = Flask(__name__)

##################
# Correlation ID #
##################

# Crear el handler de logging con el filtro de Correlation ID
handler = logging.StreamHandler()
handler.addFilter(CorrelationIdFilter())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - cid-[%(correlation_id)s] %(message)s",
    handlers=[handler]
)

#########
# Hooks #
#########

@app.before_request
def set_correlation_id() -> None:
    """Hook que se ejecuta antes de cada petición HTTP para establecer el Correlation ID."""
    correlation_id = request.headers.get("X-Correlation-ID")
    g.correlation_id = correlation_id if correlation_id else str(uuid.uuid4())
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


app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema),
)

if __name__ == "__main__":
    app.run(debug=True, port=5002)