# Deploy & Share TalentFlow ATS

Share the app with others by running it on a small cloud server. One URL, login required, data saved per user.

## What gets deployed

| Service  | Role                          | Public port |
|----------|-------------------------------|-------------|
| Frontend | React dashboard (Nginx)       | **80**      |
| Backend  | FastAPI API (internal only)     | —           |
| Database | SQLite on a Docker volume     | —           |

Others open `http://YOUR_SERVER_IP`, sign up, and use AI Screening.

---

## Option A — VPS (recommended, ~$5–6/month)

Works on **DigitalOcean**, **Hetzner**, **AWS Lightsail**, **Azure VM**, etc.

### 1. Create a server

- **OS:** Ubuntu 22.04 or 24.04  
- **Size:** 2 GB RAM minimum (spaCy + ML need memory)  
- **Firewall:** allow **SSH (22)** and **HTTP (80)**

### 2. Install Docker on the server

SSH in, then:

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

Log out and back in so the `docker` group applies.

### 3. Upload the project

**Option 1 — Git (easiest if repo is on GitHub):**

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git resumescreening
cd resumescreening
```

**Option 2 — Copy from your PC:**

```bash
scp -r "Resume Screening" user@YOUR_SERVER_IP:~/resumescreening
ssh user@YOUR_SERVER_IP
cd ~/resumescreening
```

### 4. Set a secret key and start

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
docker compose -f docker-compose.prod.yml up -d --build
```

First build takes **5–15 minutes** (Python deps + spaCy model).

### 5. Share the link

Send others:

```
http://YOUR_SERVER_IP
```

They **Sign Up** → **Login** → **AI Screening** → upload resumes or **Run Demo Screening**.

### Useful commands

```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart after code update
git pull
docker compose -f docker-compose.prod.yml up -d --build

# Stop
docker compose -f docker-compose.prod.yml down

# Backup database
docker compose -f docker-compose.prod.yml exec backend cat /data/ats_database.db > backup.db
```

---

## Option B — Test sharing on your network first

Before paying for a server, verify Docker locally:

```bash
docker compose -f docker-compose.prod.yml up --build
```

Open **http://localhost** (port 80).  
Others on the same Wi‑Fi can use **http://YOUR_LAN_IP** (e.g. `http://192.168.1.5`).

---

## Option C — Custom domain + HTTPS (optional)

1. Point a domain **A record** to your server IP.  
2. Install Caddy on the server:

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy
```

3. Edit `/etc/caddy/Caddyfile`:

```
yourdomain.com {
    reverse_proxy localhost:80
}
```

4. `sudo systemctl reload caddy` — Caddy adds HTTPS automatically.

Share: `https://yourdomain.com`

---

## Option D — CI/CD (GitHub Actions)

For automatic deploys on every push to `main`, see `.github/workflows/deploy.yml`.

Required GitHub secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`, `REMOTE_COMPOSE_DIR`, `SECRET_KEY`.

Update image names in the workflow if not using Docker Hub.

---

## Environment variables

| Variable        | Default              | Purpose                    |
|-----------------|----------------------|----------------------------|
| `SECRET_KEY`    | (required in prod)   | Session security           |
| `DATABASE_PATH` | `./ats_database.db`  | SQLite file path           |
| `DEBUG`         | `false`              | Debug mode                 |

Create `.env` on the server:

```env
SECRET_KEY=your-long-random-string
```

Docker Compose reads it automatically.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Build fails on spaCy | Ensure server has **2 GB+ RAM**; retry build |
| “Screening failed” in UI | Check backend logs: `docker compose -f docker-compose.prod.yml logs backend` |
| Blank page after deploy | Wait for build to finish; check `docker compose ps` |
| Port 80 in use | Stop other web servers or change `"80:80"` to `"8080:80"` in compose file |
| Data lost after restart | Confirm `ats_data` volume exists: `docker volume ls` |

---

## What not to deploy

The **Streamlit** app (`app.py`) is for local use only. Share the **React + Docker** stack above.
