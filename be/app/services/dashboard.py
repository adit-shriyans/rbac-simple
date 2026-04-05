from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RecordType
from app.models.financial_record import FinancialRecord
from app.schemas.summary import (
    CategoryTotal,
    DashboardSummary,
    RecentActivityItem,
    TrendPoint,
)


ZERO = Decimal("0.00")


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_summary(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> DashboardSummary:
        base_filters = []
        if start_date:
            base_filters.append(FinancialRecord.entry_date >= start_date)
        if end_date:
            base_filters.append(FinancialRecord.entry_date <= end_date)

        totals_stmt = select(
            func.coalesce(
                func.sum(
                    case((FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount), else_=0)
                ),
                0,
            ).label("total_income"),
            func.coalesce(
                func.sum(
                    case((FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount), else_=0)
                ),
                0,
            ).label("total_expense"),
        ).where(*base_filters)
        totals_result = (await self.session.execute(totals_stmt)).one()

        category_stmt = (
            select(
                FinancialRecord.category,
                func.coalesce(func.sum(FinancialRecord.amount), 0).label("total"),
            )
            .where(*base_filters)
            .group_by(FinancialRecord.category)
            .order_by(func.sum(FinancialRecord.amount).desc())
        )
        category_rows = (await self.session.execute(category_stmt)).all()

        recent_stmt = (
            select(FinancialRecord)
            .where(*base_filters)
            .order_by(FinancialRecord.created_at.asc())
            .limit(5)
        )
        recent_records = (await self.session.execute(recent_stmt)).scalars().all()

        bind = self.session.get_bind()
        dialect_name = bind.dialect.name if bind is not None else ""
        if dialect_name == "sqlite":
            trend_period = func.strftime("%Y-%m", FinancialRecord.entry_date)
        else:
            trend_period = func.to_char(FinancialRecord.entry_date, "YYYY-MM")
        trend_stmt = (
            select(
                trend_period.label("period"),
                func.coalesce(
                    func.sum(
                        case((FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount), else_=0)
                    ),
                    0,
                ).label("income"),
                func.coalesce(
                    func.sum(
                        case((FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount), else_=0)
                    ),
                    0,
                ).label("expense"),
            )
            .where(*base_filters)
            .group_by(trend_period)
            .order_by(trend_period)
            .limit(12)
        )
        trend_rows = (await self.session.execute(trend_stmt)).all()

        total_income = Decimal(str(totals_result.total_income or 0)).quantize(Decimal("0.01"))
        total_expenses = Decimal(str(totals_result.total_expense or 0)).quantize(Decimal("0.01"))

        return DashboardSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            net_balance=(total_income - total_expenses).quantize(Decimal("0.01")),
            category_breakdown=[
                CategoryTotal(
                    category=row.category,
                    total=Decimal(str(row.total or 0)).quantize(Decimal("0.01")),
                )
                for row in category_rows
            ],
            recent_activity=[
                RecentActivityItem(
                    id=record.id,
                    amount=Decimal(str(record.amount or ZERO)).quantize(Decimal("0.01")),
                    type=record.type.value,
                    category=record.category,
                    entry_date=record.entry_date.isoformat(),
                    notes=record.notes,
                )
                for record in recent_records
            ],
            monthly_trends=[
                TrendPoint(
                    period=row.period,
                    income=Decimal(str(row.income or 0)).quantize(Decimal("0.01")),
                    expense=Decimal(str(row.expense or 0)).quantize(Decimal("0.01")),
                    net=(
                        Decimal(str(row.income or 0)) - Decimal(str(row.expense or 0))
                    ).quantize(Decimal("0.01")),
                )
                for row in trend_rows
            ],
        )
