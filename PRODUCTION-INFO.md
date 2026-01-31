# UNTANGLE - Production Information

> Fill this out after deployment completes

---

## Production URLs

### Backend (Railway)

**API Base URL:**
```
https://_____________________.up.railway.app
```

**API Documentation:**
```
https://_____________________.up.railway.app/docs
```

**Health Check:**
```
https://_____________________.up.railway.app/health
```

### Frontend (Vercel)

**Application URL:**
```
https://_____________________.vercel.app
```

### Custom Domains (if configured)

**Frontend:**
```
https://_____________________
```

**Backend API:**
```
https://_____________________
```

---

## Deployment Dates

| Event | Date | Time |
|-------|------|------|
| Backend Deployed | __________ | __________ |
| Frontend Deployed | __________ | __________ |
| Database Seeded | __________ | __________ |
| First Production Login | __________ | __________ |

---

## Test Credentials (Change After First Login!)

| Role | Email | Password | Status |
|------|-------|----------|--------|
| Admin | admin@untangle.com | password123 | ⚠️ CHANGE IMMEDIATELY |
| Manager | manager@untangle.com | password123 | ⚠️ CHANGE IMMEDIATELY |
| Staff | staff@untangle.com | password123 | ⚠️ CHANGE IMMEDIATELY |

---

## Production Credentials (After Password Change)

| Role | Email | New Password | Changed On |
|------|-------|--------------|------------|
| Admin | admin@untangle.com | [REDACTED] | __________ |
| Manager | manager@untangle.com | [REDACTED] | __________ |
| Staff | staff@untangle.com | [REDACTED] | __________ |

**⚠️ DO NOT commit this file with real passwords!**

---

## Environment Variables

### Backend (Railway)

**Configured:**
- [x] SECRET_KEY (value: `_____________________`)
- [x] DATABASE_URL (value: `sqlite:///./untangle.db`)
- [x] ALGORITHM (value: `HS256`)
- [x] ACCESS_TOKEN_EXPIRE_MINUTES (value: `30`)
- [x] REFRESH_TOKEN_EXPIRE_DAYS (value: `7`)
- [x] ENVIRONMENT (value: `production`)
- [x] LOG_LEVEL (value: `INFO`)
- [x] ALLOWED_ORIGINS (value: `["https://YOUR-FRONTEND-URL"]`)

**Optional (not yet configured):**
- [ ] GOOGLE_CLIENT_ID
- [ ] GOOGLE_CLIENT_SECRET
- [ ] DODO_API_KEY
- [ ] DODO_WEBHOOK_SECRET

### Frontend (Vercel)

**Configured:**
- [x] VITE_API_URL (value: `https://YOUR-BACKEND-URL/api/v1`)

---

## Database

**Type:** SQLite

**Location:** Railway persistent volume

**Backup Strategy:**
- Manual: `railway run sqlite3 untangle.db .dump > backup.sql`
- Automated: ⚠️ Not configured (Railway paid plan required)

**Last Backup:**
```
Date: __________
Size: __________
Location: __________
```

---

## Monitoring

### Railway (Backend)

**Metrics to Watch:**
- CPU usage (target: < 50%)
- Memory usage (target: < 512MB)
- Request rate (target: < 100 req/min on free tier)
- Error rate (target: < 1%)

**Logs:**
```
https://railway.app/project/YOUR-PROJECT-ID/logs
```

### Vercel (Frontend)

**Metrics to Watch:**
- Bandwidth (target: < 100GB/month)
- Page load time (target: < 2s)
- Build time (target: < 2 min)
- Visitor count

**Analytics:**
```
https://vercel.com/YOUR-USERNAME/YOUR-PROJECT/analytics
```

---

## Performance Baselines

| Metric | Baseline | Current | Status |
|--------|----------|---------|--------|
| Frontend Load Time | < 3s | _____ | _____ |
| API Response Time | < 500ms | _____ | _____ |
| Login Flow | < 2s | _____ | _____ |
| Dashboard Load | < 2s | _____ | _____ |
| Member Search | < 1s | _____ | _____ |

---

## Deployment History

