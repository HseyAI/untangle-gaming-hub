"""
Gaming session endpoints for UNTANGLE.
Tracks hour usage and automatically deducts from member balance.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import math
from datetime import datetime

from ..database import get_db
from ..schemas.sessions import (
    SessionStart,
    SessionEnd,
    SessionResponse,
    SessionListResponse,
    SessionStatsResponse
)
from ..services import sessions_service, members_service
from ..dependencies import get_current_user, require_role
from ..models.user import User
from ..exceptions import NotFoundException

router = APIRouter()


@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    session_data: SessionStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new gaming session for a member.

    Validations:
    - Member must exist
    - Member must have active balance > 0
    - Member must not have another active session
    - Member's plan must not be expired

    No hours are deducted at start - only when session ends.

    Requires authentication. All roles can start sessions.
    """
    session = sessions_service.start_session(
        db,
        member_id=session_data.member_id,
        station_id=session_data.station_id,
        notes=session_data.notes
    )

    return SessionResponse.from_orm(session)


@router.put("/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: str,
    session_end: SessionEnd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    End an active gaming session and deduct hours.

    Hour Calculation:
    - If manual_hours provided: use that value (admin/manager only)
    - Otherwise: calculate from start_time to end_time

    Deduction Logic:
    - Hours deducted from member's total_hours_used
    - If calculated hours exceed balance, use all remaining balance
    - Balance cannot go negative

    Requires authentication. Manual hours require admin/manager role.
    """
    # Check if manual hours provided - requires elevated role
    if session_end.manual_hours is not None:
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin and manager can set manual hours"
            )

    session = sessions_service.end_session(
        db,
        session_id=session_id,
        manual_hours=session_end.manual_hours,
        notes=session_end.notes
    )

    return SessionResponse.from_orm(session)


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    member_id: Optional[str] = Query(None, description="Filter by member"),
    active_only: bool = Query(False, description="Show only active sessions"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all sessions with pagination and filters.

    Supports:
    - Filter by member
    - Filter active sessions only
    - Pagination

    Requires authentication.
    """
    sessions, total = sessions_service.list_sessions(
        db,
        member_id=member_id,
        active_only=active_only,
        page=page,
        page_size=page_size
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return SessionListResponse(
        sessions=[SessionResponse.from_orm(s) for s in sessions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/active", response_model=list[SessionResponse])
async def get_active_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all currently active sessions.

    Returns list of sessions that haven't been ended yet.
    Useful for real-time monitoring dashboard.

    Requires authentication.
    """
    sessions = sessions_service.get_active_sessions(db)

    return [SessionResponse.from_orm(s) for s in sessions]


@router.get("/member/{member_id}", response_model=SessionListResponse)
async def get_member_sessions(
    member_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get session history for a specific member.

    Returns all sessions (active and completed) for the member,
    ordered by start time (most recent first).

    Requires authentication.
    """
    # Validate member exists
    member = members_service.get_member_by_id(db, member_id)
    if not member:
        raise NotFoundException("Member", member_id)

    sessions, total = sessions_service.get_member_sessions(
        db,
        member_id=member_id,
        page=page,
        page_size=page_size
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return SessionListResponse(
        sessions=[SessionResponse.from_orm(s) for s in sessions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/stats", response_model=SessionStatsResponse)
async def get_session_stats(
    member_id: Optional[str] = Query(None, description="Filter by member"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get session statistics.

    Returns:
    - Total sessions count
    - Total hours used
    - Active sessions count
    - Average session duration
    - Busiest hour of day

    Optionally filter by member_id for member-specific stats.

    Requires authentication.
    """
    stats = sessions_service.get_session_stats(db, member_id=member_id)

    return SessionStatsResponse(**stats)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get session details by ID.

    Returns complete session information including:
    - Start and end times
    - Hours used
    - Member information
    - Station ID
    - Notes

    Requires authentication.
    """
    session = sessions_service.get_session_by_id(db, session_id)

    if not session:
        raise NotFoundException("Session", session_id)

    return SessionResponse.from_orm(session)
