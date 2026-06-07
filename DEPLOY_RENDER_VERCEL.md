Render + Vercel deployment
==========================

This guide shows the minimal steps to deploy the backend to Render and the frontend to Vercel. Files added to the repo:
- `Procfile`, `runtime.txt` (root) — backend start/runtime
- `render.yaml` (root) — optional infra-as-code for Render
- `frontend/vercel.json` — Vercel rewrite for `/api` → Render backend
- `.env.example` — example env variables

Steps
-----

1. Push repo to GitHub (if not already):

```bash
git add .
git commit -m "Add Render/Vercel deployment configs"
git push origin main
```

2. Backend: create Render Web Service

- Go to Render dashboard → New → Web Service → Connect your repo and select branch.
- Name: `ats-backend`
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`
- Add Environment Variables in Render (Dashboard → Environment):
  - `SECRET_KEY` = (strong value)
  - `ENV` = `production`
  - `DATABASE_URL` = (if using Postgres)

3. Frontend: Vercel static site

- Go to Vercel → Import Project → select this repo and set Project Root to `frontend`.
- Build Command: `npm ci && npm run build`
- Output Directory: `dist`
- Commit `frontend/vercel.json` rewrites to repo (already added), then set the Render backend domain into `frontend/vercel.json` by replacing `<YOUR_RENDER_BACKEND_DOMAIN>`.

4. (Optional) Use Render's `render.yaml`

- Render will detect `render.yaml` on connect; you can also create services manually and then set secrets in the Render dashboard.

5. Verify

- Visit Vercel URL: the frontend should load and API calls to `/api` will be proxied to Render.
- Backend health: `curl https://<render-backend-domain>/health` → `{"status":"ok"}`

6. Troubleshooting

- Logs: Render dashboard logs for the backend; Vercel deployment logs for frontend.
- CORS: `api.py` already configures permissive CORS.

If you want, I can now:
- Replace the placeholder in `frontend/vercel.json` with your Render domain, or
- Create a `render.yaml` variant that references Render secrets (fromSecret) instead of inline env values.
