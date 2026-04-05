import asyncio
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.enums import RecordType, UserRole, UserStatus
from app.models.financial_record import FinancialRecord
from app.models.user import User


async def seed_demo_data() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        existing_users = await session.execute(select(User.id).limit(1))
        if existing_users.first():
            print("Seed skipped: users already exist.")
            return

        admin = User(
            name="Admin User",
            email="admin@zorvyn.local",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        analyst = User(
            name="Analyst User",
            email="analyst@zorvyn.local",
            role=UserRole.ANALYST,
            status=UserStatus.ACTIVE,
        )
        viewer = User(
            name="Viewer User",
            email="viewer@zorvyn.local",
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
        )

        session.add_all([admin, analyst, viewer])
        await session.flush()

        session.add_all(
            [
                FinancialRecord(
                    amount=Decimal("4800.00"),
                    type=RecordType.INCOME,
                    category="Salary",
                    entry_date=date(2026, 1, 31),
                    notes="January salary",
                    created_by_user_id=admin.id,
                ),
                FinancialRecord(
                    amount=Decimal("320.00"),
                    type=RecordType.EXPENSE,
                    category="Groceries",
                    entry_date=date(2026, 2, 3),
                    notes="Monthly grocery spend",
                    created_by_user_id=admin.id,
                ),
                FinancialRecord(
                    amount=Decimal("900.00"),
                    type=RecordType.INCOME,
                    category="Freelance",
                    entry_date=date(2026, 2, 15),
                    notes="Client retainer",
                    created_by_user_id=analyst.id,
                ),
                FinancialRecord(
                    amount=Decimal("1200.00"),
                    type=RecordType.EXPENSE,
                    category="Rent",
                    entry_date=date(2026, 3, 1),
                    notes="March rent",
                    created_by_user_id=admin.id,
                ),
                FinancialRecord(
                    amount=Decimal("240.00"),
                    type=RecordType.EXPENSE,
                    category="Utilities",
                    entry_date=date(2026, 3, 10),
                    notes="Electricity and internet",
                    created_by_user_id=analyst.id,
                ),
            ]
        )

        await session.commit()
        print("Seeded demo users and financial records.")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
