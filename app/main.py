import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .routers import admin, tasks, users
from .schemas import HealthResponse
from .rooms import room_manager

app = FastAPI(title="Tasks API")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health", response_model=HealthResponse)
def health() -> dict:
	env = os.getenv("APP_ENV", "local")
	return {"status": "ok", "env": env}


@app.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str) -> dict:
	users = await room_manager.get_users(room_id)
	return {"room_id": room_id, "users": users}


@app.websocket("/ws/rooms/{room_id}")
async def websocket_rooms(room_id: str, websocket: WebSocket) -> None:
	username = (websocket.query_params.get("username") or "").strip()
	if not username:
		await websocket.close(code=1008)
		return

	await room_manager.connect(room_id, username, websocket)
	await room_manager.broadcast(
		room_id,
		{"type": "join", "room_id": room_id, "username": username},
	)

	try:
		while True:
			data = await websocket.receive_json()
			if data.get("type") != "message":
				continue
			text = data.get("text", "")
			if not isinstance(text, str):
				text = str(text)
			if len(text) > 300:
				await websocket.send_json(
					{"type": "error", "detail": "Message is too long"}
				)
				continue
			await room_manager.broadcast(
				room_id,
				{
					"type": "message",
					"room_id": room_id,
					"username": username,
					"text": text,
				},
			)
	except WebSocketDisconnect:
		await room_manager.disconnect(room_id, username, websocket)
