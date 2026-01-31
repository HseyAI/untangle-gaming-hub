# CLAUDE.md - UNTANGLE Project Rules

> Project-specific rules for Claude Code. This file is read automatically.

---

## Project Overview

**Project Name:** UNTANGLE
**Description:** Unified admin dashboard that automates membership tracking, gaming session logs, and real-time balance calculations for gaming hubs.

**Tech Stack:**
- Backend: FastAPI + Python 3.11+
- Frontend: React + Vite + TypeScript
- Database: PostgreSQL + SQLAlchemy
- Auth: JWT + Email/Password + Google OAuth
- UI: Tailwind CSS + shadcn/ui
- Payments: Dodo Payments

---

## Project Structure

```
untangle/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings and env vars
│   │   ├── database.py          # DB connection and session
│   │   ├── models/
│   │   │   ├── user.py          # User, RefreshToken
│   │   │   ├── member.py        # Member (gaming hub customers)
│   │   │   ├── purchase.py      # Purchase (credit/plan transactions)
│   │   │   ├── session.py       # GamingSession (activity logs)
│   │   │   └── branch.py        # Branch (locations)
│   │   ├── schemas/
│   │   │   ├── user.py          # Pydantic schemas for User
│   │   │   ├── member.py        # Pydantic schemas for Member
│   │   │   ├── purchase.py      # Pydantic schemas for Purchase
│   │   │   ├── session.py       # Pydantic schemas for GamingSession
│   │   │   └── branch.py        # Pydantic schemas for Branch
│   │   ├── routers/
│   │   │   ├── auth.py          # /auth endpoints
│   │   │   ├── members.py       # /members endpoints
│   │   │   ├── purchases.py     # /purchases endpoints
│   │   │   ├── sessions.py      # /sessions endpoints
│   │   │   ├── dashboard.py     # /dashboard endpoints
│   │   │   └── branches.py      # /branches endpoints
│   │   ├── services/
│   │   │   ├── member_service.py      # Member business logic
│   │   │   ├── balance_service.py     # Balance & rollover calculations
│   │   │   ├── session_service.py     # Session tracking logic
│   │   │   └── payment_service.py     # Dodo Payments integration
│   │   └── auth/
│   │       ├── jwt.py           # JWT token handling
│   │       └── oauth.py         # Google OAuth flow
│   ├── alembic/
│   │   └── versions/            # Database migrations
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_members.py
│   │   ├── test_balance_logic.py  # Critical: test 180-day rollover
│   │   ├── test_sessions.py
│   │   └── conftest.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MemberSearch.tsx       # Global search bar
│   │   │   ├── BalanceCards.tsx       # Total/Used/Balance cards
│   │   │   ├── SessionForm.tsx        # Quick-entry session form
│   │   │   ├── StationMap.tsx         # Live occupancy grid
│   │   │   └── ExpiryAlert.tsx        # Expiration warnings
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx          # Main landing page
│   │   │   ├── Members.tsx            # Member list
│   │   │   ├── MemberDetail.tsx       # Single member view
│   │   │   ├── Track.tsx              # Session tracking tab
│   │   │   ├── Sessions.tsx           # Activity timeline
│   │   │   ├── Analytics.tsx          # Reports and trends
│   │   │   ├── Login.tsx              # Auth pages
│   │   │   └── Settings.tsx           # Branch/user settings
│   │   ├── hooks/
│   │   │   ├── useMember.ts           # Member CRUD hooks
│   │   │   ├── useBalance.ts          # Balance calculations
│   │   │   └── useSession.ts          # Session tracking
│   │   ├── services/
│   │   │   ├── api.ts                 # Axios instance
│   │   │   ├── memberService.ts       # Member API calls
│   │   │   ├── sessionService.ts      # Session API calls
│   │   │   └── authService.ts         # Auth API calls
│   │   ├── context/
│   │   │   └── AuthContext.tsx        # Auth state management
│   │   └── types/
│   │       ├── member.ts              # Member types
│   │       ├── purchase.ts            # Purchase types
│   │       ├── session.ts             # Session types
│   │       └── api.ts                 # API response types
│   └── package.json
├── skills/
│   ├── BACKEND.md                     # Backend development guide
│   ├── FRONTEND.md                    # Frontend development guide
│   ├── DATABASE.md                    # Database modeling guide
│   ├── TESTING.md                     # Testing guide
│   └── DEPLOYMENT.md                  # Docker and deployment
├── agents/
│   ├── DATABASE-AGENT.md
│   ├── BACKEND-AGENT.md
│   ├── FRONTEND-AGENT.md
│   ├── TEST-AGENT.md
│   ├── REVIEW-AGENT.md
│   └── DEVOPS-AGENT.md
├── .claude/
│   └── commands/
│       ├── generate-prp.md
│       └── execute-prp.md
└── PRPs/
    └── untangle-prp.md                # Generated PRP
```

