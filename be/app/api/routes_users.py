from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session, require_roles
from app.models.enums import UserRole
from app.repositories.users import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=list[UserRead],
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def list_users(session: AsyncSession = Depends(db_session)):
    repository = UserRepository(session)
    return await repository.list_users()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(db_session)):
    repository = UserRepository(session)
    existing_user = await repository.get_by_email(payload.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="A user with this email already exists.")

    user = await repository.create(payload)
    await session.commit()
    return user


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def update_user(
    user_id: int, payload: UserUpdate, session: AsyncSession = Depends(db_session)
):
    repository = UserRepository(session)
    user = await repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if payload.email:
        existing_user = await repository.get_by_email(payload.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="A user with this email already exists.")

    updated_user = await repository.update(user, payload)
    await session.commit()
    return updated_user
