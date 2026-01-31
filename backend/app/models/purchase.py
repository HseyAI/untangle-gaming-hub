"""
Purchase model for credit/plan transactions.

CRITICAL BUSINESS LOGIC: 180-day rollover + 365-day expiry
"""
from sqlalchemy import Column, String, DECIMAL, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
# UUID import removed for SQLite compatibility
from datetime import date, timedelta
from decimal import Decimal
import enum

from ..database import Base
from .base import UUIDMixin, TimestampMixin


class RolloverStatus(str, enum.Enum):
    """Status of rollover from previous purchase."""
    PENDING = "pending"
    APPLIED = "applied"
    FORFEITED = "forfeited"
    NOT_APPLICABLE = "not_applicable"


class Purchase(Base, UUIDMixin, TimestampMixin):
    """
    Purchase model for credit/plan assignments.

    CRITICAL BUSINESS LOGIC:
    1. expiry_date = purchase_date + 365 days (auto-calculated)
    2. rollover_deadline = expiry_date + 180 days (auto-calculated)
    3. 180-day Rollover Rule:
       - When a member purchases a new plan, unused hours from previous plan
         are rolled over ONLY if previous plan expired < 180 days ago
       - Otherwise, unused hours are forfeited
    """
    __tablename__ = "purchases"

    # Member linkage
    member_id = Column(String(36), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    mobile = Column(String(10), nullable=False)  # Denormalized for quick lookup

    # Plan details
    plan_name = Column(String, nullable=False)  # e.g., "60 Hours Premium"
    amount_paid = Column(DECIMAL(10, 2), nullable=False)

    # Hour tracking
    hours_granted = Column(DECIMAL(10, 2), nullable=False)  # Base hours for this plan
    total_valid_purchased = Column(DECIMAL(10, 2), nullable=False)  # Including rollover

    # Date tracking
    purchase_date = Column(DateTime, nullable=False, index=True)
    expiry_date = Column(Date, nullable=False, index=True)  # purchase_date + 365 days
    rollover_deadline = Column(Date, nullable=False)  # expiry_date + 180 days
    # is_expired is computed via hybrid_property below

    # Rollover status
    rollover_status = Column(
        SQLEnum(RolloverStatus),
        default=RolloverStatus.PENDING,
        nullable=False
    )

    # Audit
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Relationships
    member = relationship("Member", back_populates="purchases")
    creator = relationship("User", back_populates="created_purchases", foreign_keys=[created_by])

    @hybrid_property
    def is_expired(self) -> bool:
        """Check if this purchase has expired."""
        return date.today() > self.expiry_date

    def calculate_expiry_dates(self):
        """
        Calculate expiry_date and rollover_deadline from purchase_date.

        Called automatically on creation.
        """
        self.expiry_date = (self.purchase_date.date() + timedelta(days=365))
        self.rollover_deadline = self.expiry_date + timedelta(days=180)

    def __repr__(self):
        return f"<Purchase {self.plan_name} for {self.mobile} - {self.total_valid_purchased}h (expires {self.expiry_date})>"
