from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import get_current_user
from ..schemas import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int) -> User:
    return User(id=user_id, role="user")
