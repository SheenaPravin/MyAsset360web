# MyAsset360 Web

Next.js 14 (App Router, TypeScript, Tailwind CSS 3) frontend for MyAsset360.

## Setup

```bash
cp .env.example .env.local
# set NEXT_PUBLIC_API_URL to your FastAPI backend, e.g. http://localhost:8000
npm install
npm run dev
```

Open http://localhost:3000.

## Backend contract (FastAPI)

`NEXT_PUBLIC_API_URL` points at the FastAPI root (no trailing slash).

| Page      | Endpoint(s)                                             |
|-----------|----------------------------------------------------------|
| Login     | `POST {API}/api/auth/login` (form-encoded `username`, `password` → `{ access_token, token_type }`) |
| Dashboard | `GET {API}/api/analytics/dashboard`                      |
| Assets    | `GET/POST {API}/api/assets/`                             |
| Loans     | `GET/POST {API}/api/loans/`                              |
| Insurance | `GET/POST {API}/api/insurance/`                          |
| Health    | `GET/POST {API}/api/health/expenses`, `GET {API}/api/health/records` |
| Vault     | `GET {API}/api/vault/documents`, `POST {API}/api/vault/upload` (multipart) |
| Insights  | `GET {API}/api/analytics/ai-insights`                    |

Auth: JWT Bearer token stored in `localStorage` key `myasset360_token`, attached via axios interceptor.

## Structure

```
app/layout.tsx            Root layout + Navbar
app/page.tsx              Landing hero
app/(auth)/login/page.tsx Login form
app/(app)/*/page.tsx      Dashboard, Assets, Loans, Insurance, Health, Vault, Insights
components/               Navbar, KpiCard, DataTable
lib/api.ts                axios instance + CRUD helpers
lib/format.ts             INR formatting + token helpers
```
