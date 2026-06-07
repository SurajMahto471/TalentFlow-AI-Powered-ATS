# Fix Render deployment (Vercel frontend + Render backend)

## What was wrong

1. **Port** — Dockerfile used port `8000` fixed; Render requires **`$PORT`**.
2. **Heavy build** — `requirements.txt` included Streamlit; free tier often runs out of memory during build.
3. **render.yaml** — Deployed 3 services (API + Streamlit + static site). Use **one Docker web service** only; frontend stays on Vercel.

---

## Render setup (do this in the dashboard)

### 1. Delete extra Render services (if any)

Keep only **one** Web Service for the API. Remove:
- `ats-streamlit` (Streamlit is local-only)
- `ats-frontend` static site (you use Vercel)

### 2. Create / fix the API Web Service

| Setting | Value |
|---------|--------|
| **Name** | `talentflow-api` (or your existing name) |
| **Root Directory** | *(blank — repo root)* |
| **Environment** | **Docker** |
| **Dockerfile Path** | `Dockerfile` |
| **Branch** | `main` |
| **Plan** | Free (demo) or **Starter $7** (recommended for spaCy) |
| **Health Check Path** | `/health` |

### 3. Environment variables

| Key | Value |
|-----|--------|
| `DATABASE_PATH` | `/tmp/ats_database.db` |
| `SECRET_KEY` | *(generate a long random string)* |

### 4. Deploy

Push the latest code to GitHub → Render **Manual Deploy** or auto-deploy.

First build takes **10–20 minutes** (spaCy + scikit-learn).

### 5. Verify backend

Open:

```
https://YOUR-SERVICE-NAME.onrender.com/health
```

Expected: `{"status":"ok"}`

If this fails, open **Logs** in Render and check the error at the bottom.

---

## Vercel setup

1. Root directory: **`frontend`**
2. Update `frontend/vercel.json` — replace the Render URL with **your** exact Render service URL:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://YOUR-SERVICE-NAME.onrender.com/$1"
    }
  ]
}
```

3. Redeploy Vercel after changing `vercel.json`.

---

## Common Render errors

| Error in logs | Fix |
|---------------|-----|
| `No open ports detected` / `Port scan timeout` | Pull latest code (Dockerfile uses `$PORT`) |
| `Ran out of memory` during build | Upgrade to **Starter** plan, or retry build |
| `Can't find model 'en_core_web_sm'` | Rebuild — Dockerfile downloads the model |
| Build timeout | Normal on free tier; wait or use Starter |
| Service sleeps 30–60s on first visit | Free tier cold start — normal |
| Login works then fails | Free tier restarted — log in again; data on `/tmp` may reset |

---

## Share link

Give others your **Vercel** URL only:

```
https://your-app.vercel.app
```

Not the raw Render URL.
