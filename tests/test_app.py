import pytest

import app as taskflow


@pytest.fixture(autouse=True)
def clear_store():
    taskflow.tasks.clear()
    yield
    taskflow.tasks.clear()


@pytest.fixture()
def client():
    taskflow.app.config.update(TESTING=True)
    return taskflow.app.test_client()


def create_task(client, title="Finish the report today"):
    response = client.post("/api/tasks", json={"title": title})
    assert response.status_code == 201
    return response.get_json()["task"]


def test_health_reports_in_memory_storage(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "storage": "in-memory"}


def test_create_task_assigns_deterministic_priority(client):
    task = create_task(client)
    assert task["priority"] == "high"
    assert task["completed"] is False


def test_create_rejects_non_string_title(client):
    response = client.post("/api/tasks", json={"title": 123})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Task title must be a string."


def test_create_rejects_non_object_json(client):
    response = client.post("/api/tasks", json=["not", "an", "object"])
    assert response.status_code == 400


def test_patch_rejects_string_false_instead_of_coercing_it(client):
    task = create_task(client)
    response = client.patch(
        f"/api/tasks/{task['id']}", json={"completed": "false"}
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "completed must be a JSON boolean."


def test_patch_accepts_boolean(client):
    task = create_task(client)
    response = client.patch(
        f"/api/tasks/{task['id']}", json={"completed": True}
    )
    assert response.status_code == 200
    assert response.get_json()["task"]["completed"] is True


def test_patch_without_body_toggles_completion(client):
    task = create_task(client)
    response = client.patch(f"/api/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.get_json()["task"]["completed"] is True


def test_delete_task(client):
    task = create_task(client)
    response = client.delete(f"/api/tasks/{task['id']}")
    assert response.status_code == 200
    assert client.get("/api/tasks").get_json()["tasks"] == []
