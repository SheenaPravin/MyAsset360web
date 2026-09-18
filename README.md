# MyAsset360 — AI-Powered Family Health, Asset & Wealth Management

Tagline: **"Manage Your Family's Wealth. Protect Your Family's Health."**

Monorepo containing the web platform (this repo `MyAsset360web`):
- `backend/` — FastAPI unified API (PostgreSQL/SQLite, JWT, family/assets/loans/insurance/health/docs/analytics/notifications). Deploys on Railway as **myasset360-api**.
- `web/` — Next.js 14 + TypeScript + Tailwind dashboards. Deploys on Railway as **myasset360-web**.

Mobile app lives in a separate repo: `MyAsset360Mobile` (Flutter).

## Quickstart (local)

Backend:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000, docs at /docs
# demo login: demo@myasset360.com / demo1234
```

Frontend:
```bash
cd web
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm install && npm run dev    # http://localhost:3000
```

## Deploy on Railway (2 services, 1 repo)

1. Create project `MyAsset360` in Railway, add PostgreSQL plugin.
2. Service 1 — API (`root directory = backend`):
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Env: `DATABASE_URL=${{Postgres.DATABASE_URL}}`, `SECRET_KEY=<long-random>`, `ACCESS_TOKEN_EXPIRE_MINUTES=10080`
   - Health check: `/health`
3. Service 2 — Web (`root directory = web`):
   - Build: `npm install && npm run build`, Start: `npm start`
   - Env: `NEXT_PUBLIC_API_URL=https://<api-service>.up.railway.app`
4. Open the web URL, login with `demo@myasset360.com / demo1234`, then Register your own family.

See `RAILWAY.md` for CLI commands.
