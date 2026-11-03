"""
Tests for /api/tasks endpoints.
"""
import pytest

from main import tasks


@pytest.fixture(autouse=True)
def clean_tasks():
    """Tasks live in module-level state; isolate each test."""
    tasks.clear()
    yield
    tasks.clear()


def create(client, **overrides):
    body = {"title": "Check stock", "priority": "high", "dueDate": "2025-10-08"}
    body.update(overrides)
    return client.post("/api/tasks", json=body)


class TestTasks:
    def test_list_empty(self, client):
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_task(self, client):
        response = create(client, title="  Check stock  ")
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Check stock"
        assert data["status"] == "pending"
        assert data["priority"] == "high"
        assert data["dueDate"] == "2025-10-08"
        assert data["id"]

    def test_list_newest_first_with_unique_ids(self, client):
        first = create(client, title="first").json()
        second = create(client, title="second").json()
        assert first["id"] != second["id"]
        listed = client.get("/api/tasks").json()
        assert [t["title"] for t in listed] == ["second", "first"]

    @pytest.mark.parametrize("overrides", [
        {"title": "   "},
        {"priority": "urgent"},
        {"dueDate": "not-a-date"},
        {"dueDate": "10/08/2025"},
    ])
    def test_create_invalid_returns_400(self, client, overrides):
        assert create(client, **overrides).status_code == 400
        assert client.get("/api/tasks").json() == []

    def test_create_missing_field_returns_422(self, client):
        assert client.post("/api/tasks", json={"title": "x"}).status_code == 422

    def test_toggle_task(self, client):
        task_id = create(client).json()["id"]
        response = client.patch(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        assert client.patch(f"/api/tasks/{task_id}").json()["status"] == "pending"

    def test_toggle_unknown_returns_404(self, client):
        assert client.patch("/api/tasks/missing").status_code == 404

    def test_delete_task(self, client):
        task_id = create(client).json()["id"]
        assert client.delete(f"/api/tasks/{task_id}").status_code == 204
        assert client.get("/api/tasks").json() == []

    def test_delete_unknown_returns_404(self, client):
        assert client.delete("/api/tasks/missing").status_code == 404
