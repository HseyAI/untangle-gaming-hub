"""
Base models and mixins for database models.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, String
import uuid


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    """Mixin that adds a UUID primary key (String-based for SQLite compatibility)."""

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
