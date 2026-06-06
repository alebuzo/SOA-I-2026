"""
Pruebas de Contrato Dirigidas por el Consumidor (Consumer-Driven Contract Testing)
para la API REST Flask usando pact-python v3.

═══════════════════════════════════════════════════════════════════════════════
¿QUÉ ES CONTRACT TESTING?
═══════════════════════════════════════════════════════════════════════════════

En arquitecturas de microservicios, un CONSUMIDOR es el servicio que hace
peticiones HTTP, y un PROVEEDOR es el servicio que las responde.

El problema: si el proveedor cambia su API sin avisar, el consumidor se rompe.
Los tests de integración clásicos requieren tener ambos servicios corriendo.

Contract Testing resuelve esto en DOS FASES independientes:

  Fase 1 — Pruebas del Consumidor (offline):
    El consumidor define exactamente qué peticiones hará y qué respuestas
    espera. pact-python levanta un servidor mock que simula al proveedor y
    graba esas expectativas en un archivo JSON llamado "contrato" (pact file).
    El proveedor NO necesita estar corriendo.

  Fase 2 — Verificación del Proveedor (online):
    El proveedor real arranca y el verificador de Pact reproduce cada
    interacción del contrato contra él. Si el proveedor responde de forma
    diferente a lo esperado, la verificación falla.

Ventaja clave: cada servicio se puede probar de forma independiente.
El contrato es el "acuerdo" entre ambos equipos.

═══════════════════════════════════════════════════════════════════════════════
PACT-PYTHON V3 VS V2
═══════════════════════════════════════════════════════════════════════════════

  v2 (API antigua, ya no disponible):
    from pact import Consumer, Provider, Like
    pact = Consumer("A").has_pact_with(Provider("B"), host_name="localhost", port=...)
    pact.start_service()   # proceso externo (Ruby standalone)
    pact.stop_service()
    pact.verify()          # comprobación por interacción

  v3 (API actual, basada en Rust FFI):
    from pact import Pact, Verifier, match
    pact = Pact("A", "B")
    with pact.serve(port=...) as mock:   # context manager, sin proceso externo
        mock.write_file(directorio)       # escribe el contrato en JSON
        ...
    verifier = Verifier("B").add_transport(url=...).add_source(archivo).verify()

  Cambios principales:
    - Consumer/Provider              →  Pact("consumidor", "proveedor")
    - Like(x)                        →  match.like(x)
    - start_service()/stop_service() →  with pact.serve() as mock:
    - pact.verify()                  →  assert mock.matched  (o verifier.results)
    - El contrato se escribe con     →  mock.write_file()
"""
import os
import pathlib
import threading
import time
import sys
from importlib import reload
from pathlib import Path

import pytest
import requests
from pact import Pact, Verifier, match
from werkzeug.serving import make_server


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from disponibilidad.app import app as disponibilidad_app
# Nota: inventario_app se importará dinámicamente en la fixture después de configurar DISP_SERVICE

# ── Constantes de configuración ───────────────────────────────────────────────

# Calculamos la raíz del proyecto a partir de la ubicación de este archivo.
# __file__ es tests/pact_tests/test_flask_pact_inventario.py
# .parents[0] = tests/pact_tests/
# .parents[1] = tests/
# .parents[2] = tarea4/   ← raíz del proyecto
_PROJECT_ROOT = pathlib.Path(__file__).parents[2]

# Directorio donde se guardarán los archivos de contrato (.json).
# Usamos ruta absoluta para que tanto mock.write_file() como Verifier.add_source()
# encuentren el archivo independientemente del directorio de trabajo.
PACT_DIR = str(_PROJECT_ROOT / "pacts")

# Puerto donde correrá el servidor mock de Pact durante las pruebas del consumidor.
MOCK_PORT = 5200

# Puerto donde correrá la app Flask DISPONIBILIDAD en la verificación del proveedor.
DISPONIBILIDAD_PORT = 5202

# Puerto donde correrá la app Flask INVENTARIO (proveedor real) en la verificación.
PROVIDER_PORT = 5203

# Ruta completa al archivo de contrato que se generará y luego se leerá.
# El nombre lo determina Pact automáticamente: "<consumidor>-<proveedor>.json"
PACT_FILE = str(_PROJECT_ROOT / "pacts" / "InventarioClient-FlaskInventarioAPI.json")

# ── Creación del objeto Pact ───────────────────────────────────────────────────

