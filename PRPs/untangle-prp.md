# PRP: UNTANGLE

> Implementation blueprint for parallel agent execution

---

## METADATA

| Field | Value |
|-------|-------|
| **Product** | UNTANGLE |
| **Type** | B2B SaaS |
| **Version** | 1.0 |
| **Created** | 2026-01-31 |
| **Complexity** | High |

---

## PRODUCT OVERVIEW

**Description:** UNTANGLE provides a unified admin dashboard that automates membership tracking, gaming session logs, and real-time balance calculations via a centralized Postgres database. The system handles complex credit logic including 180-day rollover periods and 365-day plan expirations, replacing manual spreadsheet tracking with real-time automated calculations.

**Value Proposition:** Eliminates manual spreadsheet errors, automates complex credit rollover logic, provides instant mobile-based member lookup, and enables multi-branch gaming hub management from mobile devices.

**MVP Scope:**
- [x] **Unified Member Lookup** - Mobile number search with instant active/expired status
- [x] **Automated Credit & Expiry Logic** - 180-day rollover + 365-day plan expiry calculations
- [x] **Session Tracking** - Log sessions (Date, Table, Game, Guru) and deduct hours
- [x] **Basic Admin Dashboard** - Mobile-friendly interface with search bar and stat cards
- [x] Member registration and profile management
- [x] Purchase/credit plan assignment
- [x] Real-time balance calculations
- [x] Member history (sessions + purchases)
- [x] Expiration alerts and rollover tracking
- [x] Multi-branch management
- [x] Export reports (CSV/PDF)
- [x] Dodo Payments integration

---

## TECH STACK

| Layer | Technology | Skill Reference |
|-------|------------|-----------------|
| Backend | FastAPI + Python 3.11+ | skills/BACKEND.md |
| Frontend | React + TypeScript + Vite | skills/FRONTEND.md |
| Database | PostgreSQL + SQLAlchemy | skills/DATABASE.md |
| Auth | JWT + bcrypt + Google OAuth | skills/BACKEND.md |
| UI | Tailwind CSS + shadcn/ui | skills/FRONTEND.md |
| Payments | Dodo Payments | skills/BACKEND.md |
| Testing | pytest + Vitest + RTL | skills/TESTING.md |
| Deployment | Docker + GitHub Actions | skills/DEPLOYMENT.md |

---

## DATABASE MODELS

### User Model (Authentication)
**Purpose:** Gaming hub administrators with role-based access
**Fields:**
- id (UUID, PK)
- email (string, unique, indexed)
- hashed_password (string)
- full_name (string)
- role (enum: admin/manager/staff)
- branch_id (FK to Branch, nullable for admins)
- is_active (boolean, default True)
- is_verified (boolean, default False)
- oauth_provider (string, nullable - "google")
- created_at (timestamp)
- updated_at (timestamp)

**Indexes:** email, role, branch_id
**Relationships:** Many-to-One with Branch

---

### RefreshToken Model
**Purpose:** JWT refresh token management
**Fields:**
- id (UUID, PK)
- user_id (FK to User)
- token (string, unique, indexed)
- expires_at (timestamp)
- revoked (boolean, default False)
- created_at (timestamp)

**Indexes:** token, user_id, expires_at
**Relationships:** Many-to-One with User

---

### Member Model
**Purpose:** Gaming hub customers with credit balances
**Fields:**
- id (UUID, PK)
- mobile (string, 10-digit normalized, unique, indexed) **PRIMARY LOOKUP KEY**
- full_name (string)
- email (string, optional)
- current_plan (string, FK to latest Purchase)
- total_hours_granted (decimal, precision 10,2)
- total_hours_used (decimal, precision 10,2)
- balance_hours (decimal, **COMPUTED**: granted - used)
- expiry_date (date, 365 days from last purchase)
- is_expired (boolean, **COMPUTED**: today > expiry_date)
- registration_date (timestamp)
- branch_preferred (FK to Branch, nullable)
- created_at (timestamp)
- updated_at (timestamp)