| Version | Date | Changes | Deployed By |
|---------|------|---------|-------------|
| 1.0.0 | __________ | Initial MVP deployment | __________ |
| | | | |
| | | | |

---

## Incident Log

| Date | Severity | Issue | Resolution | Duration |
|------|----------|-------|------------|----------|
| | | | | |
| | | | | |

---

## Maintenance Windows

| Date | Time | Duration | Reason | Status |
|------|------|----------|--------|--------|
| | | | | |
| | | | | |

---

## Contacts

**Development Team:**
- Primary: __________
- Email: __________
- Phone: __________

**Platform Support:**
- Railway: https://railway.app/help
- Vercel: https://vercel.com/support

**Escalation:**
- Level 1: __________
- Level 2: __________

---

## Quick Commands

### Railway CLI

```bash
# Install
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Run command in production
railway run <command>

# Download database backup
railway run sqlite3 untangle.db .dump > backup.sql
```

### Vercel CLI

```bash
# Install
npm install -g vercel

# Login
vercel login

# Link to project
vercel link

# View logs
vercel logs

# Deploy
vercel --prod
```

---

## Health Check Endpoints

Test these regularly:

**Backend:**
```bash
curl https://YOUR-BACKEND-URL/health
# Expected: {"status":"healthy","timestamp":"..."}
```

**Frontend:**
```bash
curl -I https://YOUR-FRONTEND-URL
# Expected: HTTP/2 200
```

**API with Auth:**
```bash
# 1. Get token
curl -X POST https://YOUR-BACKEND-URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@untangle.com","password":"password123"}'

# 2. Test authenticated endpoint
curl https://YOUR-BACKEND-URL/api/v1/members \
  -H "Authorization: Bearer YOUR-TOKEN"
```

---

## Backup & Recovery

### Manual Backup Process

**Backend Code:**
```bash
git pull origin main
git tag v1.0.0-backup-YYYYMMDD
git push --tags
```

**Database:**
```bash
railway run sqlite3 untangle.db .dump > backups/backup-YYYYMMDD.sql
```

**Environment Variables:**
```bash
# Railway: Export from dashboard → Settings → Variables
# Vercel: Export from dashboard → Settings → Environment Variables
# Store in secure location (1Password, etc.)
```

### Recovery Process

**Restore Database:**
```bash
railway run sqlite3 untangle.db < backups/backup-YYYYMMDD.sql
```

**Rollback Deployment:**
- Railway: Deployments → Select previous → Redeploy
- Vercel: Deployments → Select previous → Promote to Production

---

## Cost Tracking

### Free Tier Limits

**Railway:**
- $5 credit per month (500 hours)
- 1GB RAM, 1 vCPU
- 1GB storage

**Vercel:**
- 100GB bandwidth per month
- Unlimited deployments
- 100 domains

### Current Usage

| Month | Railway Cost | Vercel Cost | Total | Notes |
|-------|-------------|-------------|-------|-------|
| __________ | $_____ | $_____ | $_____ | |
| __________ | $_____ | $_____ | $_____ | |

### Upgrade Triggers

- Railway: > 80% of free tier used
- Vercel: > 80GB bandwidth used
- Database: > 800MB size
- Concurrent users: > 100

---

## Future Enhancements

### Planned Features

- [ ] Google OAuth integration
- [ ] Dodo Payments integration
- [ ] Email notifications
- [ ] WhatsApp notifications
- [ ] Mobile app
- [ ] Multi-language support

### Infrastructure Improvements

- [ ] Migrate to PostgreSQL (if needed)
- [ ] Set up automated backups
- [ ] Add monitoring (Sentry)
- [ ] Implement rate limiting
- [ ] Add caching (Redis)
- [ ] CDN for static assets

### Security Enhancements

- [ ] 2FA for admin accounts
- [ ] IP whitelisting
- [ ] Audit logging
- [ ] Security headers
- [ ] DDoS protection
- [ ] Regular security audits

---

## Notes

```
[Your deployment notes here]

Date: __________
Deployed by: __________
Issues encountered:

Resolutions:

Next steps:

```

---

**Status:** ✅ Deployed | ⚠️ In Progress | ❌ Not Started

**Last Updated:** __________
