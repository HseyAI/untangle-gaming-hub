"""
Pydantic schemas for gaming session management.
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class SessionStart(BaseModel):
    """Schema for starting a gaming session."""
    member_id: str
    station_id: Optional[str] = Field(None, max_length=50, description="Gaming station/PC ID")
    notes: Optional[str] = Field(None, max_length=500, description="Session notes")


class SessionEnd(BaseModel):
    """Schema for ending a gaming session."""
    manual_hours: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Manual hour override (admin only). If not provided, calculated from start/end time."
    )
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: str
    member_id: str
    start_time: datetime
    end_time: Optional[datetime]
    hours_used: Optional[Decimal]
    station_id: Optional[str]
    notes: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Schema for paginated session list."""
    sessions: list[SessionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ActiveSessionResponse(BaseModel):
    """Schema for active session with member details."""
    session_id: str
    member_id: str
    member_name: str
    member_mobile: str
    member_balance: Decimal
    start_time: datetime
    duration_minutes: int
    station_id: Optional[str]

    class Config:
        from_attributes = True


class SessionStatsResponse(BaseModel):
    """Schema for session statistics."""
    total_sessions: int
    total_hours_used: Decimal
    active_sessions: int
    average_session_duration: Decimal
    busiest_hour: Optional[int]
