import pytest
from fastapi.testclient import TestClient

from app.main import app, tasks


@pytest.fixture(autouse=True)
def clear_tasks():
    tasks.clear()
    yield
    tasks.clear()


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Systems Limited Task API"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Complete assignment",
            "description": "Implement CI/CD",
            "completed": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Complete assignment"
    assert response.json()["id"] == 1


def test_list_tasks():
    client.post("/tasks", json={"title": "Task one"})
    client.post("/tasks", json={"title": "Task two"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_task():
    created = client.post("/tasks", json={"title": "Test retrieval"})
    task_id = created.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Test retrieval"


def test_update_task():
    created = client.post("/tasks", json={"title": "Original"})
    task_id = created.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated",
            "description": "Updated description",
            "completed": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["completed"] is True


def test_delete_task():
    created = client.post("/tasks", json={"title": "Delete me"})
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_missing_task_returns_404():
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_missing_task_returns_404():
    response = client.put(
        "/tasks/999",
        json={"title": "Missing task"},
    )
    assert response.status_code == 404


def test_delete_missing_task_returns_404():
    response = client.delete("/tasks/999")
    assert response.status_code == 404


def test_empty_title_is_rejected():
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_title_over_100_characters_is_rejected():
    response = client.post("/tasks", json={"title": "A" * 101})
    assert response.status_code == 422


def test_missing_title_is_rejected():
    response = client.post("/tasks", json={"description": "No title"})
    assert response.status_code == 422


def test_invalid_task_id_returns_422():
    response = client.get("/tasks/not-a-number")
    assert response.status_code == 422