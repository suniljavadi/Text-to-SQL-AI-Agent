from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_validate_endpoint():
    response = client.post("/api/v1/validate-sql", json={"sql":"SELECT * FROM customers"})
    assert response.status_code == 200
    assert response.json()["valid"]

def test_query_endpoint():
    response = client.post("/api/v1/query", json={"question":"Show the top products by revenue."})
    assert response.status_code == 200
    assert response.json()["validation"]["valid"]
    assert response.json()["rows"]