**Indexes:** mobile (unique), expiry_date, branch_preferred
**Relationships:**
- Many-to-One with Branch
- One-to-Many with Purchase
- One-to-Many with GamingSession

**Computed Properties:**
```python
@hybrid_property
def balance_hours(self) -> Decimal:
    return self.total_hours_granted - self.total_hours_used

@hybrid_property
def is_expired(self) -> bool:
    return date.today() > self.expiry_date if self.expiry_date else False
```

---

### Purchase Model
**Purpose:** Credit/plan purchases with rollover logic
**Fields:**
- id (UUID, PK)
- member_id (FK to Member, indexed)
- mobile (string, denormalized for quick lookup)
- plan_name (string, e.g., "60 Hours Premium")
- amount_paid (decimal, precision 10,2)
- hours_granted (decimal, precision 10,2) - base hours for plan
- total_valid_purchased (decimal, precision 10,2) - including rollover
- purchase_date (timestamp, indexed)
- expiry_date (date, **COMPUTED**: purchase_date + 365 days)
- rollover_deadline (date, **COMPUTED**: expiry_date + 180 days)
- is_expired (boolean, **COMPUTED**: today > expiry_date)
- rollover_status (enum: 'pending', 'applied', 'forfeited', 'not_applicable')
- created_by (FK to User)
- created_at (timestamp)
- updated_at (timestamp)

**Indexes:** member_id, purchase_date, expiry_date
**Relationships:**
- Many-to-One with Member
- Many-to-One with User (created_by)

**Business Logic:**
- On create: `expiry_date = purchase_date + 365 days`
- On create: `rollover_deadline = expiry_date + 180 days`
- On create: Apply 180-day rollover if previous plan exists

---

### GamingSession Model
**Purpose:** Track gaming activity and hour consumption
**Fields:**
- id (UUID, PK)
- member_id (FK to Member, indexed)
- mobile (string, denormalized)
- branch_id (FK to Branch, indexed)
- date (date, indexed)
- time_start (timestamp)
- time_end (timestamp, nullable for active sessions)
- hours_consumed (decimal, precision 10,2, **COMPUTED** on end)
- table_number (string, e.g., "PC-01", "Console-03")
- game_title (string, with auto-suggest)
- guru_assigned (string, staff member name)
- status (enum: 'active', 'completed', 'voided')
- created_by (FK to User)
- created_at (timestamp)
- updated_at (timestamp)

**Indexes:** member_id, branch_id, date, status
**Relationships:**
- Many-to-One with Member
- Many-to-One with Branch
- Many-to-One with User (created_by)

**Business Logic:**
- On end: `hours_consumed = (time_end - time_start) / 3600`
- On end: Deduct hours_consumed from member.total_hours_used
- On void: Refund hours_consumed back to member

---

### Branch Model
**Purpose:** Gaming hub locations
**Fields:**
- id (UUID, PK)
- name (string, unique, e.g., "Downtown", "Mall")
- location (string, address)
- total_stations (integer, number of gaming stations)
- is_active (boolean, default True)
- created_at (timestamp)
- updated_at (timestamp)

**Indexes:** name (unique)
**Relationships:**
- One-to-Many with User
- One-to-Many with Member (preferred)
- One-to-Many with GamingSession

---

## MODULES

### Module 1: Authentication
**Agents:** DATABASE-AGENT + BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/v1/auth/register | Create new admin account (invitation-only) | Public |
| POST | /api/v1/auth/login | Login with email/password, returns JWT | Public |
| POST | /api/v1/auth/google | Initiate Google OAuth flow | Public |
| GET | /api/v1/auth/google/callback | Google OAuth callback | Public |
| POST | /api/v1/auth/refresh | Refresh access token | Public (refresh token) |
| POST | /api/v1/auth/logout | Revoke refresh token | Protected |
| GET | /api/v1/auth/me | Get current user profile | Protected |
| PUT | /api/v1/auth/me | Update user profile | Protected |

