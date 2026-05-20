from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from .schemas import User
from .storage import InMemoryTaskStorage, storage


def get_current_user(
    x_user_id: str | None = Header(None, alias="X-User-Id"),
    x_user_role: str | None = Header("user", alias="X-User-Role"),
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    role = (x_user_role or "user").strip().lower()
    if not role:
        role = "user"
    return User(id=user_id, role=role)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user


def get_storage() -> InMemoryTaskStorage:
    return storage
