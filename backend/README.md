# MyAsset360 Backend (FastAPI)

Family Health, Asset & Wealth Management API — MVP Phase 1+2.

## Quick start

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional
uvicorn app.main:app --reload --port 8000
```

Open:
- API: http://localhost:8000/
- Health: http://localhost:8000/health
- Swagger: http://localhost:8000/docs

## Env vars

| Var | Default | Description |
|-----|---------|-------------|
| `SECRET_KEY` | dev key | JWT signing key |
| `DATABASE_URL` | `sqlite:///./myasset360.db` | Override with Postgres URL, e.g. `postgresql://user:pass@host:5432/db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT expiry |

SQLite works out of the box. For Postgres (Railway), set `DATABASE_URL` — `psycopg2-binary` is included.

## Demo seed

On startup, tables are created and a demo account is seeded if empty:

- Email: `demo@myasset360.com`
- Password: `demo1234`

Login via `POST /api/auth/login` (OAuth2 password flow: `username` + `password` form fields) to get a JWT, then use `Authorization: Bearer <token>`.

## Layout

- `app/main.py` — app, CORS, routers, startup seed
- `app/core/` — config, database, security (JWT + bcrypt)
- `app/models/models.py` — SQLAlchemy models
- `app/schemas/schemas.py` — Pydantic v2 schemas
- `app/routers/` — auth, families, assets, loans, insurance, health, documents, analytics, notifications
- `uploads/` — uploaded document files
```

## Railway deploy

Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
Set `DATABASE_URL` to the Postgres plugin URL and `SECRET_KEY` to a random string.