**Services:**
- `auth_service.py`: JWT token generation/validation, password hashing, OAuth integration
- `jwt.py`: Token creation, verification, refresh logic
- `oauth.py`: Google OAuth flow handler

**Frontend Pages:**
| Route | Component | Features |
|-------|-----------|----------|
| /login | Login.tsx | Email/password form + Google OAuth button |
| /register | Register.tsx | Registration form (admin invitation only) |
| /forgot-password | ForgotPassword.tsx | Password reset flow |
| /profile | Profile.tsx | User profile settings (protected) |

**Frontend Components:**
- `LoginForm.tsx` - Email/password login
- `GoogleOAuthButton.tsx` - One-click Google sign-in
- `ProtectedRoute.tsx` - Route guard for authentication

---

### Module 2: Members
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/members | List all members (paginated, filterable) | Protected |
| POST | /api/v1/members | Create new member | Protected (manager+) |
| GET | /api/v1/members/search?mobile={number} | **PRIMARY LOOKUP** - Search by mobile | Protected |
| GET | /api/v1/members/{id} | Get member details with full history | Protected |
| PUT | /api/v1/members/{id} | Update member profile | Protected (manager+) |
| DELETE | /api/v1/members/{id} | Deactivate member (soft delete) | Protected (admin only) |
| GET | /api/v1/members/{id}/history | Get purchase and session history | Protected |
| POST | /api/v1/members/{id}/reset-rollover | Manual rollover reset | Protected (admin only) |

**Services:**
- `member_service.py`: Member CRUD, mobile normalization, search logic
- Mobile normalization function (10-digit format)

**Frontend Pages:**
| Route | Component | Features |
|-------|-----------|----------|
| /dashboard | Dashboard.tsx | **PRIMARY PAGE** - Search bar + stats |
| /members | Members.tsx | Member list table (searchable, filterable) |
| /members/new | MemberNew.tsx | Registration form |
| /members/{id} | MemberDetail.tsx | Balance cards + history tables |
| /members/{id}/edit | MemberEdit.tsx | Edit profile form |

**Frontend Components:**
- `MemberSearch.tsx` - **CORE FEATURE** - Mobile number search bar (sticky)
- `BalanceCards.tsx` - Total/Used/Balance visual cards
- `MemberTable.tsx` - Sortable, filterable member list
- `ExpiryAlert.tsx` - Red banner for expired members

---

### Module 3: Credits/Balance
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/purchases | List all purchases (filterable) | Protected |
| POST | /api/v1/purchases | Create new purchase/plan assignment | Protected (manager+) |
| GET | /api/v1/purchases/{id} | Get purchase details | Protected |
| PUT | /api/v1/purchases/{id} | Update purchase (manual correction) | Protected (admin only) |
| GET | /api/v1/members/{id}/balance | **CRITICAL** - Get balance breakdown | Protected |
| GET | /api/v1/members/{id}/rollover-status | Check rollover eligibility | Protected |
| POST | /api/v1/members/{id}/adjust-balance | Manual balance adjustment with audit | Protected (admin only) |
| GET | /api/v1/purchases/expiring-soon | List expiring in 7-30 days | Protected |

**Services:**
- `balance_service.py`: **CORE LOGIC** - 180-day rollover calculation, expiry logic
- `payment_service.py`: Dodo Payments integration, webhook handling

**Critical Business Logic - 180-Day Rollover:**
```python
def apply_rollover(db: Session, member_id: str, new_purchase: Purchase) -> Decimal:
    """
    Apply 180-day rollover when member purchases new plan.

    Rules:
    1. Find previous purchase
    2. Check if previous plan expired < 180 days ago
    3. If yes: rollover = previous.total_valid_purchased - member.total_hours_used
    4. If no: rollover = 0 (forfeited)
    5. new.total_valid_purchased = new.hours_granted + rollover
    """
    previous_purchase = db.query(Purchase).filter(
        Purchase.member_id == member_id
    ).order_by(Purchase.purchase_date.desc()).first()

    if not previous_purchase:
        return new_purchase.hours_granted

    days_since_expiry = (new_purchase.purchase_date - previous_purchase.expiry_date).days

    if days_since_expiry <= 180:
        # Apply rollover
        unused_hours = previous_purchase.total_valid_purchased - member.total_hours_used
        rollover = max(unused_hours, Decimal(0))
        previous_purchase.rollover_status = 'applied'
    else:
        # Forfeit
        rollover = Decimal(0)
        previous_purchase.rollover_status = 'forfeited'

    db.commit()
    return new_purchase.hours_granted + rollover
```

