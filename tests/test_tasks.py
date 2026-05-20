def test_create_task_success(client):
    payload = {
        "title": "Write tests",
        "description": "Cover core scenarios",
        "status": "todo",
        "priority": 4,
    }
    response = client.post("/tasks", headers={"X-User-Id": "10"}, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["owner_id"] == 10
    assert data["title"] == payload["title"]


def test_create_task_validation_error(client):
    payload = {
        "title": "No",
        "description": None,
        "status": "todo",
        "priority": 3,
    }
    response = client.post("/tasks", headers={"X-User-Id": "1"}, json=payload)
    assert response.status_code == 422


def test_create_task_requires_header(client):
    payload = {
        "title": "Missing header",
        "description": None,
        "status": "todo",
        "priority": 2,
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 401


def test_user_sees_only_own_tasks(client):
    payload = {
        "title": "Owner 1",
        "description": None,
        "status": "todo",
        "priority": 1,
    }
    client.post("/tasks", headers={"X-User-Id": "1"}, json=payload)
    client.post("/tasks", headers={"X-User-Id": "2"}, json={
        "title": "Owner 2",
        "description": None,
        "status": "todo",
        "priority": 1,
    })
    response = client.get("/tasks", headers={"X-User-Id": "1"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["owner_id"] == 1


def test_filter_tasks(client):
    tasks = [
        {
            "title": "Low todo",
            "description": None,
            "status": "todo",
            "priority": 1,
        },
        {
            "title": "High todo",
            "description": None,
            "status": "todo",
            "priority": 4,
        },
        {
            "title": "Done",
            "description": None,
            "status": "done",
            "priority": 5,
        },
    ]
    for payload in tasks:
        client.post("/tasks", headers={"X-User-Id": "5"}, json=payload)

    response = client.get(
        "/tasks",
        headers={"X-User-Id": "5"},
        params={"status": "todo", "min_priority": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "High todo"
    assert data[0]["priority"] == 4


def test_update_status(client):
    payload = {
        "title": "Update",
        "description": None,
        "status": "todo",
        "priority": 2,
    }
    create_response = client.post("/tasks", headers={"X-User-Id": "3"}, json=payload)
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        headers={"X-User-Id": "3"},
        json={"status": "done"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_get_task_not_found_for_other_user(client):
    payload = {
        "title": "Private",
        "description": None,
        "status": "todo",
        "priority": 2,
    }
    create_response = client.post("/tasks", headers={"X-User-Id": "7"}, json=payload)
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "8"})
    assert response.status_code == 404

    missing_response = client.get("/tasks/999", headers={"X-User-Id": "7"})
    assert missing_response.status_code == 404


def test_delete_task(client):
    payload = {
        "title": "Delete",
        "description": None,
        "status": "todo",
        "priority": 2,
    }
    create_response = client.post("/tasks", headers={"X-User-Id": "4"}, json=payload)
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "4"})
    assert response.status_code == 204

    follow_up = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "4"})
    assert follow_up.status_code == 404
