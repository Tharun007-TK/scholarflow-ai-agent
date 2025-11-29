from fastapi.testclient import TestClient
from api import app
import os
import pytest

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ScholarFlow AI API is running"}

def test_dashboard_empty():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.json()["status"] == "empty"

# We skip the upload test in CI/automated environment if no PDF is available,
# but we can mock it or just test the root endpoint for now to ensure server starts.