**Frontend Pages:**
| Route | Component | Features |
|-------|-----------|----------|
| /members/{id}/purchases | PurchaseHistory.tsx | Purchase history table |
| /members/{id}/add-credits | AddCredits.tsx | Plan selection + Dodo Payments |
| /reports/expiring | ExpiringReport.tsx | Expiration alerts |

**Frontend Components:**
- `PurchaseTable.tsx` - Chronological purchase history
- `AddCreditsForm.tsx` - Plan selection with Dodo Payments integration
- `RolloverIndicator.tsx` - Visual rollover status badge

---

### Module 4: Gaming Sessions (Track)
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/sessions | List sessions (filterable by branch, date, member) | Protected |
| POST | /api/v1/sessions | Log new gaming session | Protected (staff+) |
| GET | /api/v1/sessions/{id} | Get session details | Protected |
| PUT | /api/v1/sessions/{id} | Edit session (time, table, game, guru) | Protected (manager+) |
| DELETE | /api/v1/sessions/{id} | Void session (refunds hours) | Protected (manager+) |
| POST | /api/v1/sessions/{id}/end | Terminate active session | Protected (staff+) |
| GET | /api/v1/sessions/active | Get all currently active sessions | Protected |
| GET | /api/v1/sessions/recent | Get recent sessions (last 24h) | Protected |
| GET | /api/v1/branches/{id}/occupancy | Real-time station occupancy | Protected |
| GET | /api/v1/games/suggest?q={query} | Auto-suggest game titles | Protected |

**Services:**
- `session_service.py`: Session CRUD, hour calculation, balance deduction logic

**Frontend Pages:**
| Route | Component | Features |
|-------|-----------|----------|
| /track | Track.tsx | **QUICK-ENTRY FORM** - Branch, Table, Game, Guru |
| /sessions | Sessions.tsx | Activity timeline (chronological feed) |
| /sessions/live | LiveSessions.tsx | Venue map with real-time occupancy |
| /sessions/{id} | SessionDetail.tsx | Single session view |

**Frontend Components:**
- `SessionForm.tsx` - **CORE FEATURE** - Quick-entry session form
- `StationMap.tsx` - Live occupancy grid (updates every 5s)
- `ActivityTimeline.tsx` - Chronological session feed
- `GameAutoSuggest.tsx` - Game title autocomplete

---

### Module 5: Dashboard & Reports
**Agents:** BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/dashboard/stats | All dashboard metrics (real-time) | Protected |
| GET | /api/v1/dashboard/occupancy | Live station occupancy | Protected |
| GET | /api/v1/dashboard/recent-activity | Recent purchases + sessions | Protected |
| GET | /api/v1/dashboard/alerts | Expiration and maintenance alerts | Protected |
| GET | /api/v1/dashboard/branch-performance | Per-branch stats | Protected |
| GET | /api/v1/reports/export?type={csv\|pdf} | Export reports | Protected (manager+) |
| GET | /api/v1/branches | List all branches | Protected |
| POST | /api/v1/branches | Create branch | Protected (admin only) |
| PUT | /api/v1/branches/{id} | Update branch | Protected (admin only) |

**Dashboard Metrics (Computed):**
- Total active members
- PC/Console occupancy rate (%)
- Daily active users (DAU)
- Total hours consumed (24h)
- Members expiring soon (7-30 days)
- New sign-ups (current month)
- Average revenue per user (ARPU)
- Net gaming revenue (NGR)

