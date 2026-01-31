# UNTANGLE - Production Deployment Guide

> Deploy your Gaming Hub Management System to production in under 15 minutes

---

## Overview

- **Backend:** Railway (Free tier - FastAPI + SQLite)
- **Frontend:** Vercel (Free tier - React + TypeScript)
- **Database:** SQLite (included with backend)

---

## Prerequisites

1. **GitHub Account** (free)
2. **Railway Account** (free) - https://railway.app
3. **Vercel Account** (free) - https://vercel.com
4. **Git installed** (to push code)

---

## Part 1: Deploy Backend to Railway

### Step 1: Initialize Git Repository

```bash
# Navigate to project root
cd "C:\YESH\My Projects\my-saas"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - UNTANGLE Gaming Hub MVP"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `untangle-gaming-hub`)
3. **Don't** initialize with README (we already have code)
4. Click "Create repository"

### Step 3: Push to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/untangle-gaming-hub.git

# Push code
git branch -M main
git push -u origin main
```

### Step 4: Deploy Backend on Railway

1. Go to https://railway.app
2. Sign up / Log in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository: `untangle-gaming-hub`
5. Railway will detect it's a Python project

### Step 5: Configure Backend Service

1. In Railway dashboard, click on your service
2. Click **"Settings"** tab
3. Set **Root Directory** to `backend`
4. Click **"Variables"** tab
5. Add environment variables:

```env
SECRET_KEY=<generate-random-32-char-string>
DATABASE_URL=sqlite:///./untangle.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["https://your-frontend-url.vercel.app"]
```

**To generate SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

6. Click **"Deploy"** in top right

### Step 6: Get Backend URL

1. After deployment succeeds, click **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://untangle-backend-production.up.railway.app`)
5. **Save this URL** - you'll need it for frontend

### Step 7: Run Database Migration

1. In Railway dashboard, click **"Settings"** → **"Deploy"**
2. Add a **Custom Start Command**:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

3. Redeploy the service

### Step 8: Seed Production Database

1. Click **"Variables"** tab
2. Add temporary variable: `RUN_SEED=true`
3. Update start command:

```bash
alembic upgrade head && python seed_data.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

4. After deployment, **remove** `RUN_SEED` variable and revert start command to:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 9: Test Backend

Visit: `https://your-backend-url.up.railway.app/docs`

You should see the Swagger UI with all 42 API endpoints.

**Test login:**
- Email: `admin@untangle.com`
- Password: `password123`

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Update Frontend Environment

1. Edit `frontend/.env`:

```env
VITE_API_URL=https://your-backend-url.up.railway.app/api/v1
```

Replace with your actual Railway backend URL.

2. Commit changes:

```bash
git add frontend/.env
git commit -m "Update API URL for production"
git push
```

### Step 2: Deploy Frontend on Vercel

1. Go to https://vercel.com
2. Sign up / Log in with GitHub
3. Click **"Add New"** → **"Project"**
4. Import your GitHub repository
5. Configure project:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

6. Click **"Deploy"**

### Step 3: Configure Environment Variables

1. After deployment, go to project **"Settings"** → **"Environment Variables"**
2. Add:

```env
VITE_API_URL=https://your-backend-url.up.railway.app/api/v1
```

3. Redeploy from **"Deployments"** tab

### Step 4: Get Frontend URL

1. After deployment succeeds, you'll see the URL (e.g., `https://untangle-frontend.vercel.app`)
2. **Copy this URL**

### Step 5: Update Backend CORS

1. Go back to Railway dashboard
2. Click **"Variables"** tab
3. Update `ALLOWED_ORIGINS`:

```env
ALLOWED_ORIGINS=["https://untangle-frontend.vercel.app"]
```

Replace with your actual Vercel frontend URL.

4. Redeploy backend

---

## Part 3: Test Production System

### Step 1: Test Authentication

1. Visit your frontend URL: `https://untangle-frontend.vercel.app`
2. You should see the login page
3. Test credentials:
   - **Admin:** `admin@untangle.com` / `password123`
   - **Manager:** `manager@untangle.com` / `password123`
   - **Staff:** `staff@untangle.com` / `password123`

### Step 2: Test All Modules

**Dashboard:**
- Verify stats load correctly
- Check total members, revenue, active sessions

**Members:**
- View members list (should show Arjun Patel, Priya Sharma, etc.)
- Search by name/mobile
- Check balance and expiry dates

**Purchases:**
- View all purchases
- Check rollover status indicators
- Verify expiry date calculations

**Sessions:**
- View gaming sessions
- Check active/completed status
- Verify hours consumed calculations

### Step 3: Test API Directly

