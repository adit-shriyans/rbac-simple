from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.enums import UserRole


async def db_session(session: AsyncSession = Depends(get_db_session)) -> AsyncSession:
    return session


def require_roles(*allowed_roles: UserRole) -> Callable:
    async def dependency(x_user_role: str = Header(..., alias="x-user-role")) -> UserRole:
        try:
            role = UserRole(x_user_role.lower())
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid x-user-role header. Use viewer, analyst, or admin.",
            ) from exc

        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role.value}' is not allowed to perform this action.",
            )
        return role

    return dependency
