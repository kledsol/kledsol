# TrustLens — Deployment Guide (Render.com)

## Prerequisites

1. A [Render.com](https://render.com) account (free)
2. A [MongoDB Atlas](https://www.mongodb.com/atlas) account (free M0 tier)
3. Your code pushed to a GitHub repo (use "Save to Github" from Emergent)
4. Your Emergent LLM Key (for Claude Sonnet AI features)

---

## Step 1: Create MongoDB Atlas Database

1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a free cluster (M0 Sandbox)
3. Create a database user (Database Access → Add New User)
4. Allow all IPs (Network Access → Add IP → `0.0.0.0/0`)
5. Get your **connection string**: `mongodb+srv://USER:PASSWORD@cluster0.xxxxx.mongodb.net/trustlens?retryWrites=true&w=majority`

---

## Step 2: Deploy the Backend (Web Service)

1. On Render, click **New → Web Service**
2. Connect your GitHub repo
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `trustlens-api` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/` |
| **Start Command** | `uvicorn server:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

4. Add **Environment Variables**:

| Key | Value |
|-----|-------|
| `MONGO_URL` | `mongodb+srv://USER:PASSWORD@cluster0.xxxxx.mongodb.net/trustlens?retryWrites=true&w=majority` |
| `DB_NAME` | `trustlens` |
| `CORS_ORIGINS` | `https://trustlens.onrender.com` (update after frontend is created) |
| `EMERGENT_LLM_KEY` | Your Emergent LLM key |
| `JWT_SECRET` | A random secret (e.g. run `openssl rand -hex 32`) |

5. Click **Create Web Service**

Your backend will be live at: `https://trustlens-api.onrender.com`

---

## Step 3: Deploy the Frontend (Static Site)

1. On Render, click **New → Static Site**
2. Connect the same GitHub repo
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `trustlens` |
| **Root Directory** | `frontend` |
| **Build Command** | `yarn install && yarn build` |
| **Publish Directory** | `build` |

4. Add **Environment Variable**:

| Key | Value |
|-----|-------|
| `REACT_APP_BACKEND_URL` | `https://trustlens-api.onrender.com` |

5. Add **Rewrite Rules** (Settings → Redirects/Rewrites):

| Source | Destination | Action |
|--------|-------------|--------|
| `/api/*` | `https://trustlens-api.onrender.com/api/*` | Proxy |
| `/*` | `/index.html` | Rewrite |

The first rule proxies API calls to your backend.
The second enables React client-side routing.

6. Click **Create Static Site**

---

## Step 4: Update CORS

Go back to your backend environment variables and update `CORS_ORIGINS` with your actual frontend URL:

```
CORS_ORIGINS=https://trustlens.onrender.com
```

---

## Step 5: Verify

1. Open `https://trustlens.onrender.com`
2. The landing page should load
3. Click "Start Relationship Analysis" — the analysis flow should work
4. Test the API directly: `https://trustlens-api.onrender.com/api/cases/stats`

---

## Important Notes

- **Cold starts**: The free Render tier spins down after 15min of inactivity. First load may take 30-50 seconds.
- **MongoDB Atlas**: The free M0 tier provides 512MB — more than enough to start.
- **Emergent LLM Key**: If the key runs low, go to Profile → Universal Key → Add Balance on the Emergent platform.
- **Custom domain**: Render allows adding a custom domain for free (Settings → Custom Domains).
