"""
Pruebas funcionales para la API de préstamos.
"""

import pytest

def gql(client, query: str, variables: dict = None) -> tuple[dict | None, list | None]:
    """Envía una petición GraphQL y retorna (data, errors)."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = client.post("/graphql", json=payload)
    body = resp.get_json()
    return body.get("data"), body.get("errors")

# Fixtures

@pytest.fixture
def prestamo(graphql_client):
    "Crea un préstamo para usar en pruebas."
    data, _ = gql(graphql_client, """
        mutation AddPrestamo($user: String!, $books: [String!]!, $dueDate: Date!) {
        addPrestamo(input: {
            user: $user
            books: $books
            loanDueDate: $dueDate
        }) {
            loanId
            user
            books
            loanDueDate
            status
        }
        }
        """, variables={"user": "Alice", "books": ["3"], "dueDate": "2023-12-31"})
    return data["addPrestamo"]

@pytest.fixture
def prestamo_eliminar(graphql_client, prestamoId):
    "Elimina un préstamo para usar en pruebas."
    data, _ =gql(graphql_client, """
        mutation DeletePrestamo($id: Int!) { deletePrestamo(id: $id) }
                 """, variables={"id": prestamoId})
    return data["deletePrestamo"]

# Pruebas de queries #

class TestPrestamosQueries:

    def test_prestamos_query(self, graphql_client, prestamo):
        "Consulta la lista de préstamos y verifica que el nuevo préstamo esté presente."
        data, errors = gql(graphql_client, """
            query { prestamos { loanId user books loanDueDate status } }
        """)
        assert errors is None
        assert any(p["loanId"] == prestamo["loanId"] for p in data["prestamos"])

    def test_prestamo_query(self, graphql_client, prestamo):
        "Consulta un préstamo por ID y verifica sus campos."
        data, errors = gql(graphql_client, """
            query GetPrestamo($id: Int!) { prestamo(loanId: $id) { loanId user books loanDueDate status } }
        """, variables={"id": prestamo["loanId"]})
        assert errors is None
        p = data["prestamo"]
        assert p["loanId"] == prestamo["loanId"]
        assert p["user"] == prestamo["user"]
        assert p["books"] == prestamo["books"]
        assert p["loanDueDate"] == prestamo["loanDueDate"]
        assert p["status"] == prestamo["status"]

    def test_prestamo_query_not_found(self, graphql_client):
        "Consulta un préstamo con ID inexistente y verifica que no se encuentre."
        data, errors = gql(graphql_client, """
            query GetPrestamo($id: Int!) { prestamo(loanId: $id) { loanId } }
        """, variables={"id": 9999})
        assert errors is None
        assert data["prestamo"] is None

# Pruebas de mutations #

class TestPrestamosMutations:
    
    def test_add_prestamo(self, graphql_client):
        "Agrega un préstamo y verifica que se cree correctamente."
        data, errors = gql(graphql_client, """
            mutation AddPrestamo($user: String!, $books: [String!]!, $dueDate: Date!) {
            addPrestamo(input: {
                user: $user
                books: $books
                loanDueDate: $dueDate
            }) {
                loanId
                user
                books
                loanDueDate
                status
            }
            }
        """, variables={"user": "Bob", "books": ["1"], "dueDate": "2024-01-15"})
        assert errors is None
        p = data["addPrestamo"]
        assert p["loanId"] is not None
        assert p["user"] == "Bob"
        assert p["books"] == ["1"]
        assert p["loanDueDate"] == "2024-01-15"
        assert p["status"] == "ACTIVE"

    def test_delete_prestamo(self, graphql_client):
        "Elimina un préstamo y verifica que se elimine correctamente."
        data, error =gql(graphql_client, """
        mutation DeletePrestamo($id: Int!) { deletePrestamo(loanId: $id) }
                 """, variables={"id": 1})
        assert error is None
        assert data["deletePrestamo"] == True

        # Verificar que el préstamo ya no exista
        data, errors = gql(graphql_client, """
            query GetPrestamo($id: Int!) { prestamo(loanId: $id) { loanId } }
        """, variables={"id": 1})
        assert errors is None
        assert data["prestamo"] is None