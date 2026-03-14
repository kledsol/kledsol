# TrustLens — Deployment Guide (Render.com)

This guide walks you through deploying TrustLens to **Render.com** with a **MongoDB Atlas** database.

---

## Prerequisites

1. A **GitHub** account (to push the code)
2. A **Render.com** account (free tier works)
3. A **MongoDB Atlas** account (free tier works)
4. Your **Emergent LLM Key** (already in your backend `.env`)

---

## Step 1: Create a MongoDB Atlas Database

1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com) and sign up / log in
2. Click **"Build a Database"** → Choose **M0 Free** tier
3. Select a region close to your users
4. Create a **database user** (username + password) — save these credentials
5. Under **Network Access**, click **"Add IP Address"** → **"Allow Access from Anywhere"** (`0.0.0.0/0`)
6. Go to **"Connect"** → **"Drivers"** → Copy the connection string. It looks like:
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
7. Replace `<username>` and `<password>` with your actual credentials

---

## Step 2: Push Code to GitHub

1. Save your code to GitHub using the **"Save to GitHub"** button in Emergent
2. This will create a repository with all your files

---

## Step 3: Deploy the Backend on Render

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

   | Setting | Value |
   |---------|-------|
   | **Name** | `trustlens-api` |
   | **Root Directory** | `backend` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/` |
   | **Start Command** | `uvicorn server:app --host 0.0.0.0 --port $PORT` |

5. Add **Environment Variables** (click "Add Environment Variable"):

   | Key | Value |
   |-----|-------|
   | `MONGO_URL` | Your MongoDB Atlas connection string from Step 1 |
   | `DB_NAME` | `trustlens` |
   | `CORS_ORIGINS` | `https://trustlens.onrender.com` (your frontend URL — update after creating frontend) |
   | `EMERGENT_LLM_KEY` | Your Emergent LLM key (`sk-emergent-...`) |
   | `JWT_SECRET` | Any random string (click "Generate" if available) |

6. Click **"Create Web Service"**
7. Wait for the build to complete. Note the URL (e.g., `https://trustlens-api.onrender.com`)

---

## Step 4: Deploy the Frontend on Render

1. Go to Render Dashboard → **"New +"** → **"Static Site"**
2. Connect the **same** GitHub repository
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
   | `REACT_APP_BACKEND_URL` | The backend URL from Step 3 (e.g., `https://trustlens-api.onrender.com`) |

5. Under **Redirects/Rewrites**, add a rule:
   - **Source**: `/*`
   - **Destination**: `/index.html`
   - **Action**: `Rewrite`

6. Click **"Create Static Site"**

---

## Step 5: Update CORS (Important!)

After the frontend is deployed, copy its URL (e.g., `https://trustlens.onrender.com`) and go back to your **backend service** on Render:

1. Go to **Environment** → Edit `CORS_ORIGINS`
2. Set it to your actual frontend URL: `https://trustlens.onrender.com`
3. The backend will automatically redeploy

---

## Step 6: Verify

1. Open your frontend URL in a browser
2. Click **"Start Relationship Analysis"**
3. Complete the flow to verify everything works end-to-end

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Backend won't start** | Check the Render logs. Make sure all env variables are set correctly |
| **"Network Error" on frontend** | Verify `REACT_APP_BACKEND_URL` points to the correct backend URL |
| **CORS errors in console** | Update `CORS_ORIGINS` in backend env to match your exact frontend URL |
| **MongoDB connection fails** | Check your Atlas connection string, ensure IP `0.0.0.0/0` is allowed |
| **AI analysis returns fallback** | Verify `EMERGENT_LLM_KEY` is set correctly in backend env |

---

## Free Tier Limitations

- **Render Free Tier**: Backend spins down after 15 minutes of inactivity. First request after sleep takes ~30 seconds
- **MongoDB Atlas M0**: 512 MB storage, shared cluster — sufficient for launch
- To avoid cold starts, consider upgrading to Render's paid tier ($7/month)

---

That's it! Your TrustLens app should now be live. 🎉
