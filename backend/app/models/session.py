"""
GamingSession model for activity tracking.
"""
from sqlalchemy import Column, String, DECIMAL, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
# UUID import removed for SQLite compatibility
from decimal import Decimal
import enum

from ..database import Base
from .base import UUIDMixin, TimestampMixin


class SessionStatus(str, enum.Enum):
    """Status of gaming session."""
    ACTIVE = "active"
    COMPLETED = "completed"
    VOIDED = "voided"


class GamingSession(Base, UUIDMixin, TimestampMixin):
    """
    GamingSession model for tracking gaming activity.

    Business Logic:
    - hours_consumed is calculated on session end: (time_end - time_start) / 3600
    - On end: deduct hours_consumed from member.total_hours_used
    - On void: refund hours_consumed back to member
    """
    __tablename__ = "gaming_sessions"

    # Member linkage
    member_id = Column(String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    mobile = Column(String(10), nullable=False)  # Denormalized

    # Location
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False, index=True)

    # Time tracking
    date = Column(Date, nullable=False, index=True)
    time_start = Column(DateTime, nullable=False)
    time_end = Column(DateTime, nullable=True)  # NULL for active sessions
    hours_consumed = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)

    # Session details
    table_number = Column(String, nullable=False)  # e.g., "PC-01", "Console-03"
    game_title = Column(String, nullable=False)
    guru_assigned = Column(String, nullable=False)  # Staff member name

    # Status
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False, index=True)

    # Audit
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Relationships
    member = relationship("Member", back_populates="sessions")
    branch = relationship("Branch", back_populates="sessions")
    creator = relationship("User", back_populates="created_sessions", foreign_keys=[created_by])

    def calculate_hours_consumed(self):
        """
        Calculate hours consumed from time_start to time_end.

        Returns hours as Decimal with 2 decimal places.
        """
        if not self.time_end:
            return Decimal('0.00')

        duration_seconds = (self.time_end - self.time_start).total_seconds()
        hours = Decimal(str(duration_seconds / 3600))
        return round(hours, 2)

    def __repr__(self):
        return f"<GamingSession {self.table_number} - {self.game_title} ({self.hours_consumed}h)>"
