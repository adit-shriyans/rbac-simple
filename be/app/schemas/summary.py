from decimal import Decimal

from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category: str
    total: Decimal


class TrendPoint(BaseModel):
    period: str
    income: Decimal
    expense: Decimal
    net: Decimal


class RecentActivityItem(BaseModel):
    id: int
    amount: Decimal
    type: str
    category: str
    entry_date: str
    notes: str | None


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    category_breakdown: list[CategoryTotal]
    recent_activity: list[RecentActivityItem]
    monthly_trends: list[TrendPoint]
