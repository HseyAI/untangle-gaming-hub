# INITIAL.md - UNTANGLE Product Definition

> Unified admin dashboard that automates membership tracking, gaming session logs, and real-time balance calculations for gaming hubs.

---

## PRODUCT

### Name
UNTANGLE

### Description
UNTANGLE provides a unified admin dashboard that automates membership tracking, gaming session logs, and real-time balance calculations via a centralized Postgres database. The system handles complex credit logic including 180-day rollover periods and 365-day plan expirations, replacing manual spreadsheet tracking with real-time automated calculations.

### Target User
Administrators and managers of gaming hubs or membership-based clubs who need to track user credits, session history, and manage multi-branch operations from mobile devices.

### Type
- [x] B2B SaaS (Software as a Service)

---

## TECH STACK

### Backend
- [x] FastAPI + Python 3.11+

### Frontend
- [x] React + Vite + TypeScript

### Database
- [x] PostgreSQL + SQLAlchemy

### Authentication
- [x] JWT + Email/Password + Google OAuth

### UI Framework
- [x] Tailwind CSS + shadcn/ui

### Payments
- [x] Dodo Payments

---

## MODULES

### Module 1: Authentication (Required)

**Description:** User authentication and authorization for gaming hub administrators

**Models:**
- **User**: id, email, hashed_password, full_name, role (admin/manager/staff), branch_id, is_active, is_verified, oauth_provider, created_at, updated_at
- **RefreshToken**: id, user_id, token, expires_at, revoked, created_at

**API Endpoints:**
- POST /api/v1/auth/register - Create new admin account
- POST /api/v1/auth/login - Login with email/password
- POST /api/v1/auth/google - Login with Google OAuth
- POST /api/v1/auth/refresh - Refresh access token
- POST /api/v1/auth/logout - Revoke refresh token
- GET /api/v1/auth/me - Get current user profile
- PUT /api/v1/auth/me - Update profile

**Frontend Pages:**
- /login - Login page (email/password + Google OAuth button)
- /register - Registration page (admin invitation only)
- /forgot-password - Password reset page
- /profile - User profile settings (protected)

---

### Module 2: Members

**Description:** Centralizes the management of gaming hub customers by linking their profiles directly to their mobile numbers in the Postgres database.

**Models:**
- **Member**:
  - id (UUID primary key)
  - mobile (string, normalized 10-digit, unique index)
  - full_name (string)
  - email (string, optional)
  - current_plan (string, FK to latest purchase)
  - total_hours_granted (decimal, with 180-day rollover)
  - total_hours_used (decimal, sum of all sessions)
  - balance_hours (decimal, computed: total_hours_granted - total_hours_used)
  - expiry_date (date, 365 days from last purchase)
  - is_expired (boolean, computed)
  - registration_date (datetime)
  - branch_preferred (FK to Branch)
  - created_at, updated_at

**API Endpoints:**
- GET /api/v1/members - List all members (paginated, filterable)
- POST /api/v1/members - Create new member
- GET /api/v1/members/search?mobile={number} - Search by mobile (primary lookup)
- GET /api/v1/members/{id} - Get member details with full history
- PUT /api/v1/members/{id} - Update member profile
- DELETE /api/v1/members/{id} - Deactivate member
- GET /api/v1/members/{id}/history - Get purchase and session history
- POST /api/v1/members/{id}/reset-rollover - Manual rollover reset (admin only)

**Frontend Pages:**
- /dashboard - Landing page with search bar and stats
- /members - Member list table (searchable, filterable)
- /members/new - Registration form for new members
- /members/{id} - Member detail view (Total/Used/Balance cards + history)
- /members/{id}/edit - Edit member profile form

---

### Module 3: Credits/Balance

**Description:** Automates real-time calculations of membership hours, handling complex logic like the 180-day rollover for new purchases and the 365-day plan expiration.

**Models:**
- **Purchase**:
  - id (UUID)
  - member_id (FK to Member, indexed)
  - mobile (string, denormalized for quick lookup)
  - plan_name (string, e.g., "60 Hours Premium")
  - amount_paid (decimal)
  - hours_granted (decimal, base hours for the plan)
  - total_valid_purchased (decimal, cumulative including rollover)
  - purchase_date (datetime, indexed)
  - expiry_date (date, calculated as purchase_date + 365 days)
  - rollover_deadline (date, expiry_date + 180 days)
  - is_expired (boolean, computed)
  - rollover_status (enum: 'pending', 'applied', 'forfeited', 'not_applicable')
  - created_by (FK to User)
  - created_at, updated_at

**API Endpoints:**
- GET /api/v1/purchases - List all purchases (filterable by member, date range)
- POST /api/v1/purchases - Create new purchase/plan assignment
- GET /api/v1/purchases/{id} - Get purchase details
- PUT /api/v1/purchases/{id} - Update purchase (manual correction)
- GET /api/v1/members/{id}/balance - Get balance calculation breakdown
- GET /api/v1/members/{id}/rollover-status - Check rollover eligibility
- POST /api/v1/members/{id}/adjust-balance - Manual balance adjustment (admin)
- GET /api/v1/purchases/expiring-soon - List purchases expiring in next 7-30 days

