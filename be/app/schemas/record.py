from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.enums import RecordType
from app.schemas.common import ORMModel, PaginationMeta


class RecordBase(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    type: RecordType
    category: str = Field(min_length=2, max_length=100)
    entry_date: date
    notes: str | None = Field(default=None, max_length=1000)
    created_by_user_id: int | None = None

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        return value.strip()


class RecordCreate(RecordBase):
    pass


class RecordUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    type: RecordType | None = None
    category: str | None = Field(default=None, min_length=2, max_length=100)
    entry_date: date | None = None
    notes: str | None = Field(default=None, max_length=1000)
    created_by_user_id: int | None = None


class RecordRead(ORMModel):
    id: int
    amount: Decimal
    type: RecordType
    category: str
    entry_date: date
    notes: str | None
    created_by_user_id: int | None
    created_at: datetime
    updated_at: datetime


class RecordListResponse(BaseModel):
    data: list[RecordRead]
    meta: PaginationMeta
