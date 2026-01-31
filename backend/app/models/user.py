"""
User and RefreshToken models for authentication.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
import uuid

from ..database import Base
from .base import TimestampMixin


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


class User(Base, TimestampMixin):
    """
    User model for gaming hub administrators.

    Supports role-based access control (RBAC) and OAuth.
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STAFF, nullable=False, index=True)
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    oauth_provider = Column(String, nullable=True)  # "google" or None

    # Relationships
    branch = relationship("Branch", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    created_purchases = relationship("Purchase", back_populates="creator", foreign_keys="Purchase.created_by")
    created_sessions = relationship("GamingSession", back_populates="creator", foreign_keys="GamingSession.created_by")

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"


class RefreshToken(Base):
    """
    Refresh token model for JWT authentication.

    Stores refresh tokens with expiration and revocation support.
    """
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken {self.id} for user {self.user_id}>"
