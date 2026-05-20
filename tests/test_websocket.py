def _drain_join(ws):
    join = ws.receive_json()
    assert join["type"] == "join"
    return join


def test_websocket_connects_with_username(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        join = _drain_join(ws)
        assert join["username"] == "alice"
        response = client.get("/rooms/python/users")
        assert response.status_code == 200
        assert response.json()["users"] == ["alice"]


def test_websocket_message_roundtrip(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        _drain_join(ws)
        ws.send_json({"type": "message", "text": "Hi"})
        message = ws.receive_json()
        assert message["type"] == "message"
        assert message["room_id"] == "python"
        assert message["username"] == "alice"
        assert message["text"] == "Hi"


def test_two_clients_same_room_receive_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws1:
        _drain_join(ws1)
        with client.websocket_connect("/ws/rooms/python?username=bob") as ws2:
            _drain_join(ws2)
            _drain_join(ws1)

            ws1.send_json({"type": "message", "text": "Hello"})
            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()

            assert msg1 == msg2
            assert msg1["room_id"] == "python"


def test_different_rooms_do_not_receive_messages(client):
    with client.websocket_connect("/ws/rooms/room1?username=alice") as ws1:
        _drain_join(ws1)
        with client.websocket_connect("/ws/rooms/room2?username=bob") as ws2:
            _drain_join(ws2)

            ws1.send_json({"type": "message", "text": "Room 1"})
            msg1 = ws1.receive_json()
            assert msg1["room_id"] == "room1"

            ws2.send_json({"type": "message", "text": "Room 2"})
            msg2 = ws2.receive_json()
            assert msg2["room_id"] == "room2"


def test_message_too_long_returns_error(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        _drain_join(ws)
        ws.send_json({"type": "message", "text": "a" * 301})
        error = ws.receive_json()
        assert error["type"] == "error"
        assert error["detail"] == "Message is too long"


def test_disconnect_removes_user_from_room(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        _drain_join(ws)
        response = client.get("/rooms/python/users")
        assert response.status_code == 200
        assert response.json()["users"] == ["alice"]

    response = client.get("/rooms/python/users")
    assert response.status_code == 200
    assert response.json()["users"] == []
