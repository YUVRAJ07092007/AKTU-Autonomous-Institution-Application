from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_ok() -> None:
    response = client.get("/api/health", headers={"x-user-id": "test", "x-roles": "TESTER"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "aktu-autonomy-portal"}