# Pact("consumidor", "proveedor") crea el objeto que acumula las interacciones.
# "InventarioClient" es el nombre del servicio consumidor (el cliente HTTP).
# "FlaskInventarioAPI" es el nombre del servicio proveedor (la API Flask).
# Estos nombres se usan para nombrar el archivo JSON del contrato.
pact = Pact("InventarioClient", "FlaskInventarioAPI")


# ── Fixture del mock (módulo completo) ────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def pact_mock():
    """
    Fixture de módulo que:
      1. Registra las cuatro interacciones en el objeto pact.
      2. Levanta el servidor mock de Pact en MOCK_PORT.
      3. Escribe el archivo de contrato ANTES de que los tests corran.
      4. Cede el control a los tests del módulo (consumidor y proveedor).
      5. Al finalizar, el context manager cierra el mock automáticamente.

    scope="module"  → la fixture se crea una vez por módulo (no por test).
    autouse=True    → se aplica automáticamente a todos los tests del módulo
                      sin necesidad de declararla como parámetro.
    """

    # ── Interacción 1: GET /books ───────────────────────────────────
    (
        pact.upon_receiving("GET /books returns a list")
        .given("at least one book exists")        # estado previo del proveedor
        .with_request("GET", "/books")      # método y ruta de la petición
        .will_respond_with(200)                        # código de estado esperado
        .with_body(
            match.each_like(
                {
                    "bookId": match.integer(1),
                    "title": match.string("Example Book"),
                    "available": match.boolean(True),
                    "author": match.string("Author Name"),
                    "isbn": match.string("978-0-00-000000-0"),
                    "edition": match.integer(1),
                    "notes": match.string("Some notes about the book")
                }
            ),
            content_type="application/json",
        )
        .with_header("Content-Type", "application/json")
    )

    # ── Interacción 2: POST /books ──────────────────────────────────
    #
    # El consumidor dice: "cuando envíe POST con body
    # {"title": "New Book", "author": "Author Name", "isbn": "978-0-00-000000-0", "edition": 3}
    # espero un 201 con el objeto creado (bookId, author, available, isbn, edition, notes)."
    #
    # Nota: .with_body() ANTES de .will_respond_with() → aplica al REQUEST.
    #       .with_body() DESPUÉS de .will_respond_with() → aplica al RESPONSE.
    (
        pact.upon_receiving("POST /books creates a new book")
        .given("any state")
        .with_request("POST", "/books")
        .with_body({"title": "New Book", "author": "Author Name", "isbn": "978-0-00-000000-0", "edition": 3},
                   content_type="application/json")  # body del request
        .will_respond_with(201)
        .with_body(                                                          # body del response
            {"bookId": match.integer(1), "title": "New Book", "author": "Author Name", "isbn": "978-0-00-000000-0", "edition": 3},
            content_type="application/json",
        )
        .with_header("Content-Type", "application/json")
    )

    # ── Interacción 3: GET /books/3 ────────────────────────────────
    #
    # Busca un recurso específico por bookId. El bookId=3 en el body es exacto
    # (el cliente verifica que el id devuelto sea el mismo que pidió),
    # pero el resto de fields son flexibles.
    (
        pact.upon_receiving("GET /books/3 returns the book")
        .given("a book with bookId 3 exists")
        .with_request("GET", "/books/3")
        .will_respond_with(200)
        .with_body(
            {"bookId": 3, "title": match.string("Example Book"), "available": match.boolean(True), "author": match.string("Author Name"), "isbn": match.string("978-0-00-000000-0"), "edition": match.integer(1), "notes": match.string("Some notes about the book")},

            content_type="application/json",
        )
        .with_header("Content-Type", "application/json")
    )

    # ── Interacción 4: GET /books/9999 (404) ─────────────────────────
    #
    # match.string("not found") → el mensaje puede ser cualquier string.
    (
        pact.upon_receiving("GET /books/9999 returns 404")
        .given("no book with bookId 9999 exists")
        .with_request("GET", "/books/9999")
        .will_respond_with(404)
        .with_body(
            {"message": match.string("not found")},
            content_type="application/json",
        )
        .with_header("Content-Type", "application/json")
    )

    # ── Arranque del servidor mock ────────────────────────────────────────────
    #
    # pact.serve() es un context manager que:
    #   - Levanta un servidor HTTP en MOCK_PORT que conoce las 4 interacciones.
    #   - Cuando recibe una petición, busca la interacción coincidente y
    #     devuelve la respuesta configurada (sin tocar ninguna base de datos).
    #   - Al salir del bloque "with", detiene el servidor automáticamente.
    #
    # raises=False → si una petición no coincide con ninguna interacción,
    #   devuelve error 500 pero NO lanza excepción en Python. Esto permite
    #   que los tests fallen con assert en vez de con una excepción inesperada.
    with pact.serve(port=MOCK_PORT, raises=False) as mock:

        # ── Escritura del contrato ─────────────────────────────────────────
        #
        # IMPORTANTE: escribimos el archivo ANTES del yield (antes de que
        # corran los tests) porque el TestFlaskProvider que está en este
        # mismo módulo necesita leer el archivo durante su ejecución.
        #
        # Si escribiéramos DESPUÉS del yield, el proveedor intentaría leer
        # un archivo que aún no existe y fallaría con "Invalid source".
        #
        # mock.write_file() serializa las interacciones registradas en el
        # objeto pact a formato JSON según la especificación de Pact.
        # overwrite=True → sobreescribe si ya existe de una ejecución anterior.
        mock.write_file(PACT_DIR, overwrite=True)

        # yield transfiere el control a los tests del módulo.
        # mock es el objeto PactServer que expone mock.url (la URL del mock).
        yield mock

    # Al salir del "with", el servidor mock se detiene.
    # No es necesario código de limpieza adicional.


