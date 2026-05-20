from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..dependencies import get_storage, require_admin
from ..storage import InMemoryTaskStorage

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats")
def get_stats(storage: InMemoryTaskStorage = Depends(get_storage)) -> dict:
    return storage.stats()


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, storage: InMemoryTaskStorage = Depends(get_storage)) -> Response:
    if not storage.get_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    storage.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
