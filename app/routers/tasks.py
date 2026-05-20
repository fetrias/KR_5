from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from ..dependencies import get_current_user, get_storage
from ..schemas import TaskCreate, TaskOut, TaskStatus, TaskStatusUpdate, User
from ..storage import InMemoryTaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _ensure_owner(task: Optional[dict], user_id: int) -> dict:
    if task is None or task.get("owner_id") != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> dict:
    return storage.create_task(payload, current_user.id)


@router.get("", response_model=List[TaskOut])
def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    min_priority: Optional[int] = Query(None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> List[dict]:
    return storage.list_tasks(current_user.id, status=status, min_priority=min_priority)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> dict:
    task = storage.get_task(task_id)
    return _ensure_owner(task, current_user.id)


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> dict:
    task = _ensure_owner(storage.get_task(task_id), current_user.id)
    updated = storage.update_status(task["id"], payload.status)
    return updated or task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: InMemoryTaskStorage = Depends(get_storage),
) -> Response:
    _ensure_owner(storage.get_task(task_id), current_user.id)
    storage.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