# ── Fase 1: Pruebas del Consumidor ────────────────────────────────────────────

class TestFlaskConsumer:
    """
    Define el contrato desde el punto de vista del CONSUMIDOR.

    Estos tests verifican que el mock responde exactamente como se configuró,
    y que el cliente (consumidor) puede manejar esas respuestas correctamente.

    Propósito educativo: cada test representa UNA interacción del contrato.
    El mock ya tiene las 4 interacciones registradas; cada test activa una.

    IMPORTANTE: estos tests no prueban la lógica de Flask. Prueban que el
    CONSUMIDOR sabe cómo comunicarse con la API. La app Flask no está corriendo.
    """

    def test_list_books(self, pact_mock):
        # Enviamos GET al mock (no a Flask real). El mock reconoce la petición,
        # la compara con la interacción registrada y devuelve la respuesta
        # configurada (array con un objeto de ejemplo).
        r = requests.get(f"{pact_mock.url}/books")

        # Verificamos que el consumidor recibe lo que espera.
        assert r.status_code == 200
        assert isinstance(r.json(), list)  # el consumidor sabe que es un array

    def test_create_book(self, pact_mock):
        # POST con el body exacto que el consumidor enviará en producción.
        r = requests.post(
            f"{pact_mock.url}/books",
            json={"title": "New Book", "author": "Author Name", "isbn": "978-0-00-000000-0", "edition": 3},
        )
        assert r.status_code == 201
        assert r.json()["title"] == "New Book"  # el título devuelto debe coincidir
        assert r.json()["author"] == "Author Name"  # el autor devuelto debe coincidir
        assert r.json()["isbn"] == "978-0-00-000000-0"  # el ISBN devuelto debe coincidir
        assert r.json()["edition"] == 3  # la edición devuelta debe coincidir

    def test_get_book_by_id(self, pact_mock):
        r = requests.get(f"{pact_mock.url}/books/3")
        assert r.status_code == 200
        # El consumidor verifica que el id devuelto es el que pidió.
        assert r.json()["bookId"] == 3

    def test_get_book_not_found(self, pact_mock):
        r = requests.get(f"{pact_mock.url}/books/9999")
        # El consumidor debe poder manejar un 404.
        assert r.status_code == 404


# ── Fase 2: Verificación del Proveedor ───────────────────────────────────────

