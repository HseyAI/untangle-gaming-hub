# UNTANGLE - Deployment Checklist

> Step-by-step checklist for deploying to production

---

## Pre-Deployment

- [ ] All code committed and pushed to GitHub
- [ ] Backend `.env.example` is up to date
- [ ] Frontend `.env.example` is up to date
- [ ] Test credentials documented
- [ ] README.md is current

---

## GitHub Setup

- [ ] GitHub account created
- [ ] New repository created (e.g., `untangle-gaming-hub`)
- [ ] Local git repository initialized
- [ ] Code pushed to GitHub main branch

**Commands:**
```bash
git init
git add .
git commit -m "Initial commit - UNTANGLE MVP"
git remote add origin https://github.com/YOUR_USERNAME/untangle-gaming-hub.git
git branch -M main
git push -u origin main
```

---

## Backend Deployment (Railway)

### Railway Account

- [ ] Railway account created at https://railway.app
- [ ] Logged in with GitHub

### Deploy Backend

- [ ] New project created in Railway
- [ ] GitHub repository connected
- [ ] Root directory set to `backend`
- [ ] Environment variables added:
  - [ ] `SECRET_KEY` (generated randomly)
  - [ ] `DATABASE_URL=sqlite:///./untangle.db`
  - [ ] `ALGORITHM=HS256`
  - [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=30`
  - [ ] `REFRESH_TOKEN_EXPIRE_DAYS=7`
  - [ ] `ENVIRONMENT=production`
  - [ ] `LOG_LEVEL=INFO`
  - [ ] `ALLOWED_ORIGINS` (will update after frontend deployed)

**Generate SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Configure Start Command

- [ ] Custom start command set:
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Deploy & Test

- [ ] Deployment succeeded (green checkmark)
- [ ] Domain generated (e.g., `untangle-backend.up.railway.app`)
- [ ] Backend URL copied and saved
- [ ] Swagger UI accessible at `/docs`
- [ ] Health check passed

**Test URL:** `https://YOUR-BACKEND-URL.up.railway.app/docs`

### Seed Production Database

- [ ] Added temporary variable: `RUN_SEED=true`
- [ ] Updated start command:
```bash
alembic upgrade head && python seed_data.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
- [ ] Redeployed
- [ ] Removed `RUN_SEED` variable
- [ ] Reverted start command to original

### Test Backend

- [ ] `/docs` endpoint loads Swagger UI
- [ ] All 42 endpoints visible
- [ ] Login test successful (`admin@untangle.com` / `password123`)
- [ ] GET `/members` returns 5 test members
- [ ] GET `/dashboard/stats` returns statistics

---

## Frontend Deployment (Vercel)

### Update Frontend Config

- [ ] Frontend `.env` updated with backend URL:
```env
VITE_API_URL=https://YOUR-BACKEND-URL.up.railway.app/api/v1
```
- [ ] Changes committed and pushed

### Vercel Account

- [ ] Vercel account created at https://vercel.com
- [ ] Logged in with GitHub

### Deploy Frontend

- [ ] New project created
- [ ] GitHub repository imported
- [ ] Project settings configured:
  - [ ] Framework: Vite
  - [ ] Root Directory: `frontend`
  - [ ] Build Command: `npm run build`
  - [ ] Output Directory: `dist`
- [ ] Environment variable added:
  - [ ] `VITE_API_URL=https://YOUR-BACKEND-URL.up.railway.app/api/v1`

### Deploy & Test

- [ ] Deployment succeeded
- [ ] Frontend URL obtained (e.g., `untangle-frontend.vercel.app`)
- [ ] Frontend URL copied and saved
- [ ] Site loads correctly
- [ ] Login page displays

**Test URL:** `https://YOUR-FRONTEND-URL.vercel.app`

---

## CORS Configuration

### Update Backend CORS

- [ ] Back in Railway dashboard
- [ ] Updated `ALLOWED_ORIGINS` variable:
```env
ALLOWED_ORIGINS=["https://YOUR-FRONTEND-URL.vercel.app"]
```
- [ ] Backend redeployed
- [ ] CORS working (no console errors)

---

## End-to-End Testing

### Authentication

- [ ] Frontend login page loads
- [ ] Login with admin@untangle.com / password123 works
- [ ] Redirected to dashboard after login
- [ ] Token stored in localStorage
- [ ] Auto-logout on token expiry works

### Dashboard

- [ ] Statistics display correctly
- [ ] Total members shows: 5
- [ ] Total revenue calculated
- [ ] Active sessions count shown
- [ ] Member alerts (expiring/expired) shown

### Members Page

- [ ] Members list loads (5 members)
- [ ] Search by name works
- [ ] Search by mobile works
- [ ] Balance and expiry dates correct
- [ ] Status indicators (active/expiring/expired) working

### Purchases Page

- [ ] Purchases list loads (5 purchases)
- [ ] Rollover status indicators correct
- [ ] Expiry dates calculated correctly
- [ ] Purchase details accurate

### Sessions Page

- [ ] Sessions list loads (5 sessions)
- [ ] Active sessions shown
- [ ] Completed sessions shown
- [ ] Hours consumed calculated
- [ ] Game titles and station info displayed

### API Testing

- [ ] Swagger UI accessible
- [ ] All 42 endpoints documented
- [ ] Authorization working
- [ ] Test all critical endpoints:
  - [ ] POST `/auth/login`
  - [ ] GET `/auth/me`
  - [ ] GET `/members`
  - [ ] GET `/purchases`
  - [ ] GET `/sessions`
  - [ ] GET `/dashboard/stats`

---

## Performance Check

- [ ] Frontend loads in < 3 seconds
- [ ] API responses < 500ms
- [ ] No console errors
- [ ] No network errors
- [ ] Mobile responsive design works

---

## Security Verification

- [ ] HTTPS enabled (automatic on Railway/Vercel)
- [ ] SECRET_KEY is random and secure
- [ ] Default passwords documented (should be changed)
- [ ] CORS only allows frontend URL
- [ ] No sensitive data in GitHub repository
- [ ] `.env` files in `.gitignore`

---

## Documentation

- [ ] DEPLOYMENT.md complete
- [ ] README.md updated with deployment status
- [ ] Test credentials documented
- [ ] Environment variables documented
- [ ] API endpoints documented

---

## Optional: Custom Domains

### Frontend Custom Domain

- [ ] Domain purchased
- [ ] DNS configured in Vercel
- [ ] SSL certificate issued
- [ ] Frontend accessible at custom domain

### Backend Custom Domain

- [ ] Subdomain configured (e.g., `api.yourdomain.com`)
- [ ] DNS configured in Railway
- [ ] SSL certificate issued
- [ ] Backend accessible at custom domain

### Update Configuration

- [ ] Frontend `.env` updated with new backend URL
- [ ] Backend `ALLOWED_ORIGINS` updated with new frontend URL
- [ ] Both services redeployed
- [ ] Tested end-to-end

---

## Post-Deployment Tasks

### Immediate

- [ ] Change default admin password
- [ ] Change default manager password
- [ ] Change default staff password
- [ ] Test all changed passwords work

### First Week

- [ ] Add real members (remove test data if needed)
- [ ] Create real user accounts
- [ ] Monitor error logs in Railway
- [ ] Monitor access logs in Vercel
- [ ] Check database size

### Future Enhancements

- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Enable Google OAuth
- [ ] Integrate Dodo Payments
- [ ] Add email notifications
- [ ] Implement rate limiting
- [ ] Add audit logging
- [ ] Set up automated backups

---

## Monitoring & Maintenance

### Daily

- [ ] Check Railway logs for errors
- [ ] Check Vercel analytics for traffic
- [ ] Monitor database size

### Weekly

- [ ] Review error logs
- [ ] Check performance metrics
- [ ] Verify automated backups (if configured)
- [ ] Test critical user flows

### Monthly

- [ ] Review Railway usage (stay within free tier)
- [ ] Review Vercel bandwidth usage
- [ ] Update dependencies (security patches)
- [ ] Database cleanup (old sessions, logs)

---

## Rollback Plan

If deployment fails or critical issues found:

### Backend Rollback

- [ ] In Railway, go to Deployments tab
- [ ] Find previous working deployment
- [ ] Click "Redeploy"
- [ ] Verify services restored

### Frontend Rollback

- [ ] In Vercel, go to Deployments tab
- [ ] Find previous working deployment
- [ ] Click "Promote to Production"
- [ ] Verify site restored

### Database Rollback

- [ ] Download backup (if configured)
- [ ] Run: `alembic downgrade -1`
- [ ] Or restore from backup SQL file

---

## Troubleshooting

### Backend Issues

**Deployment fails:**
- [ ] Check Railway build logs
- [ ] Verify `requirements.txt` is complete
- [ ] Check environment variables are set
- [ ] Verify start command is correct

**Database migration fails:**
- [ ] SSH into Railway (railway login + railway run)
- [ ] Run: `alembic upgrade head`
- [ ] Check migration files for errors

**API returns 500 errors:**
- [ ] Check Railway logs
- [ ] Verify database is accessible
- [ ] Check SECRET_KEY is set
- [ ] Verify all environment variables

### Frontend Issues

**Deployment fails:**
- [ ] Check Vercel build logs
- [ ] Verify `package.json` scripts are correct
- [ ] Check for TypeScript errors
- [ ] Verify build command

**Can't connect to backend:**
- [ ] Check `VITE_API_URL` in Vercel settings
- [ ] Verify backend is running
- [ ] Check CORS settings on backend
- [ ] Check browser console for errors

**401 Unauthorized:**
- [ ] Verify login works
- [ ] Check token is stored in localStorage
- [ ] Verify SECRET_KEY matches
- [ ] Test login again

---

## Success Criteria

Deployment is complete when:

- ✅ Backend accessible at production URL
- ✅ Frontend accessible at production URL
- ✅ Login works end-to-end
- ✅ All 5 pages load correctly
- ✅ All test data visible
- ✅ No console errors
- ✅ No network errors
- ✅ Mobile responsive
- ✅ HTTPS enabled
- ✅ Performance acceptable (< 3s load)

---

## Support Resources

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev
- **This Project:** See DEPLOYMENT.md and README.md

---

**Status:** Ready for Production Deployment 🚀

**Estimated Time:** 15-20 minutes
