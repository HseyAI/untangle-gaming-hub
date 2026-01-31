"""
Gaming session management service with hour tracking.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
from decimal import Decimal

from ..models.session import GamingSession
from ..models.member import Member
from ..exceptions import ConflictException, NotFoundException, ValidationException
from ..services import members_service


def start_session(
    db: Session,
    member_id: str,
    station_id: Optional[str] = None,
    notes: Optional[str] = None
) -> GamingSession:
    """
    Start a new gaming session for a member.

    Validations:
    - Member must exist
    - Member must have active balance > 0
    - Member must not have another active session
    - Member's plan must not be expired

    Args:
        db: Database session
        member_id: Member ID
        station_id: Optional gaming station/PC ID
        notes: Optional session notes

    Returns:
        GamingSession: Created session instance

    Raises:
        NotFoundException: If member not found
        ValidationException: If member cannot start session
        ConflictException: If member already has active session
    """
    # Validate member exists
    member = members_service.get_member_by_id(db, member_id)
    if not member:
        raise NotFoundException("Member", member_id)

    # Check if member's plan is expired
    if member.is_expired:
        raise ValidationException(
            f"Member's plan expired on {member.expiry_date}. Please renew to continue."
        )

    # Check if member has balance
    if member.balance_hours <= 0:
        raise ValidationException(
            f"Member has no remaining hours. Current balance: {member.balance_hours}"
        )

    # Check if member already has an active session
    active_session = db.query(GamingSession).filter(
        GamingSession.member_id == member_id,
        GamingSession.end_time.is_(None)
    ).first()

    if active_session:
        raise ConflictException(
            f"Member already has an active session (started at {active_session.start_time})",
            field="member_id"
        )

    # Create new session
    session = GamingSession(
        member_id=member_id,
        start_time=datetime.utcnow(),
        station_id=station_id,
        notes=notes
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def end_session(
    db: Session,
    session_id: str,
    manual_hours: Optional[Decimal] = None,
    notes: Optional[str] = None
) -> GamingSession:
    """
    End an active gaming session and deduct hours from member's balance.

    Hour Calculation:
    - If manual_hours provided: use that value (admin override)
    - Otherwise: calculate from start_time to end_time (in hours, rounded to 2 decimals)

    Deduction Logic:
    - Hours are deducted from member's total_hours_used
    - Real-time balance = total_hours_granted - total_hours_used (via hybrid property)
    - If calculated hours exceed member's balance, use all remaining balance

    Args:
        db: Database session
        session_id: Session ID to end
        manual_hours: Optional manual hour override (admin only)
        notes: Optional additional notes

    Returns:
        GamingSession: Updated session instance

    Raises:
        NotFoundException: If session not found
        ValidationException: If session already ended
    """
    session = db.query(GamingSession).filter(GamingSession.id == session_id).first()
    if not session:
        raise NotFoundException("Session", session_id)

    # Check if session already ended
    if session.end_time is not None:
        raise ValidationException(
            f"Session already ended at {session.end_time}"
        )

    # Get member
    member = members_service.get_member_by_id(db, session.member_id)
    if not member:
        raise NotFoundException("Member", session.member_id)

    # Set end time
    session.end_time = datetime.utcnow()

    # Calculate hours
    if manual_hours is not None:
        # Admin manual override
        hours_to_deduct = manual_hours
    else:
        # Calculate from time difference
        duration = session.end_time - session.start_time
        hours_to_deduct = Decimal(str(round(duration.total_seconds() / 3600, 2)))

    # Don't deduct more than member's balance
    if hours_to_deduct > member.balance_hours:
        hours_to_deduct = member.balance_hours

    # Ensure minimum of 0
    if hours_to_deduct < 0:
        hours_to_deduct = Decimal("0.0")

    # Set hours and deduct from member
    session.hours_used = hours_to_deduct

    # Deduct hours from member's balance
    member.total_hours_used += hours_to_deduct

    # Append notes if provided
    if notes:
        if session.notes:
            session.notes += f"\n{notes}"
        else:
            session.notes = notes

    db.commit()
    db.refresh(session)
    db.refresh(member)

    return session


def get_session_by_id(db: Session, session_id: str) -> Optional[GamingSession]:
    """Get session by ID."""
    return db.query(GamingSession).filter(GamingSession.id == session_id).first()


def get_member_sessions(
    db: Session,
    member_id: str,
    page: int = 1,
    page_size: int = 50
) -> Tuple[list[GamingSession], int]:
    """
    Get all sessions for a member with pagination.

    Args:
        db: Database session
        member_id: Member ID
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple[list[GamingSession], int]: List of sessions and total count
    """
    query = db.query(GamingSession).filter(GamingSession.member_id == member_id)

    total = query.count()

    offset = (page - 1) * page_size
    sessions = query.order_by(GamingSession.start_time.desc()).offset(offset).limit(page_size).all()

    return sessions, total


def get_active_sessions(db: Session) -> list[GamingSession]:
    """
    Get all currently active sessions.

    Returns:
        list[GamingSession]: List of active sessions
    """
    return db.query(GamingSession).filter(
        GamingSession.end_time.is_(None)
    ).order_by(GamingSession.start_time.asc()).all()


def list_sessions(
    db: Session,
    member_id: Optional[str] = None,
    active_only: bool = False,
    page: int = 1,
    page_size: int = 50
) -> Tuple[list[GamingSession], int]:
    """
    List all sessions with optional filters.

    Args:
        db: Database session
        member_id: Optional filter by member
        active_only: Filter only active sessions (not ended)
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple[list[GamingSession], int]: List of sessions and total count
    """
    query = db.query(GamingSession)

    # Apply filters
    if member_id:
        query = query.filter(GamingSession.member_id == member_id)

    if active_only:
        query = query.filter(GamingSession.end_time.is_(None))

    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    sessions = query.order_by(GamingSession.start_time.desc()).offset(offset).limit(page_size).all()

    return sessions, total


def get_session_stats(db: Session, member_id: Optional[str] = None) -> dict:
    """
    Get session statistics.

    Args:
        db: Database session
        member_id: Optional filter by member

    Returns:
        dict: Session statistics
    """
    query = db.query(GamingSession)

    if member_id:
        query = query.filter(GamingSession.member_id == member_id)

    # Total sessions
    total_sessions = query.count()

    # Total hours used (only completed sessions)
    total_hours = db.query(func.sum(GamingSession.hours_used)).filter(
        GamingSession.hours_used.isnot(None)
    ).scalar() or Decimal("0.0")

    # Active sessions
    active_sessions = query.filter(GamingSession.end_time.is_(None)).count()

    # Average session duration
    avg_duration = db.query(func.avg(GamingSession.hours_used)).filter(
        GamingSession.hours_used.isnot(None)
    ).scalar() or Decimal("0.0")

    # Busiest hour (hour of day with most sessions)
    # This is a simplified version - in production, you'd want more sophisticated analytics
    busiest_hour = None

    return {
        "total_sessions": total_sessions,
        "total_hours_used": Decimal(str(total_hours)),
        "active_sessions": active_sessions,
        "average_session_duration": Decimal(str(avg_duration)) if avg_duration else Decimal("0.0"),
        "busiest_hour": busiest_hour
    }
