"""
Dashboard analytics and reporting endpoints for UNTANGLE.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta
import io
import csv
import json

from ..database import get_db
from ..schemas.dashboard import (
    DashboardStatsResponse,
    RevenueStatsResponse,
    ExpiringMembersResponse,
    ExpiringMemberInfo,
    TopMembersResponse,
    TopMemberInfo,
    RevenueChartResponse
)
from ..services import dashboard_service
from ..dependencies import get_current_user, require_role
from ..models.user import User

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall dashboard statistics.

    Returns:
    - Total, active, and expired members
    - Total revenue and hours (granted/used/balance)
    - Active sessions count
    - Members expiring soon (next 30 days)
    - Pending rollovers

    Requires authentication. Admin/Manager can filter by branch.
    """
    stats = dashboard_service.get_overall_stats(db, branch_id=branch_id)
    return DashboardStatsResponse(**stats)


@router.get("/revenue", response_model=RevenueStatsResponse)
async def get_revenue_stats(
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get revenue analytics.

    Returns:
    - Total revenue and average purchase value
    - This month vs last month revenue
    - Total and monthly purchase counts
    - Revenue breakdown by payment method

    Requires authentication.
    """
    stats = dashboard_service.get_revenue_stats(db, branch_id=branch_id)
    return RevenueStatsResponse(**stats)


@router.get("/members/expiring", response_model=ExpiringMembersResponse)
async def get_expiring_members(
    days: int = Query(30, ge=1, le=180, description="Days to look ahead"),
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get members expiring within specified days.

    Returns list of members with:
    - Member details (ID, name, mobile)
    - Current balance hours
    - Expiry date
    - Days until expiry

    Sorted by expiry date (soonest first).

    Requires authentication.
    """
    members = dashboard_service.get_expiring_members(db, days=days, branch_id=branch_id)

    return ExpiringMembersResponse(
        members=[ExpiringMemberInfo(**m) for m in members],
        total=len(members)
    )


@router.get("/members/top", response_model=TopMembersResponse)
async def get_top_members(
    limit: int = Query(10, ge=1, le=50, description="Number of top members"),
    by: str = Query("usage", pattern="^(usage|spending)$", description="Sort by usage or spending"),
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get top members by usage or spending.

    Sort options:
    - "usage": Top members by total hours used
    - "spending": Top members by total amount spent

    Returns member details with usage and spending statistics.

    Requires authentication.
    """
    members = dashboard_service.get_top_members(db, limit=limit, by=by, branch_id=branch_id)

    return TopMembersResponse(
        members=[TopMemberInfo(**m) for m in members]
    )


@router.get("/revenue/chart", response_model=RevenueChartResponse)
async def get_revenue_chart(
    start_date: Optional[date] = Query(None, description="Start date (defaults to 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to today)"),
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily revenue data for chart visualization.

    Returns array of daily data points with:
    - Date
    - Revenue for that day
    - Number of purchases

    Defaults to last 30 days if dates not provided.

    Requires authentication.
    """
    # Default date range: last 30 days
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    data = dashboard_service.get_revenue_chart_data(
        db,
        start_date=start_date,
        end_date=end_date,
        branch_id=branch_id
    )

    return RevenueChartResponse(**data)


@router.get("/export/csv")
async def export_data_csv(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Export dashboard data as CSV.

    Exports:
    - All members with current balance and expiry
    - All purchases within date range (if specified)
    - All sessions within date range (if specified)

    Only admin and manager roles can export data.

    Returns CSV file for download.
    """
    from ..models.member import Member
    from ..models.purchase import Purchase
    from ..models.gaming_session import GamingSession

    output = io.StringIO()
    writer = csv.writer(output)

    # Export Members
    writer.writerow(["=== MEMBERS ==="])
    writer.writerow(["ID", "Full Name", "Mobile", "Email", "Total Hours Granted", "Total Hours Used", "Balance Hours", "Expiry Date"])

    members = db.query(Member).all()
    for m in members:
        writer.writerow([
            m.id, m.full_name, m.mobile, m.email or "",
            str(m.total_hours_granted), str(m.total_hours_used),
            str(m.balance_hours), str(m.expiry_date) if m.expiry_date else ""
        ])

    writer.writerow([])  # Empty row

    # Export Purchases
    writer.writerow(["=== PURCHASES ==="])
    writer.writerow(["ID", "Member ID", "Purchase Date", "Hours Purchased", "Amount Paid", "Payment Method", "Expiry Date", "Rollover Status"])

    purchase_query = db.query(Purchase)
    if start_date:
        purchase_query = purchase_query.filter(Purchase.purchase_date >= start_date)
    if end_date:
        purchase_query = purchase_query.filter(Purchase.purchase_date <= end_date)

    purchases = purchase_query.all()
    for p in purchases:
        writer.writerow([
            p.id, p.member_id, str(p.purchase_date), str(p.hours_purchased),
            str(p.amount_paid), p.payment_method, str(p.expiry_date), p.rollover_status
        ])

    writer.writerow([])  # Empty row

    # Export Sessions
    writer.writerow(["=== GAMING SESSIONS ==="])
    writer.writerow(["ID", "Member ID", "Start Time", "End Time", "Hours Used", "Station ID"])

    session_query = db.query(GamingSession)
    if start_date:
        session_query = session_query.filter(GamingSession.start_time >= start_date)
    if end_date:
        session_query = session_query.filter(GamingSession.start_time <= end_date)

    sessions = session_query.all()
    for s in sessions:
        writer.writerow([
            s.id, s.member_id, str(s.start_time),
            str(s.end_time) if s.end_time else "Active",
            str(s.hours_used) if s.hours_used else "0",
            s.station_id or ""
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=untangle_export_{date.today()}.csv"
        }
    )


@router.get("/export/json")
async def export_data_json(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Export dashboard data as JSON.

    Exports complete data structure with:
    - Members array
    - Purchases array
    - Sessions array
    - Summary statistics

    Only admin and manager roles can export data.

    Returns JSON file for download.
    """
    from ..models.member import Member
    from ..models.purchase import Purchase
    from ..models.gaming_session import GamingSession

    # Get data
    members = db.query(Member).all()

    purchase_query = db.query(Purchase)
    if start_date:
        purchase_query = purchase_query.filter(Purchase.purchase_date >= start_date)
    if end_date:
        purchase_query = purchase_query.filter(Purchase.purchase_date <= end_date)
    purchases = purchase_query.all()

    session_query = db.query(GamingSession)
    if start_date:
        session_query = session_query.filter(GamingSession.start_time >= start_date)
    if end_date:
        session_query = session_query.filter(GamingSession.start_time <= end_date)
    sessions = session_query.all()

    # Build JSON structure
    data = {
        "export_date": date.today().isoformat(),
        "date_range": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None
        },
        "members": [
            {
                "id": m.id,
                "full_name": m.full_name,
                "mobile": m.mobile,
                "email": m.email,
                "total_hours_granted": float(m.total_hours_granted),
                "total_hours_used": float(m.total_hours_used),
                "balance_hours": float(m.balance_hours),
                "expiry_date": m.expiry_date.isoformat() if m.expiry_date else None
            }
            for m in members
        ],
        "purchases": [
            {
                "id": p.id,
                "member_id": p.member_id,
                "purchase_date": p.purchase_date.isoformat(),
                "hours_purchased": float(p.hours_purchased),
                "amount_paid": float(p.amount_paid),
                "payment_method": p.payment_method,
                "rollover_status": p.rollover_status
            }
            for p in purchases
        ],
        "sessions": [
            {
                "id": s.id,
                "member_id": s.member_id,
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "hours_used": float(s.hours_used) if s.hours_used else 0,
                "station_id": s.station_id
            }
            for s in sessions
        ],
        "summary": {
            "total_members": len(members),
            "total_purchases": len(purchases),
            "total_sessions": len(sessions)
        }
    }

    json_str = json.dumps(data, indent=2)

    return StreamingResponse(
        iter([json_str]),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=untangle_export_{date.today()}.json"
        }
    )
