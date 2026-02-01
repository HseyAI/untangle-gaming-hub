"""
Dashboard analytics and reporting service.
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, datetime, timedelta
from decimal import Decimal

from ..models.member import Member
from ..models.purchase import Purchase
from ..models.session import GamingSession
from ..services import sessions_service


def get_overall_stats(db: Session, branch_id: Optional[str] = None) -> dict:
    """
    Get overall dashboard statistics.

    Args:
        db: Database session
        branch_id: Optional filter by branch

    Returns:
        dict: Overall statistics
    """
    # Base queries
    member_query = db.query(Member)
    purchase_query = db.query(Purchase)

    if branch_id:
        member_query = member_query.filter(Member.branch_id == branch_id)
        purchase_query = purchase_query.join(Member).filter(Member.branch_id == branch_id)

    # Total members
    total_members = member_query.count()

    # Active members (not expired)
    today = date.today()
    active_members = member_query.filter(
        or_(
            Member.expiry_date >= today,
            Member.expiry_date.is_(None)
        )
    ).count()

    # Expired members
    expired_members = member_query.filter(Member.expiry_date < today).count()

    # Total revenue
    total_revenue = purchase_query.with_entities(
        func.sum(Purchase.amount_paid)
    ).scalar() or Decimal("0.0")

    # Total hours granted
    total_hours_granted = member_query.with_entities(
        func.sum(Member.total_hours_granted)
    ).scalar() or Decimal("0.0")

    # Total hours used
    total_hours_used = member_query.with_entities(
        func.sum(Member.total_hours_used)
    ).scalar() or Decimal("0.0")

    # Total balance hours
    total_balance_hours = total_hours_granted - total_hours_used

    # Active sessions
    active_sessions = db.query(GamingSession).filter(
        GamingSession.time_end.is_(None)
    ).count()

    # Members expiring in next 30 days
    thirty_days_later = today + timedelta(days=30)
    members_expiring_soon = member_query.filter(
        and_(
            Member.expiry_date >= today,
            Member.expiry_date <= thirty_days_later
        )
    ).count()

    # Pending rollovers
    pending_rollovers = purchase_query.filter(
        Purchase.rollover_status == "pending"
    ).count()

    return {
        "total_members": total_members,
        "active_members": active_members,
        "expired_members": expired_members,
        "total_revenue": Decimal(str(total_revenue)),
        "total_hours_granted": Decimal(str(total_hours_granted)),
        "total_hours_used": Decimal(str(total_hours_used)),
        "total_balance_hours": Decimal(str(total_balance_hours)),
        "active_sessions": active_sessions,
        "members_expiring_soon": members_expiring_soon,
        "pending_rollovers": pending_rollovers
    }


def get_revenue_stats(db: Session, branch_id: Optional[str] = None) -> dict:
    """
    Get revenue analytics.

    Args:
        db: Database session
        branch_id: Optional filter by branch

    Returns:
        dict: Revenue statistics
    """
    query = db.query(Purchase)

    if branch_id:
        query = query.join(Member).filter(Member.branch_id == branch_id)

    # Total revenue
    total_revenue = query.with_entities(func.sum(Purchase.amount_paid)).scalar() or Decimal("0.0")

    # This month's revenue
    today = date.today()
    first_day_this_month = today.replace(day=1)
    revenue_this_month = query.filter(
        Purchase.purchase_date >= first_day_this_month
    ).with_entities(func.sum(Purchase.amount_paid)).scalar() or Decimal("0.0")

    # Last month's revenue
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    revenue_last_month = query.filter(
        and_(
            Purchase.purchase_date >= first_day_last_month,
            Purchase.purchase_date < first_day_this_month
        )
    ).with_entities(func.sum(Purchase.amount_paid)).scalar() or Decimal("0.0")

    # Total purchases
    total_purchases = query.count()

    # Average purchase value
    average_purchase_value = total_revenue / total_purchases if total_purchases > 0 else Decimal("0.0")

    # Purchases this month
    purchases_this_month = query.filter(
        Purchase.purchase_date >= first_day_this_month
    ).count()

    # Payment methods breakdown - TODO: Add payment_method field to Purchase model
    # payment_methods = {}
    # for method in ["cash", "dodo", "card"]:
    #     amount = query.filter(Purchase.payment_method == method).with_entities(
    #         func.sum(Purchase.amount_paid)
    #     ).scalar() or Decimal("0.0")
    #     payment_methods[method] = float(amount)

    return {
        "total_revenue": Decimal(str(total_revenue)),
        "revenue_this_month": Decimal(str(revenue_this_month)),
        "revenue_last_month": Decimal(str(revenue_last_month)),
        "average_purchase_value": Decimal(str(average_purchase_value)),
        "total_purchases": total_purchases,
        "purchases_this_month": purchases_this_month
        # "payment_methods": payment_methods  # TODO: Add after implementing payment_method field
    }


def get_expiring_members(
    db: Session,
    days: int = 30,
    branch_id: Optional[str] = None
) -> List[dict]:
    """
    Get members expiring within specified days.

    Args:
        db: Database session
        days: Number of days to look ahead
        branch_id: Optional filter by branch

    Returns:
        List[dict]: List of expiring members with details
    """
    today = date.today()
    future_date = today + timedelta(days=days)

    query = db.query(Member).filter(
        and_(
            Member.expiry_date >= today,
            Member.expiry_date <= future_date
        )
    )

    if branch_id:
        query = query.filter(Member.branch_id == branch_id)

    members = query.order_by(Member.expiry_date.asc()).all()

    result = []
    for member in members:
        days_until_expiry = (member.expiry_date - today).days
        result.append({
            "member_id": member.id,
            "full_name": member.full_name,
            "mobile": member.mobile,
            "balance_hours": member.balance_hours,
            "expiry_date": member.expiry_date,
            "days_until_expiry": days_until_expiry
        })

    return result


def get_top_members(
    db: Session,
    limit: int = 10,
    by: str = "usage",
    branch_id: Optional[str] = None
) -> List[dict]:
    """
    Get top members by usage or spending.

    Args:
        db: Database session
        limit: Number of top members to return
        by: Sort by "usage" or "spending"
        branch_id: Optional filter by branch

    Returns:
        List[dict]: List of top members
    """
    query = db.query(Member)

    if branch_id:
        query = query.filter(Member.branch_id == branch_id)

    if by == "usage":
        members = query.order_by(Member.total_hours_used.desc()).limit(limit).all()
    else:  # by spending
        # Join with purchases to get total spent
        members = query.join(Purchase).group_by(Member.id).order_by(
            func.sum(Purchase.amount_paid).desc()
        ).limit(limit).all()

    result = []
    for member in members:
        # Get member's total purchases and spending
        purchases = db.query(Purchase).filter(Purchase.member_id == member.id).all()
        total_purchases = len(purchases)
        total_spent = sum(p.amount_paid for p in purchases)

        result.append({
            "member_id": member.id,
            "full_name": member.full_name,
            "mobile": member.mobile,
            "total_hours_used": member.total_hours_used,
            "total_purchases": total_purchases,
            "total_spent": Decimal(str(total_spent))
        })

    return result


def get_revenue_chart_data(
    db: Session,
    start_date: date,
    end_date: date,
    branch_id: Optional[str] = None
) -> dict:
    """
    Get daily revenue data for chart visualization.

    Args:
        db: Database session
        start_date: Start date for the period
        end_date: End date for the period
        branch_id: Optional filter by branch

    Returns:
        dict: Revenue chart data
    """
    query = db.query(
        Purchase.purchase_date,
        func.sum(Purchase.amount_paid).label('revenue'),
        func.count(Purchase.id).label('purchases')
    ).filter(
        and_(
            Purchase.purchase_date >= start_date,
            Purchase.purchase_date <= end_date
        )
    ).group_by(Purchase.purchase_date)

    if branch_id:
        query = query.join(Member).filter(Member.branch_id == branch_id)

    results = query.all()

    # Create daily data points
    data = []
    total_revenue = Decimal("0.0")

    for row in results:
        data.append({
            "date": row.purchase_date.isoformat(),
            "revenue": Decimal(str(row.revenue)),
            "purchases": row.purchases
        })
        total_revenue += Decimal(str(row.revenue))

    return {
        "data": data,
        "total_revenue": total_revenue,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat()
    }
