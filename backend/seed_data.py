"""
Seed script to populate database with test data.
Bypasses the API to avoid bcrypt issues on Windows.
"""
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

# Add app to path
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.member import Member
from app.models.purchase import Purchase
from app.models.session import GamingSession
from app.models.branch import Branch

# Create a bcrypt hash for "password123" (pre-computed)
ADMIN_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXpjKUyK"


def create_test_data():
    """Create comprehensive test data for UNTANGLE."""
    db = SessionLocal()

    try:
        print("Seeding database with test data...")

        # 1. Create Branch
        print("\n[1/7] Creating test branch...")
        branch = Branch(
            id=str(uuid.uuid4()),
            name="Main Branch - Makati",
            location="123 Ayala Avenue, Makati City",
            total_stations=10,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(branch)
        db.commit()
        print(f"   OK: Branch created - {branch.name}")

        # 2. Create Admin User
        print("\n[2/7] Creating admin user...")
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@untangle.com",
            hashed_password=ADMIN_PASSWORD_HASH,
            full_name="Admin User",
            role=UserRole.ADMIN.value,
            branch_id=branch.id,
            is_active=True,
            is_verified=True,
            oauth_provider=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin)
        db.commit()
        print(f"   OK: {admin.email} (password: password123)")

        # 3. Create Manager User
        print("\n[3/7] Creating manager user...")
        manager = User(
            id=str(uuid.uuid4()),
            email="manager@untangle.com",
            hashed_password=ADMIN_PASSWORD_HASH,
            full_name="Manager User",
            role=UserRole.MANAGER.value,
            branch_id=branch.id,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(manager)
        db.commit()
        print(f"   OK: {manager.email} (password: password123)")

        # 4. Create Staff User
        print("\n[4/7] Creating staff user...")
        staff = User(
            id=str(uuid.uuid4()),
            email="staff@untangle.com",
            hashed_password=ADMIN_PASSWORD_HASH,
            full_name="Staff User",
            role=UserRole.STAFF.value,
            branch_id=branch.id,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(staff)
        db.commit()
        print(f"   OK: {staff.email} (password: password123)")

        # 5. Create Test Members
        print("\n[5/7] Creating test members...")
        members_data = [
            {"full_name": "Juan dela Cruz", "mobile": "9171234567", "email": "juan@example.com", "hours": 20, "amount": 500, "days_ago": 10},
            {"full_name": "Maria Santos", "mobile": "9187654321", "email": "maria@example.com", "hours": 50, "amount": 1200, "days_ago": 30},
            {"full_name": "Pedro Reyes", "mobile": "9191112233", "email": "pedro@example.com", "hours": 100, "amount": 2000, "days_ago": 60},
            {"full_name": "Ana Garcia", "mobile": "9199998888", "email": "ana@example.com", "hours": 30, "amount": 750, "days_ago": 5},
            {"full_name": "Carlos Mendoza", "mobile": "9195554444", "email": None, "hours": 15, "amount": 400, "days_ago": 90}
        ]

        members = []
        for data in members_data:
            registration_date = date.today() - timedelta(days=data["days_ago"])
            member = Member(
                id=str(uuid.uuid4()),
                full_name=data["full_name"],
                mobile=data["mobile"],
                email=data["email"],
                branch_preferred_id=branch.id,
                total_hours_granted=Decimal("0"),
                total_hours_used=Decimal("0"),
                expiry_date=None,
                registration_date=registration_date,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(member)
            db.commit()
            db.refresh(member)
            members.append((member, data))
            print(f"   OK: {member.full_name} - {member.mobile}")

        # 6. Create Purchases
        print("\n[6/7] Creating purchases...")
        for member, data in members:
            purchase_date_dt = datetime.combine(date.today() - timedelta(days=data["days_ago"]), datetime.min.time())
            expiry_date = purchase_date_dt.date() + timedelta(days=365)
            rollover_deadline = expiry_date + timedelta(days=180)

            purchase = Purchase(
                id=str(uuid.uuid4()),
                member_id=member.id,
                mobile=member.mobile,
                plan_name=f"{data['hours']} Hours Plan",
                amount_paid=Decimal(str(data["amount"])),
                hours_granted=Decimal(str(data["hours"])),
                total_valid_purchased=Decimal(str(data["hours"])),
                purchase_date=purchase_date_dt,
                expiry_date=expiry_date,
                rollover_deadline=rollover_deadline,
                rollover_status="pending",
                created_by=admin.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(purchase)
            member.total_hours_granted += Decimal(str(data["hours"]))
            member.expiry_date = expiry_date
            db.commit()
            print(f"   OK: {data['hours']}h for {member.full_name} - PHP{data['amount']}")

        # 7. Create Gaming Sessions
        print("\n[7/7] Creating gaming sessions...")

        # Active session
        session_date = date.today()
        time_start = datetime.utcnow() - timedelta(hours=2)
        active = GamingSession(
            id=str(uuid.uuid4()),
            member_id=members[0][0].id,
            mobile=members[0][0].mobile,
            branch_id=branch.id,
            date=session_date,
            time_start=time_start,
            time_end=None,
            hours_consumed=Decimal("0.0"),
            table_number="PC-01",
            game_title="Valorant",
            guru_assigned=staff.full_name,
            status="active",
            created_by=staff.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(active)
        db.commit()
        print(f"   OK: ACTIVE - {members[0][0].full_name} at PC-01")

        # Completed sessions
        sessions_data = [
            (1, 3.5, 1, "PC-02", "League of Legends"),
            (1, 5.0, 3, "PC-03", "Dota 2"),
            (2, 8.0, 2, "PC-01", "CS:GO"),
            (2, 10.0, 5, "PC-04", "Valorant"),
            (3, 2.0, 1, "PC-05", "Minecraft"),
            (0, 4.5, 7, "PC-01", "Fortnite")
        ]

        for idx, hours, days_ago, table_num, game in sessions_data:
            member, _ = members[idx]
            sess_date = date.today() - timedelta(days=days_ago)
            start = datetime.combine(sess_date, datetime.min.time()) + timedelta(hours=10)  # 10 AM
            end = start + timedelta(hours=hours)

            session = GamingSession(
                id=str(uuid.uuid4()),
                member_id=member.id,
                mobile=member.mobile,
                branch_id=branch.id,
                date=sess_date,
                time_start=start,
                time_end=end,
                hours_consumed=Decimal(str(hours)),
                table_number=table_num,
                game_title=game,
                guru_assigned=staff.full_name,
                status="completed",
                created_by=staff.id,
                created_at=start,
                updated_at=end
            )
            db.add(session)
            member.total_hours_used += Decimal(str(hours))
            db.commit()
            print(f"   OK: {member.full_name} - {hours}h at {table_num}")

        print("\n" + "="*60)
        print("SUCCESS! Database seeded with test data")
        print("="*60)

        print("\nSUMMARY:")
        print("  - 1 Branch")
        print("  - 3 Users (admin, manager, staff)")
        print("  - 5 Members")
        print("  - 5 Purchases")
        print("  - 7 Gaming Sessions (1 active, 6 completed)")

        print("\nLOGIN CREDENTIALS:")
        print("  Admin:   admin@untangle.com    / password123")
        print("  Manager: manager@untangle.com  / password123")
        print("  Staff:   staff@untangle.com    / password123")

        print("\nTEST MEMBERS:")
        for member, _ in members:
            balance = member.total_hours_granted - member.total_hours_used
            print(f"  {member.full_name:20} | {member.mobile} | Balance: {balance}h")

        print("\nNEXT STEPS:")
        print("  1. Visit: http://localhost:8000/docs")
        print("  2. Test GET endpoints (no auth required)")
        print("  3. Login to test protected endpoints")
        print("="*60)

    except Exception as e:
        print(f"\nERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
