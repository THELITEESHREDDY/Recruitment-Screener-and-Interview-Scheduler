import pytest

from fastapi.testclient import TestClient

from backend.main import app
from backend.db.connection import get_db

@pytest.fixture
def client(db_setup):
    """
    Create a FastAPI test client using
    the isolated SQLite test database.
    """

    def override_get_db():
        yield db_setup

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

def test_create_job(client):
    response = client.post(
        "/jobs",
        json={
            "job_description": "Hiring a Python Backend Developer"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["job_description"] == "Hiring a Python Backend Developer"

def test_get_all_jobs(client):
    client.post(
        "/jobs",
        json={"job_description": "Python Developer"}
    )

    client.post(
        "/jobs",
        json={"job_description": "AI Engineer"}
    )

    response = client.get("/jobs")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

def test_get_job_by_id(client):
    create_response = client.post(
        "/jobs",
        json={"job_description": "Backend Engineer"}
    )

    assert create_response.status_code == 201

    job_id = create_response.json()["id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["id"] == job_id
    assert response.json()["job_description"] == "Backend Engineer"

def test_get_nonexistent_job(client):
    response = client.get("/jobs/nonexistent-job-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"