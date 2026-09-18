# Railway deployment — MyAsset360web

This repo deploys as **two Railway services** from one GitHub repo.

## Option A: Dashboard (recommended)

1. railway.app → New Project → Deploy from GitHub → `SheenaPravin/MyAsset360web`
2. Add **PostgreSQL** plugin (Variables → `DATABASE_URL`).
3. Create service `myasset360-api`:
   - Settings → Source → Root Directory = `backend`
   - Start Command = `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Variables: `DATABASE_URL=${{Postgres.DATABASE_URL}}`, `SECRET_KEY` (generate: `openssl rand -hex 32`), `ACCESS_TOKEN_EXPIRE_MINUTES=10080`
   - Healthcheck Path = `/health`
   - Generate Domain → note `https://xxx.up.railway.app`
4. Create service `myasset360-web`:
   - Root Directory = `web`
   - Build = `npm install && npm run build`, Start = `npm start`
   - Variables: `NEXT_PUBLIC_API_URL=https://<api-domain>.up.railway.app`
   - Generate Domain.

## Option B: CLI

```bash
npm i -g @railway/cli || brew install railway
railway login
railway init  # project MyAsset360
railway add --database postgres
# backend service
railway service create myasset360-api
railway link && railway up --service myasset360-api
railway variables set DATABASE_URL='${{Postgres.DATABASE_URL}}' SECRET_KEY='change-me' --service myasset360-api
# frontend service
railway service create myasset360-web
railway up --service myasset360-web
railway variables set NEXT_PUBLIC_API_URL='https://<api>.up.railway.app' --service myasset360-web
```

Demo login after deploy: `demo@myasset360.com / demo1234` (auto-seeded on first boot).
