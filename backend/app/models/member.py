"""
Member model for gaming hub customers.
"""
from sqlalchemy import Column, String, DECIMAL, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
# UUID import removed for SQLite compatibility
from datetime import date
from decimal import Decimal

from ..database import Base
from .base import UUIDMixin, TimestampMixin


class Member(Base, UUIDMixin, TimestampMixin):
    """
    Member model representing gaming hub customers.

    PRIMARY LOOKUP KEY: mobile (10-digit normalized)

    Key Business Logic:
    - balance_hours is COMPUTED: total_hours_granted - total_hours_used
    - is_expired is COMPUTED: today > expiry_date
    - Mobile numbers are normalized to 10-digit format
    """
    __tablename__ = "members"

    # Primary lookup key - normalized 10-digit mobile number
    mobile = Column(String(10), unique=True, index=True, nullable=False)

    # Profile information
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)

    # Credit tracking
    current_plan = Column(String, nullable=True)  # Latest plan name
    total_hours_granted = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    total_hours_used = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    # balance_hours is computed via hybrid_property below

    # Expiry tracking
    expiry_date = Column(Date, nullable=True, index=True)
    # is_expired is computed via hybrid_property below

    registration_date = Column(Date, nullable=False)

    # Branch preference
    branch_preferred_id = Column(String(36), ForeignKey("branches.id"), nullable=True)

    # Relationships
    branch_preferred = relationship("Branch", back_populates="members")
    purchases = relationship("Purchase", back_populates="member", cascade="all, delete-orphan", order_by="Purchase.purchase_date.desc()")
    sessions = relationship("GamingSession", back_populates="member", cascade="all, delete-orphan")

    @hybrid_property
    def balance_hours(self) -> Decimal:
        """
        Real-time balance calculation.

        Formula: total_hours_granted - total_hours_used
        """
        return self.total_hours_granted - self.total_hours_used

    @hybrid_property
    def is_expired(self) -> bool:
        """
        Check if member's plan has expired.

        Returns True if expiry_date is in the past.
        """
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date

    def __repr__(self):
        return f"<Member {self.mobile} - {self.full_name} ({self.balance_hours}h remaining)>"