---

## Code Standards

### Python (Backend)

```python
# ALWAYS use type hints
from typing import Optional
from decimal import Decimal
from datetime import date, datetime

def get_member(db: Session, member_id: str) -> Optional[Member]:
    """Fetch a member by ID."""
    return db.query(Member).filter(Member.id == member_id).first()

# ALWAYS add docstrings for public functions
def calculate_balance(
    db: Session,
    member_id: str
) -> Decimal:
    """
    Calculate real-time balance for a member.

    Formula: total_hours_granted - total_hours_used

    Args:
        db: Database session
        member_id: Member UUID

    Returns:
        Current balance in hours (Decimal)
    """
    member = get_member(db, member_id)
    return member.total_hours_granted - member.total_hours_used

# Mobile number normalization
def normalize_mobile(mobile: str) -> str:
    """
    Normalize mobile number to 10-digit format.

    Examples:
        "+639171234567" -> "9171234567"
        "09171234567" -> "9171234567"
        "9171234567" -> "9171234567"
    """
    digits = ''.join(filter(str.isdigit, mobile))
    if digits.startswith('63'):
        return digits[2:]  # Remove country code
    if digits.startswith('0'):
        return digits[1:]  # Remove leading zero
    return digits[-10:]  # Last 10 digits
```

### TypeScript (Frontend)

```typescript
// ALWAYS define interfaces for props and data
interface Member {
  id: string;
  mobile: string;
  full_name: string;
  email?: string;
  balance_hours: number;
  total_hours_granted: number;
  total_hours_used: number;
  expiry_date: string;
  is_expired: boolean;
}

interface MemberSearchProps {
  onMemberFound: (member: Member) => void;
  placeholder?: string;
}

// NO any types allowed
const fetchMember = async (mobile: string): Promise<Member> => {
  const response = await api.get<Member>(`/api/v1/members/search?mobile=${mobile}`);
  return response.data;
};

// Always handle loading and error states
const useMemberSearch = (mobile: string) => {
  const [member, setMember] = useState<Member | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!mobile) return;

    const searchMember = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchMember(mobile);
        setMember(data);
      } catch (err) {
        setError('Member not found');
      } finally {
        setLoading(false);
      }
    };

    searchMember();
  }, [mobile]);

  return { member, loading, error };
};
```

---

## Forbidden Patterns

### Backend
- ❌ Never use `print()` - use `logging` module
- ❌ Never store passwords in plain text - use bcrypt via `passlib`
- ❌ Never hardcode secrets - use environment variables
- ❌ Never use `SELECT *` - specify columns or use ORM models
- ❌ Never skip input validation - use Pydantic schemas
- ❌ Never perform calculations in controllers - move to services
- ❌ Never forget to normalize mobile numbers before DB operations

### Frontend
- ❌ Never use `any` type - define proper interfaces
- ❌ Never leave `console.log` in production code
- ❌ Never skip error handling in async operations
- ❌ Never use inline styles - use Tailwind utility classes
- ❌ Never mutate state directly - use setState/useState
- ❌ Never forget loading states for async operations
- ❌ Never hardcode API URLs - use environment variables

---

## Module-Specific Rules

### Members Module
- All members MUST have a unique 10-digit mobile number
- Mobile numbers are the primary lookup key (indexed)
- `balance_hours` is ALWAYS computed (never stored directly)
- `is_expired` is computed based on current date vs. `expiry_date`
- Member search must return results in < 500ms