**Frontend Pages:**
- /members/{id} - Balance summary cards (part of member detail)
- /members/{id}/purchases - Purchase history table
- /members/{id}/add-credits - Add credits/plan form (modal or page)
- /reports/expiring - Expiration alerts and rollover tracking

---

### Module 4: Gaming Sessions (Track)

**Description:** Powers the activity log by tracking consumed hours across different branches, allowing admins to see exactly when and where credits were used.

**Models:**
- **GamingSession**:
  - id (UUID)
  - member_id (FK to Member, indexed)
  - mobile (string, denormalized)
  - branch_id (FK to Branch)
  - date (date, indexed)
  - time_start (datetime)
  - time_end (datetime, nullable for active sessions)
  - hours_consumed (decimal, calculated on session end)
  - table_number (string, e.g., "PC-01", "Console-03")
  - game_title (string, with auto-suggest)
  - guru_assigned (string, staff member name)
  - status (enum: 'active', 'completed', 'voided')
  - created_by (FK to User)
  - created_at, updated_at

- **Branch**:
  - id (UUID)
  - name (string, e.g., "Downtown", "Mall")
  - location (string)
  - total_stations (integer)
  - is_active (boolean)
  - created_at, updated_at

**API Endpoints:**
- GET /api/v1/sessions - List all sessions (filterable by branch, date, member)
- POST /api/v1/sessions - Log new gaming session
- GET /api/v1/sessions/{id} - Get session details
- PUT /api/v1/sessions/{id} - Edit session (time, table, game, guru)
- DELETE /api/v1/sessions/{id} - Void session (soft delete)
- POST /api/v1/sessions/{id}/end - Terminate active session
- GET /api/v1/sessions/active - Get all currently active sessions
- GET /api/v1/sessions/recent - Get recent sessions (last 24h)
- GET /api/v1/branches/{id}/occupancy - Get real-time station occupancy
- GET /api/v1/games/suggest?q={query} - Auto-suggest game titles

**Frontend Pages:**
- /track - Session tracking tab with quick-entry form
- /sessions - Activity timeline (chronological feed)
- /sessions/live - Venue map showing real-time station occupancy
- /sessions/{id} - Session detail view
- /games - Games library management (post-MVP)

---

### Module 5: Dashboard

**Description:** Provides a mobile-optimized overview featuring the "Member Lookup" search, visual stats for hour balances, and a chronological history of all transactions and logs.

**Models:**
- **DashboardStats** (computed, no table):
  - Total active members
  - PC/Console occupancy rate
  - Daily active users (DAU)
  - Total hours consumed (24h)
  - Members expiring soon (7-30 days)
  - New sign-ups (current month)
  - Average revenue per user (ARPU)
  - Net gaming revenue (NGR)

**API Endpoints:**
- GET /api/v1/dashboard/stats - Get all dashboard metrics
- GET /api/v1/dashboard/occupancy - Get live station occupancy
- GET /api/v1/dashboard/recent-activity - Get recent purchases and sessions
- GET /api/v1/dashboard/alerts - Get expiration and maintenance alerts
- GET /api/v1/dashboard/branch-performance - Get per-branch stats
- GET /api/v1/reports/export?type={csv|pdf} - Export reports

**Frontend Pages:**
- /dashboard - Main home (search bar + quick stats grid + live session map)
- /analytics - Long-term trends and branch performance
- /reports - Export interface for session logs and financial reports
- /settings - Branch details, user permissions, notification preferences
- /calendar - Event scheduling and reservations (post-MVP)

---

## MVP SCOPE

### Must Have (MVP)
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

### Nice to Have (Post-MVP)
- [ ] Games Library - Full management system for adding/editing games (start with dropdown)
- [ ] Calendar/Bookings - Advanced event scheduling (start with manual logging)
- [ ] Email Notifications - Automated alerts for expiring memberships
- [ ] File Uploads - Member profile pictures
- [ ] SMS Notifications - Mobile alerts for session start/end
- [ ] Mobile App - Native iOS/Android app for admins
- [ ] Advanced Analytics - Predictive churn analysis, revenue forecasting

---

## ACCEPTANCE CRITERIA

### Authentication
- [ ] Admin can register with email/password (invitation-only)
- [ ] Admin can login with email/password
- [ ] Admin can login with Google OAuth
- [ ] JWT tokens work correctly with refresh mechanism
- [ ] Protected routes redirect to login
- [ ] Role-based access control (admin vs. manager vs. staff)

### Members Module
- [ ] Admin can search member by mobile number instantly
- [ ] Search returns real-time balance and expiration status
- [ ] Admin can create new member profile
- [ ] Admin can update member contact information
- [ ] Admin can view full purchase and session history
- [ ] Member list shows current balance and expiry at a glance
- [ ] System correctly calculates balance_hours (granted - used)
- [ ] System correctly identifies is_expired status

