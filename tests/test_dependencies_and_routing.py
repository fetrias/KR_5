def _create_task(client, user_id, status="todo", priority=1):
    payload = {
        "title": f"Task {user_id}",
        "description": None,
        "status": status,
        "priority": priority,
    }
    response = client.post("/tasks", headers={"X-User-Id": str(user_id)}, json=payload)
    assert response.status_code == 201
    return response.json()


def test_users_me_returns_current_user(client):
    response = client.get(
        "/users/me", headers={"X-User-Id": "10", "X-User-Role": "user"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": 10, "role": "user"}


def test_users_me_requires_header(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_non_admin_forbidden_for_admin_stats(client):
    response = client.get(
        "/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "user"}
    )
    assert response.status_code == 403


def test_admin_gets_stats(client):
    _create_task(client, 1, status="todo")
    _create_task(client, 2, status="in_progress")
    _create_task(client, 3, status="done")
    _create_task(client, 4, status="done")

    response = client.get(
        "/admin/stats", headers={"X-User-Id": "99", "X-User-Role": "admin"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 4
    assert data["by_status"]["todo"] == 1
    assert data["by_status"]["in_progress"] == 1
    assert data["by_status"]["done"] == 2


def test_user_cannot_delete_foreign_task(client):
    task = _create_task(client, 1)
    response = client.delete(f"/tasks/{task['id']}", headers={"X-User-Id": "2"})
    assert response.status_code == 404


def test_admin_can_delete_any_task(client):
    task = _create_task(client, 1)
    response = client.delete(
        f"/admin/tasks/{task['id']}",
        headers={"X-User-Id": "99", "X-User-Role": "admin"},
    )
    assert response.status_code == 204

    follow_up = client.get(f"/tasks/{task['id']}", headers={"X-User-Id": "1"})
    assert follow_up.status_code == 404


def test_swagger_tags_grouped(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    found_tags = set()
    for path_item in openapi.get("paths", {}).values():
        for method in path_item.values():
            for tag in method.get("tags", []):
                found_tags.add(tag)
    assert {"tasks", "users", "admin"}.issubset(found_tags)
