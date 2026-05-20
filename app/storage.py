from __future__ import annotations

from threading import Lock
from typing import Any, Dict, List, Optional

from .schemas import TaskCreate, TaskStatus


class InMemoryTaskStorage:
    def __init__(self) -> None:
        self._lock = Lock()
        self._tasks: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def reset(self) -> None:
        with self._lock:
            self._tasks.clear()
            self._next_id = 1

    def create_task(self, payload: TaskCreate, owner_id: int) -> Dict[str, Any]:
        with self._lock:
            task_id = self._next_id
            self._next_id += 1
            task_data = self._model_dump(payload)
            task_data.update({"id": task_id, "owner_id": owner_id})
            self._tasks[task_id] = task_data
            return dict(task_data)

    def list_tasks(
        self,
        owner_id: int,
        status: Optional[TaskStatus] = None,
        min_priority: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        tasks = [task for task in self._tasks.values() if task["owner_id"] == owner_id]
        if status is not None:
            status_value = status.value if isinstance(status, TaskStatus) else str(status)
            tasks = [task for task in tasks if task["status"] == status_value]
        if min_priority is not None:
            tasks = [task for task in tasks if task["priority"] >= min_priority]
        return [dict(task) for task in tasks]

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        task = self._tasks.get(task_id)
        return dict(task) if task is not None else None

    def update_status(self, task_id: int, status: TaskStatus) -> Optional[Dict[str, Any]]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        status_value = status.value if isinstance(status, TaskStatus) else str(status)
        task["status"] = status_value
        return dict(task)

    def delete_task(self, task_id: int) -> bool:
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

    def stats(self) -> Dict[str, Any]:
        by_status = {status.value: 0 for status in TaskStatus}
        for task in self._tasks.values():
            status_value = task.get("status")
            if status_value in by_status:
                by_status[status_value] += 1
        return {"total_tasks": len(self._tasks), "by_status": by_status}

    @staticmethod
    def _model_dump(model: Any) -> Dict[str, Any]:
        if hasattr(model, "model_dump"):
            return model.model_dump()
        return model.dict()


storage = InMemoryTaskStorage()
