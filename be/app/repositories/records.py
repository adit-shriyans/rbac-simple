from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import FinancialRecord
from app.schemas.record import RecordCreate, RecordUpdate


class RecordRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payload: RecordCreate) -> FinancialRecord:
        record = FinancialRecord(**payload.model_dump())
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_by_id(self, record_id: int) -> FinancialRecord | None:
        result = await self.session.execute(
            select(FinancialRecord).where(FinancialRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def update(self, record: FinancialRecord, payload: RecordUpdate) -> FinancialRecord:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def delete(self, record: FinancialRecord) -> None:
        await self.session.delete(record)

    async def list_records(
        self,
        *,
        page: int,
        page_size: int,
        category: str | None = None,
        record_type: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[list[FinancialRecord], int]:
        stmt = select(FinancialRecord)
        count_stmt = select(func.count(FinancialRecord.id))

        if category:
            stmt = stmt.where(FinancialRecord.category.ilike(f"%{category}%"))
            count_stmt = count_stmt.where(FinancialRecord.category.ilike(f"%{category}%"))
        if record_type:
            stmt = stmt.where(FinancialRecord.type == record_type)
            count_stmt = count_stmt.where(FinancialRecord.type == record_type)
        if start_date:
            stmt = stmt.where(FinancialRecord.entry_date >= start_date)
            count_stmt = count_stmt.where(FinancialRecord.entry_date >= start_date)
        if end_date:
            stmt = stmt.where(FinancialRecord.entry_date <= end_date)
            count_stmt = count_stmt.where(FinancialRecord.entry_date <= end_date)

        stmt = stmt.order_by(FinancialRecord.created_at.asc(), FinancialRecord.id.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        records_result = await self.session.execute(stmt)
        count_result = await self.session.execute(count_stmt)
        return list(records_result.scalars().all()), count_result.scalar_one()
