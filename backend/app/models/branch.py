"""
Branch model for gaming hub locations.
"""
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from ..database import Base
from .base import UUIDMixin, TimestampMixin


class Branch(Base, UUIDMixin, TimestampMixin):
    """
    Branch model representing gaming hub locations.

    Each branch can have multiple users, members, and sessions.
    """
    __tablename__ = "branches"

    name = Column(String, unique=True, nullable=False, index=True)  # e.g., "Downtown", "Mall"
    location = Column(String, nullable=False)  # Address
    total_stations = Column(Integer, default=0, nullable=False)  # Number of gaming stations
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="branch")
    members = relationship("Member", back_populates="branch_preferred")
    sessions = relationship("GamingSession", back_populates="branch")

    def __repr__(self):
        return f"<Branch {self.name} - {self.total_stations} stations>"