### Credits/Balance Module
- [ ] Admin can assign new plan to member
- [ ] Purchase triggers automatic expiry_date calculation (365 days)
- [ ] System applies 180-day rollover when member renews within window
- [ ] System forfeits unused hours after rollover_deadline
- [ ] Balance audit shows step-by-step calculation breakdown
- [ ] Admin can manually adjust credits with audit trail
- [ ] Expiration alerts show members expiring in next 7-30 days
- [ ] Rollover status correctly reflects 'pending', 'applied', 'forfeited'

### Gaming Sessions Module
- [ ] Admin can log new session with all required fields
- [ ] Session deducts hours_consumed from member balance
- [ ] Admin can edit active or past sessions
- [ ] Admin can void accidental session logs
- [ ] Live dashboard shows real-time station occupancy
- [ ] Activity timeline displays chronological session feed
- [ ] Sessions are filterable by branch, date range, member
- [ ] Game title field has auto-suggest functionality

### Dashboard Module
- [ ] Member lookup search bar is prominently displayed
- [ ] Quick stats cards show Total/Used/Balance hours
- [ ] Live session map displays PC/Console occupancy
- [ ] Recent activity feed shows latest purchases and sessions
- [ ] Alert center highlights expired memberships
- [ ] Branch performance metrics are accurate
- [ ] Dashboard is fully responsive and mobile-optimized

### Multi-Branch Management
- [ ] Admin can create and manage multiple branch locations
- [ ] Sessions are correctly attributed to specific branches
- [ ] Dashboard shows per-branch occupancy and stats
- [ ] Reports can be filtered by branch

### Export Reports
- [ ] Admin can export session logs to CSV
- [ ] Admin can export financial reports to PDF
- [ ] Exports include filterable date ranges
- [ ] Exports respect branch filtering

### Payments (Dodo Payments)
- [ ] Admin can record payment via Dodo Payments
- [ ] Payment success triggers credit/plan assignment
- [ ] Payment history is linked to purchases
- [ ] Webhook handles payment status updates

### Quality
- [ ] All API endpoints documented in OpenAPI/Swagger
- [ ] Backend test coverage 80%+
- [ ] Frontend TypeScript strict mode passes
- [ ] Docker builds and runs successfully
- [ ] Mobile-optimized UI works on smartphones
- [ ] Performance: Member lookup < 500ms
- [ ] Performance: Balance calculation < 1s

---

## SPECIAL REQUIREMENTS

### Security
- [x] Rate limiting on auth endpoints
- [x] Input validation on all endpoints (especially mobile number normalization)
- [x] SQL injection prevention via ORM
- [x] XSS prevention in frontend
- [x] CSRF protection for OAuth flows
- [x] Audit trail for all credit adjustments and manual overrides
- [x] Role-based access control (RBAC) for admin actions

### Business Logic
- [x] **180-day Rollover**: When a member purchases a new plan, unused hours from the previous plan are rolled over ONLY if the previous plan expired less than 180 days ago
- [x] **365-day Expiry**: Every plan expires exactly 365 days from purchase_date
- [x] **Real-time Balance**: balance_hours = total_hours_granted - total_hours_used (computed on every request)
- [x] **Mobile Number Normalization**: All mobile numbers stored as 10-digit strings without country code
- [x] **Session Hour Deduction**: hours_consumed automatically deducted from member balance on session end

### Integrations
- [x] Dodo Payments for payment processing
- [ ] Email service for notifications (post-MVP)
- [ ] SMS service for mobile alerts (post-MVP)

### Performance
- [x] Member lookup by mobile number must be < 500ms
- [x] Balance calculation must be < 1s even with 1000+ transactions
- [x] Support up to 10,000 active members per gaming hub
- [x] Real-time occupancy updates every 5 seconds

---

## AGENTS

> These 6 agents will build your product in parallel:

| Agent | Role | Works On |
|-------|------|----------|
| DATABASE-AGENT | Creates all models and migrations | Member, Purchase, GamingSession, Branch, User, RefreshToken models |
| BACKEND-AGENT | Builds API endpoints and services | All module backends + complex rollover/expiry logic |
| FRONTEND-AGENT | Creates UI pages and components | Dashboard, Members, Sessions, Reports pages |
| DEVOPS-AGENT | Sets up Docker, CI/CD, environments | Docker Compose, PostgreSQL, FastAPI + React deployment |
| TEST-AGENT | Writes unit and integration tests | Business logic tests (rollover, expiry calculations) |
| REVIEW-AGENT | Security and code quality audit | Security review (RBAC, audit trails), performance optimization |

---

## READY?

Run this command to generate your Project Requirements Plan:

```bash
/generate-prp INITIAL.md
```

Then execute the plan with:

```bash
/execute-prp PRPs/untangle-prp.md
```
