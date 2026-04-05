from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session, require_roles
from app.models.enums import UserRole
from app.repositories.records import RecordRepository
from app.schemas.common import APIMessage, PaginationMeta
from app.schemas.record import RecordCreate, RecordListResponse, RecordRead, RecordUpdate

router = APIRouter(prefix="/records", tags=["records"])


@router.get(
    "",
    response_model=RecordListResponse,
    dependencies=[Depends(require_roles(UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN))],
)
async def list_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    category: str | None = None,
    type: str | None = Query(default=None, pattern="^(income|expense)$"),
    start_date: date | None = None,
    end_date: date | None = None,
    session: AsyncSession = Depends(db_session),
):
    repository = RecordRepository(session)
    records, total = await repository.list_records(
        page=page,
        page_size=page_size,
        category=category,
        record_type=type,
        start_date=start_date,
        end_date=end_date,
    )
    return RecordListResponse(
        data=[RecordRead.model_validate(record) for record in records],
        meta=PaginationMeta(total=total, page=page, page_size=page_size),
    )


@router.post(
    "",
    response_model=RecordRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def create_record(
    payload: RecordCreate,
    session: AsyncSession = Depends(db_session),
):
    repository = RecordRepository(session)
    record = await repository.create(payload)
    await session.commit()
    return record


@router.patch(
    "/{record_id}",
    response_model=RecordRead,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def update_record(
    record_id: int,
    payload: RecordUpdate,
    session: AsyncSession = Depends(db_session),
):
    repository = RecordRepository(session)
    record = await repository.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Financial record not found.")

    updated_record = await repository.update(record, payload)
    await session.commit()
    return updated_record


@router.delete(
    "/{record_id}",
    response_model=APIMessage,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def delete_record(
    record_id: int,
    session: AsyncSession = Depends(db_session),
):
    repository = RecordRepository(session)
    record = await repository.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Financial record not found.")

    await repository.delete(record)
    await session.commit()
    return APIMessage(message="Financial record deleted successfully.")