### Credits/Balance Module
- Every purchase MUST trigger automatic `expiry_date` calculation (365 days)
- Rollover logic MUST check previous purchase expiry date
- **180-day Rollover Rule**:
  - IF previous plan expired < 180 days ago → apply rollover
  - ELSE → forfeit unused hours
- Balance calculation MUST be real-time (not cached)
- Manual adjustments MUST create audit trail entries

### Gaming Sessions Module
- Sessions MUST deduct `hours_consumed` from member balance on end
- Active sessions (time_end = NULL) should not affect balance yet
- Session start MUST verify member has sufficient balance
- Voided sessions MUST refund hours back to member
- All sessions MUST be linked to a branch

### Dashboard Module
- Member search is the PRIMARY interface element
- All stats MUST be real-time (no stale data)
- Occupancy data updates every 5 seconds
- Mobile-first responsive design (min-width: 320px)

---

## API Conventions

- All endpoints prefixed with `/api/v1/`
- Use plural nouns for resources: `/members`, `/sessions`, `/purchases`
- Return appropriate HTTP status codes:
  - 200: Success (GET, PUT)
  - 201: Created (POST)
  - 204: No Content (DELETE)
  - 400: Bad Request (validation errors)
  - 401: Unauthorized (missing/invalid token)
  - 403: Forbidden (insufficient permissions)
  - 404: Not Found
  - 409: Conflict (duplicate mobile number)
  - 500: Internal Server Error

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}

