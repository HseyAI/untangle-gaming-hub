"""
Pydantic schemas for member management.
"""
from typing import Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, validator

from ..utils import normalize_mobile


class MemberBase(BaseModel):
    """Base schema for member data."""
    full_name: str = Field(..., min_length=1, max_length=100)
    mobile: str = Field(..., min_length=10, max_length=15)
    email: Optional[str] = Field(None, max_length=100)
    branch_id: Optional[str] = None

    @validator('mobile')
    def normalize_mobile_number(cls, v):
        """Normalize mobile number to 10-digit format."""
        return normalize_mobile(v)


class MemberCreate(MemberBase):
    """Schema for creating a new member."""
    pass


class MemberUpdate(BaseModel):
    """Schema for updating a member."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    mobile: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[str] = Field(None, max_length=100)
    branch_id: Optional[str] = None
    notes: Optional[str] = None

    @validator('mobile')
    def normalize_mobile_number(cls, v):
        """Normalize mobile number to 10-digit format."""
        if v is not None:
            return normalize_mobile(v)
        return v


class MemberResponse(BaseModel):
    """Schema for member response."""
    id: str
    full_name: str
    mobile: str
    email: Optional[str]
    branch_id: Optional[str]
    total_hours_granted: Decimal
    total_hours_used: Decimal
    balance_hours: Decimal
    expiry_date: Optional[date]
    is_expired: bool
    notes: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class MemberListResponse(BaseModel):
    """Schema for paginated member list."""
    members: list[MemberResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MemberSearchParams(BaseModel):
    """Schema for member search parameters."""
    search: Optional[str] = Field(None, description="Search by name or mobile number")
    branch_id: Optional[str] = Field(None, description="Filter by branch")
    is_expired: Optional[bool] = Field(None, description="Filter by expiry status")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")
