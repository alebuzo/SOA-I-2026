import pytest
import os
import sys
import threading
import time
from werkzeug.serving import make_server

# Get the absolute path of the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(current_dir))

# Port configuration - avoiding 5200, 5201, 5203
DISPONIBILIDAD_PORT = 5210
INVENTARIO_PORT = 5211
PRESTAMOS_PORT = 5212

from disponibilidad.app import app as disponibilidad_app

@pytest.fixture(scope="function")
def graphql_client():
    """
    Fixture that starts disponibilidad, inventario, and prestamos services,
    then provides a GraphQL test client for prestamos.
    
    Services are started in dependency order:
      1. disponibilidad (no dependencies)
      2. inventario (depends on DISP_SERVICE)
      3. prestamos (depends on DISP_SERVICE and/or INVENTARIO_SERVICE)
    """
    
    # Step 1: Start disponibilidad on port 5210 (no dependencies)
    disp_server = make_server("localhost", DISPONIBILIDAD_PORT, disponibilidad_app)
    disp_thread = threading.Thread(target=disp_server.serve_forever, daemon=True)
    disp_thread.start()
    time.sleep(0.2)
    
    # Step 2: Configure and start inventario on port 5211
    # Set DISP_SERVICE BEFORE importing inventario.app (so it reads the env var)
    disponibilidad_url = f"http://localhost:{DISPONIBILIDAD_PORT}"
    os.environ["DISP_SERVICE"] = disponibilidad_url
    # Ensure tests don't attempt to connect to RabbitMQ (avoid None host)
    # Skipping RabbitMQ in functional testing
    os.environ.setdefault("RABBITMQ_HOST", "")
    
    import inventario.app as inv_module
    inventario_app = inv_module.app
    
    inv_server = make_server("localhost", INVENTARIO_PORT, inventario_app)
    inv_thread = threading.Thread(target=inv_server.serve_forever, daemon=True)
    inv_thread.start()
    time.sleep(0.2)
    
    # Step 3: Configure and start prestamos on port 5212
    # Set service URLs before importing prestamos.app
    os.environ["INVENTARIO_SERVICE"] = f"http://localhost:{INVENTARIO_PORT}"
    # DISP_SERVICE already set above, but ensure it's correct
    os.environ["DISP_SERVICE"] = disponibilidad_url
    
    import prestamos.app as prest_module
    prestamos_app = prest_module.app
    
    prestamos_app.config["TESTING"] = True
    with prestamos_app.test_client() as client:
        yield client
    
    # Cleanup: stop all servers
    disp_server.shutdown()
    inv_server.shutdown()
    
    # Clean up environment variables
    if "DISP_SERVICE" in os.environ:
        del os.environ["DISP_SERVICE"]
    if "INVENTARIO_SERVICE" in os.environ:
        del os.environ["INVENTARIO_SERVICE"]
