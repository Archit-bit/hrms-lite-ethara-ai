# HRMS Lite

HRMS Lite is a lightweight internal HR tool for managing employees and tracking daily attendance. It ships as a React frontend plus a FastAPI backend with SQL persistence, reusable UI components, validation, and production-oriented configuration for local or hosted deployment.

## Features

- Add employees with unique employee IDs and email addresses
- View employee records with total present days
- Delete employees and remove their attendance history
- Mark daily attendance as `PRESENT` or `ABSENT`
- Filter attendance records by employee and date
- Dashboard summary for employee count and daily attendance totals
- RESTful API with validation, duplicate handling, and meaningful error responses

## Tech Stack

- Frontend: React 18, TypeScript, Vite, CSS
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: SQLite for local development, PostgreSQL via `.env` fields or `DATABASE_URL`
- Testing: Pytest and HTTPX

## Project Structure

```text
backend/
  app/
    api/
      routes/
    core/
    db/
    models/
    repositories/
    schemas/
    services/
  tests/
frontend/
  src/
```

## Local Setup

### 1. Install dependencies

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd frontend && npm install
```

### 2. Configure environment variables

Backend example: [backend/.env.example](/mnt/hdd/full STack/HRMS_ETHARA.AI/backend/.env.example)

Frontend example: [frontend/.env.example](/mnt/hdd/full STack/HRMS_ETHARA.AI/frontend/.env.example)

Create `backend/.env` from the example and choose one database mode.

SQLite:

```env
DB_ENGINE=sqlite
SQLITE_PATH=data/hrms.db
```

PostgreSQL:

```env
DB_ENGINE=postgresql
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hrms_lite
POSTGRES_SCHEMA=public
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

If you already have a full connection string, set `DATABASE_URL` and it will take precedence over the individual fields.

### 3. Run the backend

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run the frontend

```bash
cd frontend
npm run dev
```

Frontend URL: `http://localhost:5173`

Backend URL: `http://localhost:8000`

## Verification

Backend tests:

```bash
cd backend
../.venv/bin/pytest
```

Frontend production build:

```bash
cd frontend
npm run build
```

## API Summary

- `GET /health`
- `GET /api/dashboard`
- `GET /api/employees`
- `POST /api/employees`
- `DELETE /api/employees/{employee_id}`
- `GET /api/employees/{employee_id}/attendance`
- `GET /api/attendance`
- `POST /api/attendance`

## Deployment Notes

- Backend: deploy `backend/` to Render or Railway with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Frontend: deploy `frontend/` to Vercel or Netlify with `VITE_API_BASE_URL` pointing to the live backend
- Set `CORS_ORIGINS` on the backend to include the deployed frontend origin
- Use PostgreSQL in production by either setting `DATABASE_URL` or the `POSTGRES_*` fields in `backend/.env`

## Assumptions and Limitations

- Single admin user; authentication is intentionally out of scope
- One attendance entry is allowed per employee per date
- Deleting an employee removes their attendance records
- SQLite is used locally for simplicity; production should use a managed database
- Public deployment URLs and a GitHub repository were not created from this environment because external hosting and repository credentials were not available here
