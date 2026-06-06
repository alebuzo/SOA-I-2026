# Tarea 4

## Instrucciones

### Opción 1: ejecute los tests manualmente

1. Desde el directorio `tarea4/` cree un virtual environment e instale las dependencias:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install -r requirements.txt
   ```

2. Desde el directorio `tarea4/` ejecute los tests:
   ```bash
   pytest tests/
   ```

### Opción 2: levante un contenedor de Docker

1. Desde el directorio `tarea4/` construya y levante un container de Docker, el entrypoint del contenedor ya corre los tests:

```bash
docker build -t tarea4 . && docker run tarea4
```

## Resultados

En su terminal observará:

```bash
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
rootdir: /tarea4/tests
configfile: pytest.ini
plugins: Faker-40.19.1
collected 15 items

tests/api/test_prestamos_api.py .....                                    [ 33%]
tests/pact_tests/test_flask_pact_disponibilidad.py .....                 [ 66%]
tests/pact_tests/test_flask_pact_inventario.py .....                     [100%]

============================== 15 passed in 8.91s ==============================
```

## Detalles de los tests

### Suites

- `tests/api/`: Tests funcionales del servicio de préstamos (no mocks, no pact)
- `tests/pact_tests/`: Tests de contrato Pact para los servicios de disponibilidad e inventario (estos sí usan mocks y Pact)
- 15 tests en total, cubriendo tanto funcionalidad como contratos. Todos los tests deben pasar.
- Los tests levantan los servicios necesarios en background (usando `make_server` y threads, en diferentes puertos) para simular un entorno realista.