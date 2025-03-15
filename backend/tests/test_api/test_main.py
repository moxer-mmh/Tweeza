from fastapi import status


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "message" in data
    assert "Welcome to" in data["message"]
    assert "docs" in data


def test_api_docs_accessible(client):
    """Test that API docs are accessible."""
    response = client.get("/api/docs")

    # Redirects are also ok since FastAPI handles the docs page
    assert response.status_code in (
        status.HTTP_200_OK,
        status.HTTP_307_TEMPORARY_REDIRECT,
    )


def test_openapi_schema(client):
    """Test that OpenAPI schema is accessible."""
    response = client.get("/api/openapi.json")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    assert "components" in data
