# Host on Render — MyAsset360web

Free-tier hosting via the `render.yaml` Blueprint at the repo root
(API + Web + Postgres).

## One-click deploy (2 minutes)

1. Go to **https://dashboard.render.com/select-repo?type=blueprint**
   (or Dashboard → New → Blueprint).
2. Connect/select repo **`SheenaPravin/MyAsset360web`**, branch `main`.
3. Render detects `render.yaml` and plans 3 resources:
   - `myasset360-db` (Postgres, free — expires after 30 days, fine for POC)
   - `myasset360-api` (Python/FastAPI, free)
   - `myasset360-web` (Node/Next.js, free)
4. Approve → Deploy. First build takes ~5–10 min (free tier).
5. Open `https://myasset360-web.onrender.com`, login with
   `demo@myasset360.com` / `demo1234` (auto-seeded).

> If Render renames the API service URL (e.g. `myasset360-api-xxxx.onrender.com`),
> set `myasset360-web` env var `NEXT_PUBLIC_API_URL` to the real API URL in the
> dashboard and redeploy the web service.

## Notes

- Free web services **spin down after ~15 min idle**; first request takes ~30–60s to wake.
- Backend health check: `https://myasset360-api.onrender.com/health`, API docs: `/docs`.
- Flutter app (`MyAsset360Mobile`): run with
  `flutter run --dart-define API_URL=https://myasset360-api.onrender.com`.