**Frontend Pages:**
| Route | Component | Features |
|-------|-----------|----------|
| /dashboard | Dashboard.tsx | **PRIMARY LANDING PAGE** - Search + Stats + Live Map |
| /analytics | Analytics.tsx | Long-term trends, branch performance |
| /reports | Reports.tsx | Export interface (CSV/PDF) |
| /settings | Settings.tsx | Branch details, user permissions |

**Frontend Components:**
- `StatCards.tsx` - Visual metric cards
- `RecentActivityFeed.tsx` - Latest purchases + sessions
- `AlertCenter.tsx` - High-priority notifications
- `ExportModal.tsx` - Report export with date filters

---

## PHASE EXECUTION PLAN

### Phase 1: Foundation (4 agents in parallel)
**Duration:** ~15-20 minutes

**DATABASE-AGENT:**
- [ ] Create all models (User, RefreshToken, Member, Purchase, GamingSession, Branch)
- [ ] Set up database.py with SQLAlchemy engine
- [ ] Configure alembic for migrations
- [ ] Create initial migration (all tables)
- [ ] Add indexes (mobile, email, purchase_date, etc.)
- [ ] Implement computed properties (balance_hours, is_expired)

**BACKEND-AGENT:**
- [ ] Initialize FastAPI project structure
- [ ] Create main.py with CORS, middleware setup
- [ ] Create config.py with environment variable management
- [ ] Set up dependency injection (get_db, get_current_user)
- [ ] Create base router structure
- [ ] Configure logging

**FRONTEND-AGENT:**
- [ ] Initialize Vite + React + TypeScript project
- [ ] Configure Tailwind CSS + shadcn/ui
- [ ] Set up folder structure (components, pages, hooks, services, context, types)
- [ ] Create base layout components
- [ ] Configure Axios instance with interceptors
- [ ] Set up routing (React Router)

**DEVOPS-AGENT:**
- [ ] Create Dockerfile for backend (Python 3.11)
- [ ] Create Dockerfile for frontend (Node 18)
- [ ] Create docker-compose.yml (PostgreSQL, backend, frontend)
- [ ] Create .env.example files
- [ ] Set up .gitignore
- [ ] Configure GitHub Actions CI/CD (placeholder)

**Validation Gate 1:**
```bash
cd backend && pip install -r requirements.txt
alembic upgrade head
cd ../frontend && npm install
docker-compose config
```

---

### Phase 2: Backend Modules (Sequential, backend-agent)
**Duration:** ~30-40 minutes

**Module Order:**
1. **Authentication** (prerequisite for all others)
   - [ ] models/user.py, models/refresh_token.py
   - [ ] schemas/user.py, schemas/auth.py
   - [ ] auth/jwt.py, auth/oauth.py
   - [ ] services/auth_service.py
   - [ ] routers/auth.py
   - [ ] Test with: `pytest backend/tests/test_auth.py -v`

2. **Members**
   - [ ] models/member.py
   - [ ] schemas/member.py
   - [ ] services/member_service.py (with mobile normalization)
   - [ ] routers/members.py
   - [ ] Test with: `pytest backend/tests/test_members.py -v`

3. **Credits/Balance** ⚠️ **CRITICAL BUSINESS LOGIC**
   - [ ] models/purchase.py
   - [ ] schemas/purchase.py
   - [ ] services/balance_service.py (180-day rollover logic)
   - [ ] services/payment_service.py (Dodo Payments)
   - [ ] routers/purchases.py
   - [ ] Test with: `pytest backend/tests/test_balance_logic.py -v`

4. **Gaming Sessions**
   - [ ] models/session.py, models/branch.py
   - [ ] schemas/session.py, schemas/branch.py
   - [ ] services/session_service.py
   - [ ] routers/sessions.py, routers/branches.py
   - [ ] Test with: `pytest backend/tests/test_sessions.py -v`

5. **Dashboard & Reports**
   - [ ] services/dashboard_service.py
   - [ ] services/report_service.py (CSV/PDF export)
   - [ ] routers/dashboard.py
   - [ ] Test with: `pytest backend/tests/test_dashboard.py -v`

