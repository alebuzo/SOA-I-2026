# Tarea 4

## Instrucciones

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

## Detalles de los tests

### Suites

- `tests/api/`: Tests funcionales del servicio de préstamos (no mocks, no pact)
- `tests/pact_tests/`: Tests de contrato Pact para los servicios de disponibilidad e inventario (estos sí usan mocks y Pact)
- 15 tests en total, cubriendo tanto funcionalidad como contratos. Todos los tests deben pasar.
- Los tests levantan los servicios necesarios en background (usando `make_server` y threads, en diferentes puertos) para simular un entorno realista.