from __future__ import annotations

import asyncio
from typing import Dict, List, Set

from fastapi import WebSocket


class RoomManager:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._rooms: Dict[str, Dict[str, Set[WebSocket]]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            users = self._rooms.setdefault(room_id, {})
            sockets = users.setdefault(username, set())
            sockets.add(websocket)

    async def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        async with self._lock:
            users = self._rooms.get(room_id)
            if not users:
                return
            sockets = users.get(username)
            if sockets and websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    users.pop(username, None)
            if not users:
                self._rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, payload: dict) -> None:
        async with self._lock:
            sockets: List[WebSocket] = []
            for user_sockets in self._rooms.get(room_id, {}).values():
                sockets.extend(list(user_sockets))
        for websocket in sockets:
            try:
                await websocket.send_json(payload)
            except Exception:
                continue

    async def get_users(self, room_id: str) -> List[str]:
        async with self._lock:
            return list(self._rooms.get(room_id, {}).keys())


room_manager = RoomManager()