@pytest.fixture(scope="class")
def flask_provider_url():
    """
    Fixture que levanta DOS apps Flask para las pruebas del proveedor:
      1. DISPONIBILIDAD (el servicio que inventario necesita llamar).
      2. INVENTARIO (el proveedor real siendo verificado contra el contrato).

    El fixture:
      - Inicia disponibilidad en DISPONIBILIDAD_PORT.
      - Establece DISP_SERVICE como variable de entorno para que inventario sepa
        dónde encontrar disponibilidad.
      - Inicia inventario (proveedor) en PROVIDER_PORT.
      - Entrega la URL de inventario al test.
      - Detiene ambos servidores en teardown.
    """

    # ── Paso 1: Iniciar el servicio DISPONIBILIDAD ────────────────────────────
    disp_server = make_server("localhost", DISPONIBILIDAD_PORT, disponibilidad_app)
    disp_thread = threading.Thread(target=disp_server.serve_forever, daemon=True)
    disp_thread.start()
    time.sleep(0.2)  # Pausa para que disponibilidad esté listo

    # ── Paso 2: Configurar variable de entorno DISP_SERVICE ────────────────────
    # inventario.app carga esta variable en app.py: disp_service = os.getenv("DISP_SERVICE")
    disponibilidad_url = f"http://localhost:{DISPONIBILIDAD_PORT}"
    os.environ["DISP_SERVICE"] = disponibilidad_url
    print(f"DEBUG: DISP_SERVICE set to {disponibilidad_url}")

    # ── Paso 3: Importar/Recargar inventario_app para que lea DISP_SERVICE ──────
    # Importamos aquí (después de configurar env vars) para que la app lea la variable.
    # Import and reload inventario.app so it reads the updated DISP_SERVICE env var
    import importlib
    import inventario.app as inv_module
    importlib.reload(inv_module)
    inventario_app = inv_module.app

    provider_server = make_server("localhost", PROVIDER_PORT, inventario_app)
    provider_thread = threading.Thread(target=provider_server.serve_forever, daemon=True)
    provider_thread.start()
    time.sleep(0.2)  # Pausa para que inventario esté listo

    # Debug: verificar que ambos servidores responden
    try:
        r_disp = requests.get(f"{disponibilidad_url}/disponibilidad/")
        print(f"DEBUG: Disponibilidad responds with {r_disp.status_code}")
    except Exception as e:
        print(f"DEBUG: Disponibilidad error: {e}")

    try:
        r_inv = requests.get(f"http://localhost:{PROVIDER_PORT}/books")
        print(f"DEBUG: Inventario responds with {r_inv.status_code}")
    except Exception as e:
        print(f"DEBUG: Inventario error: {e}")

    # Entregamos la URL de inventario (proveedor) al test
    yield f"http://localhost:{PROVIDER_PORT}"

    # ── Teardown: detener ambos servidores ────────────────────────────────────
    provider_server.shutdown()
    disp_server.shutdown()

    # Limpiar variable de entorno
    if "DISP_SERVICE" in os.environ:
        del os.environ["DISP_SERVICE"]


class TestFlaskProvider:
    """
    Verifica que la app Flask REAL cumple el contrato generado por el consumidor.

    El verificador de Pact lee el archivo JSON del contrato y reproduce cada
    interacción contra el proveedor real. Si Flask devuelve algo diferente a
    lo especificado en el contrato (código de estado, estructura del body,
    headers), la verificación falla.

    Esto garantiza que cualquier cambio en la API Flask que rompa el contrato
    sea detectado ANTES de desplegarse a producción.
    """

    def test_provider_honours_pact(self, flask_provider_url):
        # Verifier("FlaskInventarioAPI") crea el verificador para el proveedor.
        # El nombre debe coincidir exactamente con el nombre del proveedor
        # usado en Pact("InventarioClient", "FlaskInventarioAPI").
        #
        # .add_transport(url=...) le indica a qué URL hacer las peticiones.
        # La URL debe usar el mismo host que el Verifier (por defecto "localhost").
        #
        # .add_source(PACT_FILE) le indica qué contrato verificar.
        # Acepta ruta a un archivo .json o a un directorio con múltiples contratos.
        #
        # .verify() ejecuta la verificación: reproduce cada interacción del
        # contrato contra el proveedor real y compara las respuestas.
        verifier = (
            Verifier("FlaskInventarioAPI")
            .add_transport(url=flask_provider_url)
            .add_source(PACT_FILE)
        )
        verifier.verify()

        # verifier.results es un dict con el resumen de la verificación.
        # Estructura típica:
        #   {
        #     "summary": {
        #       "testCount": 4,
        #       "failureCount": 0,
        #       "pendingCount": 0
        #     },
        #     "testResults": [...],
        #     ...
        #   }
        results = verifier.results
        failures = results.get("summary", {}).get("failureCount", 0)

        # Si failureCount > 0, al menos una interacción del contrato no fue
        # satisfecha por el proveedor. El mensaje de error incluye el dict
        # completo para facilitar el diagnóstico.
        assert failures == 0, f"El proveedor Flask Inventario no satisfizo {failures} interacción(es): {results}"
