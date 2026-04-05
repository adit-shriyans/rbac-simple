from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import db_session
from app.main import app
from app.models.base import Base
from app.models.enums import RecordType, UserRole, UserStatus
from app.models.financial_record import FinancialRecord
from app.models.user import User


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    future=True,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_db_session() -> AsyncIterator[AsyncSession]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[db_session] = override_db_session


@pytest_asyncio.fixture(autouse=True)
async def reset_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    async with TestingSessionLocal() as db:
        yield db


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    @asynccontextmanager
    async def no_op_lifespan(_app):
        yield

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = no_op_lifespan
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
    app.router.lifespan_context = original_lifespan


@pytest_asyncio.fixture
async def seeded_data(session: AsyncSession):
    users = [
        User(
            id=1,
            name="Admin User",
            email="admin@example.com",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            created_at=datetime(2026, 4, 1, 10, 0, tzinfo=UTC),
            updated_at=datetime(2026, 4, 1, 10, 0, tzinfo=UTC),
        ),
        User(
            id=2,
            name="Analyst User",
            email="analyst@example.com",
            role=UserRole.ANALYST,
            status=UserStatus.ACTIVE,
            created_at=datetime(2026, 4, 2, 10, 0, tzinfo=UTC),
            updated_at=datetime(2026, 4, 2, 10, 0, tzinfo=UTC),
        ),
        User(
            id=3,
            name="Viewer User",
            email="viewer@example.com",
            role=UserRole.VIEWER,
            status=UserStatus.INACTIVE,
            created_at=datetime(2026, 4, 3, 10, 0, tzinfo=UTC),
            updated_at=datetime(2026, 4, 3, 10, 0, tzinfo=UTC),
        ),
    ]

    records = [
        FinancialRecord(
            id=1,
            amount=Decimal("5000.00"),
            type=RecordType.INCOME,
            category="Salary",
            entry_date=date(2026, 1, 1),
            notes="January salary",
            created_by_user_id=1,
            created_at=datetime(2026, 4, 1, 11, 0, tzinfo=UTC),
            updated_at=datetime(2026, 4, 1, 11, 0, tzinfo=UTC),
        ),
        FinancialRecord(
            id=2,
            amount=Decimal("300.00"),
            type=RecordType.EXPENSE,
            category="Groceries",
            entry_date=date(2026, 1, 5),
            notes="Weekly grocery run",
            created_by_user_id=2,
            created_at=datetime(2026, 4, 2, 11, 0, tzinfo=UTC),
            updated_at=datetime(2026, 4, 2, 11, 0, tzinfo=UTC),
        ),
        FinancialRecord(
            id=3,
            amount=Decimal("1200.00"),
            type=RecordType.EXPENSE,
            category="Rent",
            entry_date=date(2026, 2, 1),
            notes="Monthly rent",
            created_by_user_id=1,
            created_at=datetime(2026, 4, 3, 11, 0, tzinfo=UTC),
            updated_at=datetime(2026, 4, 3, 11, 0, tzinfo=UTC),
        ),
        FinancialRecord(
            id=4,
            amount=Decimal("800.00"),
            type=RecordType.INCOME,
            category="Freelance",
            entry_date=date(2026, 2, 12),
            notes="Side project",
            created_by_user_id=2,
            created_at=datetime(2026, 4, 4, 11, 0, tzinfo=UTC),
            updated_at=datetime(2026, 4, 4, 11, 0, tzinfo=UTC),
        ),
    ]

    session.add_all(users + records)
    await session.commit()
    return {"users": users, "records": records}


def auth_headers(role: str) -> dict[str, str]:
    return {"x-user-role": role}