Visit: `https://your-backend-url.up.railway.app/docs`

**Test sequence:**
1. POST `/auth/login` - Get access token
2. Click "Authorize" button, paste token
3. GET `/members` - Should return 5 members
4. GET `/purchases` - Should return 5 purchases
5. GET `/sessions` - Should return 5 sessions
6. GET `/dashboard/stats` - Should return aggregated stats

---

## Monitoring & Logs

### Railway (Backend)

1. Click **"Deployments"** tab to see build logs
2. Click **"Observability"** to see runtime logs
3. Monitor CPU/Memory usage

### Vercel (Frontend)

1. Click **"Deployments"** to see build logs
2. Click **"Analytics"** to see visitor stats
3. Monitor page load times

---

## Database Backup

### Export SQLite Database

1. In Railway, click **"Settings"** → **"Data"**
2. Set up automated backups (available on paid plans)

OR manually via CLI:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Download database
railway run sqlite3 untangle.db .dump > backup.sql
```

---

## Custom Domain (Optional)

### Frontend Domain

1. In Vercel, go to **"Settings"** → **"Domains"**
2. Add your custom domain (e.g., `app.untangle.com`)
3. Configure DNS records as shown

### Backend Domain

1. In Railway, go to **"Settings"** → **"Domains"**
2. Add custom domain (e.g., `api.untangle.com`)
3. Configure DNS records

**Don't forget to update:**
- Backend `ALLOWED_ORIGINS` with new frontend domain
- Frontend `.env` with new backend domain

---

## Environment Variables Summary

### Backend (Railway)

```env
SECRET_KEY=<random-32-char-string>
DATABASE_URL=sqlite:///./untangle.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["https://untangle-frontend.vercel.app"]
```

### Frontend (Vercel)

```env
VITE_API_URL=https://untangle-backend-production.up.railway.app/api/v1
```

---

## Troubleshooting

### Backend won't start

**Check logs in Railway:**
```
railway logs
```

**Common issues:**
- Missing environment variables
- Database migration failed - Check `alembic upgrade head` succeeded
- Import errors - Ensure all dependencies in `requirements.txt`

### Frontend can't connect to backend

**Check:**
1. `VITE_API_URL` is correct in Vercel environment variables
2. Backend `ALLOWED_ORIGINS` includes frontend URL
3. Backend is actually running (visit `/docs` endpoint)
4. CORS errors in browser console

### 401 Unauthorized errors

**Check:**
1. Token is being sent in `Authorization: Bearer <token>` header
2. `SECRET_KEY` matches between deployments
3. Token hasn't expired (30 min default)

### Database migration fails

**Run manually in Railway:**
```bash
railway run alembic upgrade head
```

---

## Scaling & Costs

### Free Tier Limits

**Railway:**
- 500 hours/month ($5 credit)
- 1GB RAM, 1 vCPU
- 1GB storage

**Vercel:**
- 100GB bandwidth/month
- Unlimited deployments
- Automatic SSL

### When to upgrade

- More than 100 concurrent users → Upgrade Railway plan
- Need PostgreSQL instead of SQLite → Add Railway PostgreSQL service
- Need real-time features → Add WebSocket support

---

## Security Checklist

- [ ] Changed `SECRET_KEY` from default
- [ ] Removed test credentials in production (or changed passwords)
- [ ] HTTPS enabled (automatic on Railway/Vercel)
- [ ] CORS configured correctly (only your frontend URL)
- [ ] Environment variables set (not hardcoded in code)
- [ ] Database backups scheduled
- [ ] Rate limiting enabled (TODO: add middleware)
- [ ] Input validation working (already implemented)

---

## Next Steps After Deployment

1. **Change default passwords** for admin/manager/staff
2. **Add your actual members** via the Members page
3. **Configure Google OAuth** (optional - update `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`)
4. **Add Dodo Payments** (optional - update `DODO_API_KEY`)
5. **Set up monitoring** (Sentry, LogRocket)
6. **Enable rate limiting** (add middleware)
7. **Add email notifications** (for expiring memberships)
8. **Implement WebSocket** (for real-time session updates)

---

## Support & Resources

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev

---

## Quick Reference

### Backend URLs
- API Docs: `https://your-backend.up.railway.app/docs`
- Health Check: `https://your-backend.up.railway.app/health`
- API Base: `https://your-backend.up.railway.app/api/v1`

### Frontend URL
- App: `https://your-frontend.vercel.app`

### Test Credentials
- **Admin:** admin@untangle.com / password123
- **Manager:** manager@untangle.com / password123
- **Staff:** staff@untangle.com / password123

---

**Deployment Complete!** Your UNTANGLE Gaming Hub is now live in production.