**Validation Gate 2:**
```bash
ruff check backend/
ruff format backend/
mypy backend/app --strict
pytest backend/tests -v --cov=app --cov-fail-under=80
```

---

### Phase 3: Frontend Modules (Sequential, frontend-agent)
**Duration:** ~30-40 minutes

**Module Order:**
1. **Authentication**
   - [ ] types/user.ts, types/api.ts
   - [ ] services/authService.ts
   - [ ] context/AuthContext.tsx
   - [ ] components/ProtectedRoute.tsx
   - [ ] pages/Login.tsx, pages/Register.tsx

2. **Members** ⚠️ **CORE VALUE**
   - [ ] types/member.ts
   - [ ] services/memberService.ts
   - [ ] hooks/useMember.ts
   - [ ] components/MemberSearch.tsx (sticky search bar)
   - [ ] components/BalanceCards.tsx
   - [ ] components/MemberTable.tsx
   - [ ] pages/Dashboard.tsx (PRIMARY PAGE)
   - [ ] pages/Members.tsx, pages/MemberDetail.tsx

3. **Credits/Balance**
   - [ ] types/purchase.ts
   - [ ] hooks/useBalance.ts
   - [ ] components/PurchaseTable.tsx
   - [ ] components/AddCreditsForm.tsx (Dodo Payments integration)
   - [ ] pages/ExpiringReport.tsx

4. **Gaming Sessions**
   - [ ] types/session.ts
   - [ ] services/sessionService.ts
   - [ ] hooks/useSession.ts
   - [ ] components/SessionForm.tsx (quick-entry)
   - [ ] components/StationMap.tsx (live occupancy)
   - [ ] pages/Track.tsx, pages/Sessions.tsx

5. **Dashboard & Reports**
   - [ ] components/StatCards.tsx
   - [ ] components/RecentActivityFeed.tsx
   - [ ] components/AlertCenter.tsx
   - [ ] components/ExportModal.tsx
   - [ ] pages/Analytics.tsx, pages/Reports.tsx, pages/Settings.tsx

**Validation Gate 3:**
```bash
cd frontend
npm run lint
npm run type-check
npm run build
```

---

### Phase 4: Quality & Integration (3 agents in parallel)
**Duration:** ~20-30 minutes

**TEST-AGENT:**
- [ ] Backend unit tests for all services
- [ ] **CRITICAL:** Balance rollover edge case tests
  - Test rollover within 180 days
  - Test rollover after 180 days (forfeiture)
  - Test first-time purchase (no rollover)
  - Test multiple renewals
- [ ] API integration tests
- [ ] Frontend component tests (Vitest + RTL)
- [ ] E2E tests for critical flows (Playwright)
- [ ] Ensure 80%+ code coverage

**REVIEW-AGENT:**
- [ ] Security audit:
  - RBAC implementation review
  - SQL injection prevention check
  - XSS vulnerability scan
  - CSRF protection verification (OAuth)
  - Rate limiting on auth endpoints
  - Audit trail for balance adjustments
- [ ] Performance review:
  - Member lookup < 500ms
  - Balance calculation < 1s
  - Database query optimization
  - Index usage verification
- [ ] Code quality audit:
  - Type safety (TypeScript strict mode)
  - Error handling completeness
  - Logging implementation
  - Documentation quality

**DEVOPS-AGENT:**
- [ ] Finalize docker-compose.yml
- [ ] Create production Dockerfiles (multi-stage)
- [ ] Set up environment variable templates
- [ ] Configure GitHub Actions workflows:
  - Backend CI (lint, test, build)
  - Frontend CI (lint, type-check, build)
  - Docker image builds
- [ ] Create deployment documentation

**Final Validation:**
```bash
# Full integration test
docker-compose up -d
sleep 10
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/dashboard/stats

# Run full test suite
docker-compose exec backend pytest -v --cov=app --cov-fail-under=80
docker-compose exec frontend npm test

# Verify builds
docker-compose build
```