// Error format
{
  "success": false,
  "error": "Error description",
  "details": { ... }
}
```

---

## Business Logic

### 180-Day Rollover Logic

```python
def apply_rollover(db: Session, member_id: str, new_purchase: Purchase) -> Decimal:
    """
    Apply 180-day rollover when member purchases new plan.

    Rules:
    1. Find previous purchase
    2. Check if previous plan expired < 180 days ago
    3. If yes: rollover = previous.total_valid_purchased - previous.total_hours_used
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
        unused_hours = previous_purchase.total_valid_purchased - previous_purchase.total_hours_used
        rollover = max(unused_hours, Decimal(0))
        previous_purchase.rollover_status = 'applied'
    else:
        # Forfeit
        rollover = Decimal(0)
        previous_purchase.rollover_status = 'forfeited'

    db.commit()
    return new_purchase.hours_granted + rollover
```

### Balance Calculation

```python
def get_member_balance(db: Session, member_id: str) -> dict:
    """
    Get real-time balance breakdown.

    Returns:
        {
            'total_hours_granted': Decimal,
            'total_hours_used': Decimal,
            'balance_hours': Decimal,
            'is_expired': bool
        }
    """
    member = get_member(db, member_id)
    return {
        'total_hours_granted': member.total_hours_granted,
        'total_hours_used': member.total_hours_used,
        'balance_hours': member.total_hours_granted - member.total_hours_used,
        'is_expired': member.is_expired
    }
```

---

## Authentication

### JWT Configuration
- Access token expires: 30 minutes
- Refresh token expires: 7 days
- Algorithm: HS256
- Token payload: `{ user_id, email, role, branch_id }`

### Google OAuth Flow
1. Frontend redirects to `/api/v1/auth/google`
2. Backend redirects to Google OAuth consent
3. Google redirects back with authorization code
4. Backend exchanges code for user info
5. Backend creates/updates user in DB
6. Backend returns JWT tokens
7. Always verify state parameter for CSRF protection

### Role-Based Access Control (RBAC)
- **admin**: Full access to all branches, can manage users
- **manager**: Access to assigned branch, can manage members/sessions
- **staff**: Read-only access to assigned branch

---

## Environment Variables

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

# Frontend
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# App Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## Development Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173

# Docker
docker-compose up -d
docker-compose logs -f backend
docker-compose logs -f frontend

# Tests
pytest backend/tests -v --cov=app --cov-report=html
cd frontend && npm test
npm run type-check

# Linting
ruff check backend/
ruff format backend/
cd frontend && npm run lint
npm run lint:fix

# Database
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

---

## Commit Message Format

```
feat(members): add mobile number search endpoint
fix(balance): correct 180-day rollover calculation
refactor(sessions): extract session service logic
test(balance): add rollover edge case tests
docs(api): update OpenAPI specs for purchases
chore(deps): update fastapi to 0.104.0
```

**Scopes:** auth, members, purchases, sessions, dashboard, frontend, backend, db

---

## Testing Requirements

### Backend Tests (pytest)
```python
# Test 180-day rollover logic
def test_rollover_within_180_days():
    """Test that unused hours rollover when renewed within 180 days."""
    # Create member with 100 hours
    # Use 30 hours
    # Purchase new plan within 180 days
    # Assert: new total = new_hours + (100 - 30)

def test_rollover_after_180_days():
    """Test that unused hours forfeit after 180 days."""
    # Create member with 100 hours
    # Use 30 hours
    # Purchase new plan after 180 days
    # Assert: new total = new_hours only

def test_member_search_by_mobile():
    """Test member lookup by normalized mobile number."""
    # Create member with mobile "09171234567"
    # Search with "+639171234567"
    # Assert: member found
```

### Frontend Tests (Vitest + Testing Library)
```typescript
// Test member search component
test('MemberSearch displays member details on valid mobile', async () => {
  render(<MemberSearch onMemberFound={jest.fn()} />);
  const input = screen.getByPlaceholderText('Enter mobile number');
  fireEvent.change(input, { target: { value: '9171234567' } });
  await waitFor(() => {
    expect(screen.getByText(/balance:/i)).toBeInTheDocument();
  });
});
```

---

## Performance Targets

- Member lookup by mobile: < 500ms
- Balance calculation: < 1s (even with 1000+ transactions)
- Dashboard load time: < 2s
- Session creation: < 300ms
- Real-time occupancy update: every 5 seconds
- Support 10,000 active members per gaming hub

---

## Skills Reference

| Task | Skill to Read |
|------|---------------|
| Database models | `skills/DATABASE.md` |
| API + Auth | `skills/BACKEND.md` |
| React + UI | `skills/FRONTEND.md` |
| Testing | `skills/TESTING.md` |
| Deployment | `skills/DEPLOYMENT.md` |

---

## Agent Coordination

For complex tasks, agents coordinate as follows:

| Agent | Responsibilities |
|-------|------------------|
| DATABASE-AGENT | Create Member, Purchase, GamingSession, Branch, User models + migrations |
| BACKEND-AGENT | Build all API endpoints, implement rollover logic, Dodo Payments integration |
| FRONTEND-AGENT | Create Dashboard, Member Search, Session Tracking, Balance Cards UI |
| TEST-AGENT | Write unit tests for rollover logic, integration tests for API |
| REVIEW-AGENT | Audit RBAC implementation, review balance calculation security |
| DEVOPS-AGENT | Docker Compose setup, PostgreSQL config, deployment scripts |

Read agent definitions in `/agents/` folder.

---

## Mobile Optimization

- Design for 320px minimum width (iPhone SE)
- Use responsive Tailwind breakpoints: `sm:`, `md:`, `lg:`
- Primary actions must be thumb-reachable (bottom of screen)
- Member search bar should be sticky/fixed at top
- Balance cards should be swipeable on mobile
- Use native mobile inputs for numbers and dates

---

## Security Checklist

- [ ] Rate limiting on `/auth/*` endpoints (10 req/min)
- [ ] Input validation on all endpoints (Pydantic)
- [ ] Mobile number normalization to prevent duplicates
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] XSS prevention (React auto-escapes, sanitize user input)
- [ ] CSRF protection for OAuth (state parameter)
- [ ] Audit trail for all manual balance adjustments
- [ ] RBAC middleware on protected routes
- [ ] Secure password hashing (bcrypt, cost factor 12)
- [ ] HTTPS in production
- [ ] Secrets in environment variables (never committed)

---

## Ready to Build?

```bash
# Step 1: Generate PRP
/generate-prp INITIAL.md

# Step 2: Execute PRP
/execute-prp PRPs/untangle-prp.md
```
