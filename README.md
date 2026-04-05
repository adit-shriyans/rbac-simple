# Zorvyn Finance Data Processing and Access Control

This project is built to match the backend assignment closely while staying easy to review. It includes a FastAPI backend in [be](/c:/study/projects/assignment/Zorvyn/be) and a minimal React playground frontend in [fe](/c:/study/projects/assignment/Zorvyn/fe). The API uses PostgreSQL for persistence and `x-user-role` headers to enforce role-based access control.

## What The Project Looks Like

1. `be` contains a clean FastAPI service with separated API routes, repositories, schemas, models, and services.
2. PostgreSQL stores users and financial records with explicit enums for user role, user status, and record type.
3. The dashboard summary endpoint computes totals, breakdowns, recent activity, and trends directly from PostgreSQL.
4. RBAC is enforced at the backend via `x-user-role`, with no frontend auth layer.
5. `fe` contains a minimal React + React Query playground to switch roles and hit every API directly.
6. The frontend intentionally performs almost no validation so backend validation/error handling remains visible.
7. The UI includes dark and light themes, a role switcher, and separate panels for users, records, and analytics.

## How To Nail The Assignment

1. Keep the backend structure obvious. Reviewers should be able to find routes, business logic, and data models instantly.
2. Make role behavior impossible to miss. Viewer, analyst, and admin should produce clearly different outcomes.
3. Treat summaries as first-class backend logic, not an afterthought on top of CRUD.
4. Use validation and clean error responses to show production-minded backend behavior.
5. Document the important assumptions, especially the decision to use `x-user-role` instead of full login.
6. Add enough thoughtful polish to feel complete, but avoid unnecessary architecture that slows down review.
7. Make local setup easy so the evaluator can run it quickly with just a Neon connection string.

## Bonus Points Added

1. A dedicated summary service for totals, breakdowns, recent activity, and monthly trends.
2. Pagination and filtering for financial records.
3. A demo seed script for quick review.
4. FastAPI Swagger and ReDoc docs exposed automatically.
5. A lightweight frontend playground so the evaluator can test RBAC and API behavior without Postman.
6. A minimal frontend playground so reviewers can test all APIs and role restrictions quickly.

## Tech Stack

- Backend: FastAPI, SQLAlchemy async, PostgreSQL
- Frontend: React, Vite, TanStack Query
- Persistence: Neon/PostgreSQL via `DATABASE_URL`
- Access control: `x-user-role` request header

## Role Matrix

| Role | Users | Records | Dashboard |
| --- | --- | --- | --- |
| Viewer | No access | Read only | No access |
| Analyst | Read only | Read only | Read summaries |
| Admin | Full access | Full access | Read summaries |

## Backend APIs

### Health

- `GET /api/health`

### Users

- `GET /api/users`
- `POST /api/users`
- `PATCH /api/users/{user_id}`

### Financial Records

- `GET /api/records?page=1&page_size=10&category=&type=&start_date=&end_date=`
- `POST /api/records`
- `PATCH /api/records/{record_id}`
- `DELETE /api/records/{record_id}`

### Dashboard

- `GET /api/dashboard/summary?start_date=&end_date=`

## Backend Structure

- [be/app/main.py](/c:/study/projects/assignment/Zorvyn/be/app/main.py): app bootstrap, CORS, router registration, startup/shutdown lifecycle
- [be/app/api](/c:/study/projects/assignment/Zorvyn/be/app/api): route modules and RBAC dependencies
- [be/app/models](/c:/study/projects/assignment/Zorvyn/be/app/models): SQLAlchemy models and enums
- [be/app/schemas](/c:/study/projects/assignment/Zorvyn/be/app/schemas): request/response schemas
- [be/app/repositories](/c:/study/projects/assignment/Zorvyn/be/app/repositories): database access layer
- [be/app/services](/c:/study/projects/assignment/Zorvyn/be/app/services): dashboard aggregation and business logic
- [be/app/db/seed_demo.py](/c:/study/projects/assignment/Zorvyn/be/app/db/seed_demo.py): optional demo data seeding

## Assumptions

1. Authentication is intentionally omitted because the assignment allows mock auth and you requested header-based role switching.
2. User management still exists as data, but request authorization is driven entirely by the `x-user-role` header.
3. Records are hard-deleted for simplicity.
4. Tables are auto-created on startup instead of using migrations to keep reviewer setup fast.
5. Dashboard summaries are computed on demand from PostgreSQL for simpler local setup.

## Local Setup

### Backend

1. Create a virtual environment inside [be](/c:/study/projects/assignment/Zorvyn/be).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy [be/.env.example](/c:/study/projects/assignment/Zorvyn/be/.env.example) to `be/.env`.
4. Replace `DATABASE_URL` with your Neon PostgreSQL connection string. Plain `postgresql://...` URLs are accepted and normalized automatically for the async driver.
5. Start the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Optional demo data:

```bash
python -m app.db.seed_demo
```

Docs:

- Swagger: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### Frontend

1. In [fe](/c:/study/projects/assignment/Zorvyn/fe), install dependencies:

```bash
npm install
```

2. Copy [fe/.env.example](/c:/study/projects/assignment/Zorvyn/fe/.env.example) to `fe/.env`.
3. Start the frontend:

```bash
npm run dev
```

4. Open `http://localhost:5173`.

## Nice Review Flow

1. Seed demo data.
2. Open the frontend playground.
3. Switch between `viewer`, `analyst`, and `admin` in the navbar.
4. Hit `GET /users`, `GET /records`, `POST /records`, and `GET /dashboard/summary`.
5. Confirm that unauthorized requests fail with backend-generated `403` responses.

## Future Improvements

1. Add JWT-based authentication while keeping the same role policy layer.
2. Add Alembic migrations for production-grade schema evolution.
3. Add test coverage for RBAC, validation, and summary aggregation.
4. Add soft deletes and audit logs for financial records.