---

## VALIDATION GATES

| Gate | Purpose | Commands |
|------|---------|----------|
| **Gate 1: Foundation** | Verify project scaffolding | `pip install -r requirements.txt`<br>`alembic upgrade head`<br>`npm install`<br>`docker-compose config` |
| **Gate 2: Backend** | Verify API quality | `ruff check backend/`<br>`mypy backend/app --strict`<br>`pytest --cov-fail-under=80` |
| **Gate 3: Frontend** | Verify UI quality | `npm run lint`<br>`npm run type-check`<br>`npm run build` |
| **Gate Final: Integration** | Verify full system | `docker-compose up -d`<br>`curl localhost:8000/health`<br>`docker-compose exec backend pytest`<br>`docker-compose exec frontend npm test` |

---

## CRITICAL BUSINESS LOGIC TESTS

### 180-Day Rollover Tests (MUST PASS)

```python
# Test Case 1: Rollover within 180 days
def test_rollover_within_180_days(db_session):
    """Test that unused hours rollover when renewed within 180 days."""
    # Setup
    member = create_member(mobile="9171234567")
    purchase1 = create_purchase(member, plan="60 Hours", hours=60, date="2025-01-01")
    create_sessions(member, hours_consumed=30)  # Use 30 hours

    # Purchase new plan 100 days after expiry (within 180-day window)
    purchase2 = create_purchase(member, plan="60 Hours", hours=60, date="2026-04-11")

    # Assert
    assert purchase2.total_valid_purchased == 90  # 60 new + 30 rollover
    assert purchase1.rollover_status == 'applied'
    assert member.balance_hours == 60  # 90 total - 30 used

# Test Case 2: Rollover after 180 days (forfeiture)
def test_rollover_after_180_days(db_session):
    """Test that unused hours forfeit after 180 days."""
    # Setup
    member = create_member(mobile="9171234567")
    purchase1 = create_purchase(member, plan="60 Hours", hours=60, date="2025-01-01")
    create_sessions(member, hours_consumed=30)  # Use 30 hours

    # Purchase new plan 200 days after expiry (beyond 180-day window)
    purchase2 = create_purchase(member, plan="60 Hours", hours=60, date="2026-07-20")

    # Assert
    assert purchase2.total_valid_purchased == 60  # 60 new only, 30 forfeited
    assert purchase1.rollover_status == 'forfeited'
    assert member.balance_hours == 30  # 60 total - 30 used (previous 30 lost)

# Test Case 3: First-time purchase (no rollover)
def test_first_purchase_no_rollover(db_session):
    """Test that first purchase has no rollover."""
    member = create_member(mobile="9171234567")
    purchase = create_purchase(member, plan="60 Hours", hours=60)

    assert purchase.total_valid_purchased == 60
    assert purchase.rollover_status == 'not_applicable'
    assert member.balance_hours == 60

# Test Case 4: Session deduction
def test_session_deducts_hours(db_session):
    """Test that ending a session deducts hours from balance."""
    member = create_member(mobile="9171234567")
    create_purchase(member, plan="60 Hours", hours=60)

    session = create_session(member, time_start="2026-01-01 14:00")
    end_session(session, time_end="2026-01-01 16:30")  # 2.5 hours

    assert session.hours_consumed == 2.5
    assert member.total_hours_used == 2.5
    assert member.balance_hours == 57.5

# Test Case 5: Voided session refund
def test_void_session_refunds_hours(db_session):
    """Test that voiding a session refunds hours."""
    member = create_member(mobile="9171234567")
    create_purchase(member, plan="60 Hours", hours=60)

    session = create_session(member)
    end_session(session, hours_consumed=5)
    assert member.balance_hours == 55

    void_session(session)
    assert session.status == 'voided'
    assert member.balance_hours == 60  # Refunded
```

---

## ENVIRONMENT VARIABLES

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/untangle

