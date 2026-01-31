# UNTANGLE - Gaming Hub Membership Tracking System

> Unified admin dashboard that automates membership tracking, gaming session logs, and real-time balance calculations for gaming hubs.

## 🎯 Overview

**UNTANGLE** eliminates manual spreadsheet errors by automating complex credit logic including:
- **180-day Rollover**: Unused hours carry over if renewed within 180 days
- **365-day Expiry**: Every plan expires exactly 1 year from purchase
- **Mobile-based Lookup**: Instant member search by 10-digit mobile number (< 500ms)
- **Real-time Balance**: Automatic calculation of granted - used hours
- **Multi-branch Management**: Track sessions across multiple gaming hub locations

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI + Python 3.11+ + PostgreSQL + SQLAlchemy
- **Frontend**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Auth**: JWT + bcrypt + Google OAuth
- **Payments**: Dodo Payments
- **Deployment**: Docker + Docker Compose

### Database Models
1. **User** - Administrators with RBAC (admin/manager/staff)
2. **RefreshToken** - JWT refresh token management
3. **Member** - Gaming hub customers with credit balances
4. **Purchase** - Credit/plan transactions with rollover logic
5. **GamingSession** - Activity logs for hour tracking
6. **Branch** - Gaming hub locations

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### Option 1: Docker (Recommended)

```bash
# Clone and navigate
cd my-saas

# Copy environment file
cp .env.example .env

# Edit .env with your values
nano .env

# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Check logs
docker-compose -f docker-compose.dev.yml logs -f

# Access services
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Run server
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

## 📋 API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Create admin account
- `POST /login` - Login with email/password
- `POST /google` - Google OAuth
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user

### Members (`/api/v1/members`)
- `GET /` - List all members
- `POST /` - Create member
- `GET /search?mobile={number}` - **PRIMARY** - Search by mobile
- `GET /{id}` - Get member details + history
- `PUT /{id}` - Update member
- `GET /{id}/balance` - Get balance breakdown

### Purchases/Credits (`/api/v1/purchases`)
- `POST /` - Assign plan (triggers rollover logic)
- `GET /expiring-soon` - Members expiring in 7-30 days
- `POST /members/{id}/adjust-balance` - Manual adjustment (admin only)

### Gaming Sessions (`/api/v1/sessions`)
- `POST /` - Log new session
- `POST /{id}/end` - End active session (deducts hours)
- `DELETE /{id}` - Void session (refunds hours)
- `GET /active` - All active sessions
- `GET /branches/{id}/occupancy` - Real-time station occupancy

### Dashboard (`/api/v1/dashboard`)
- `GET /stats` - All metrics (real-time)
- `GET /reports/export?type=csv|pdf` - Export reports

## 🔑 Environment Variables

See `.env.example` for all required variables:

### Required
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret (change in production!)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - Google OAuth
- `DODO_API_KEY` - Dodo Payments API key

### Optional
- `ENVIRONMENT` - development/production
- `LOG_LEVEL` - INFO/DEBUG/WARNING
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Default: 30
- `REFRESH_TOKEN_EXPIRE_DAYS` - Default: 7

## 💡 Key Features

### 180-Day Rollover Logic
When a member purchases a new plan:
1. Find their previous purchase
2. Check if it expired < 180 days ago
3. If yes: Rollover unused hours (previous total - used)
4. If no: Forfeit unused hours
5. Set `total_valid_purchased = new hours + rollover`

### Mobile Number Normalization
All mobile numbers are normalized to 10-digit format:
- `+639171234567` → `9171234567`
- `09171234567` → `9171234567`
- `9171234567` → `9171234567`

### Real-time Balance
`balance_hours` is computed in real-time:
```python
@hybrid_property
def balance_hours(self) -> Decimal:
    return self.total_hours_granted - self.total_hours_used
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest -v --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## 📦 Project Structure

```
my-saas/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas (Phase 2)
│   │   ├── routers/         # API endpoints (Phase 2)
│   │   ├── services/        # Business logic (Phase 2)
│   │   ├── auth/            # JWT & OAuth (Phase 2)
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Settings
│   │   ├── database.py      # DB session
│   │   └── utils.py         # Utilities
│   ├── alembic/             # Migrations
│   ├── tests/               # Tests (Phase 4)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/      # React components (Phase 3)
│       ├── pages/           # Pages (Phase 3)
│       ├── hooks/           # Custom hooks (Phase 3)
│       ├── services/        # API calls (Phase 3)
│       └── types/           # TypeScript types (Phase 3)
├── docker-compose.yml
├── docker-compose.dev.yml
└── .env.example
```

## 🔐 Security

- ✅ Rate limiting on auth endpoints (10 req/min)
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (React auto-escapes)
- ✅ CSRF protection (OAuth state parameter)
- ✅ Password hashing (bcrypt, cost factor 12)
- ✅ Audit trail for balance adjustments
- ✅ RBAC (admin/manager/staff roles)

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| Member lookup by mobile | < 500ms |
| Balance calculation | < 1s |
| Dashboard load | < 2s |
| Session creation | < 300ms |
| Concurrent users | 100+ |

## 📝 Development Status

### ✅ Phase 1: Foundation (COMPLETE)
- [x] Database models (8 models)
- [x] FastAPI app structure
- [x] SQLite database setup
- [x] Alembic migrations
- [x] Environment setup

### ✅ Phase 2: Backend Modules (COMPLETE)
- [x] Authentication endpoints + JWT (5 endpoints)
- [x] Members CRUD + mobile search (8 endpoints)
- [x] Purchase/credit assignment + rollover logic (10 endpoints)
- [x] Gaming session tracking (12 endpoints)
- [x] Dashboard stats + reports (7 endpoints)

### ✅ Phase 3: Frontend (COMPLETE)
- [x] Auth pages (login with JWT)
- [x] Dashboard with real-time stats
- [x] Member management pages
- [x] Purchase tracking interface
- [x] Session monitoring interface
- [x] Responsive Tailwind UI

### 🚀 Phase 4: Deployment (READY)
- [x] Deployment configuration (Railway + Vercel)
- [x] Production environment setup
- [x] Seed data for testing
- [ ] Production deployment
- [ ] Live testing

### ⏳ Phase 5: Quality (PLANNED)
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] Security audit
- [ ] Performance optimization

## 🚀 Production Deployment

**MVP is complete and ready for deployment!**

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for comprehensive guide on deploying to production:
- **Backend:** Railway (free tier) - https://railway.app
- **Frontend:** Vercel (free tier) - https://vercel.com

Deployment takes ~15 minutes and requires only a GitHub account.

**Quick Deploy:**
1. Push code to GitHub
2. Connect Railway to repository (backend deployment)
3. Connect Vercel to repository (frontend deployment)
4. Set environment variables
5. Test at your production URLs

## 🤝 Contributing

This is an MVP built with Claude Code. Development phases complete:

1. ✅ Phase 1: Database & Foundation
2. ✅ Phase 2: Backend API (42 endpoints)
3. ✅ Phase 3: Frontend UI (5 pages, 20 components)

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

For issues or questions:
- Check API docs: http://localhost:8000/docs
- Review PRP: `PRPs/untangle-prp.md`
- Check CLAUDE.md for project rules