# Auth
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Dodo Payments
DODO_API_KEY=your-dodo-api-key
DODO_WEBHOOK_SECRET=your-webhook-secret
DODO_BASE_URL=https://api.dodopayments.com/v1

# App Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
VITE_ENVIRONMENT=development
```

---

## PERFORMANCE REQUIREMENTS

| Metric | Target | Validation |
|--------|--------|------------|
| Member lookup by mobile | < 500ms | Load test with 10k members |
| Balance calculation | < 1s | Test with 1000+ transactions |
| Dashboard load time | < 2s | Lighthouse performance score > 90 |
| Session creation | < 300ms | API response time check |
| Real-time occupancy update | Every 5 seconds | WebSocket or polling implementation |
| Database query optimization | All queries < 100ms | pg_stat_statements analysis |
| Concurrent users | 100+ simultaneous | Load test with k6 or Locust |

---

## SECURITY REQUIREMENTS

| Requirement | Implementation | Validation |
|-------------|----------------|------------|
| Rate limiting on auth | 10 req/min per IP | Test with curl loop |
| Input validation | Pydantic schemas on all endpoints | Fuzzing test |
| Mobile normalization | 10-digit format enforced | Test with various formats |
| SQL injection prevention | SQLAlchemy ORM only | OWASP ZAP scan |
| XSS prevention | React auto-escape + DOMPurify | Manual input testing |
| CSRF for OAuth | State parameter validation | OAuth flow testing |
| Audit trail | All balance adjustments logged | Check audit log table |
| RBAC | Middleware on protected routes | Role-based access test |
| Password hashing | bcrypt cost factor 12 | Verify hash format |
| HTTPS in production | Enforce SSL | Check deployment config |

---

## AGENT ASSIGNMENTS

| Agent | Tasks | Skill Files | Output Files |
|-------|-------|-------------|--------------|
| **DATABASE-AGENT** | All models, migrations | skills/DATABASE.md | backend/app/models/*.py<br>backend/alembic/versions/*.py |
| **BACKEND-AGENT** | All API endpoints, services | skills/BACKEND.md | backend/app/routers/*.py<br>backend/app/services/*.py<br>backend/app/schemas/*.py |
| **FRONTEND-AGENT** | All UI pages, components | skills/FRONTEND.md | frontend/src/pages/*.tsx<br>frontend/src/components/*.tsx<br>frontend/src/hooks/*.ts |
| **TEST-AGENT** | All tests (unit, integration, E2E) | skills/TESTING.md | backend/tests/*.py<br>frontend/src/**/*.test.tsx |
| **REVIEW-AGENT** | Security, performance, quality audit | N/A | Review report |
| **DEVOPS-AGENT** | Docker, CI/CD, deployment | skills/DEPLOYMENT.md | Dockerfile<br>docker-compose.yml<br>.github/workflows/*.yml |

---

## SUCCESS CRITERIA

### Must Have (MVP Completion)
- [x] Admin can login with email/password and Google OAuth
- [x] Admin can search member by mobile number instantly (< 500ms)
- [x] System correctly calculates 180-day rollover
- [x] System correctly calculates 365-day plan expiry
- [x] Admin can log gaming sessions and deduct hours
- [x] Dashboard displays real-time stats and occupancy
- [x] Admin can export reports to CSV/PDF
- [x] Multi-branch management works correctly
- [x] Dodo Payments integration processes payments
- [x] All tests pass (80%+ coverage)
- [x] Docker builds and runs successfully
- [x] Mobile-optimized UI works on smartphones

### Quality Gates
- [x] Backend test coverage ≥ 80%
- [x] Frontend TypeScript strict mode passes
- [x] All API endpoints documented in OpenAPI/Swagger
- [x] Performance targets met (member lookup < 500ms)
- [x] Security audit passed
- [x] No critical vulnerabilities (OWASP scan)

---

## NEXT STEP

Execute this PRP with parallel agents:

```bash
/execute-prp PRPs/untangle-prp.md
```

The ORCHESTRATOR will coordinate all agents to build UNTANGLE from scratch.
