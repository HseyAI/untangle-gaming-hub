"""
Pydantic schemas for purchase/credits management.
"""
from typing import Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class PurchaseBase(BaseModel):
    """Base schema for purchase data."""
    member_id: str
    hours_purchased: Decimal = Field(..., gt=0, description="Number of hours purchased")
    amount_paid: Decimal = Field(..., ge=0, description="Amount paid in PHP")
    payment_method: str = Field(default="cash", pattern="^(cash|dodo|card)$")
    payment_reference: Optional[str] = Field(None, max_length=100)


class PurchaseCreate(PurchaseBase):
    """Schema for creating a new purchase."""
    purchase_date: Optional[date] = Field(None, description="Date of purchase (defaults to today)")


class PurchaseResponse(BaseModel):
    """Schema for purchase response."""
    id: str
    member_id: str
    purchase_date: date
    hours_purchased: Decimal
    amount_paid: Decimal
    payment_method: str
    payment_reference: Optional[str]
    expiry_date: date
    rollover_deadline: date
    rollover_status: str
    rollover_hours: Optional[Decimal]
    rollover_applied_at: Optional[date]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PurchaseListResponse(BaseModel):
    """Schema for paginated purchase list."""
    purchases: list[PurchaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PurchaseHistoryResponse(BaseModel):
    """Schema for member's purchase history with summary."""
    member_id: str
    purchases: list[PurchaseResponse]
    total_purchases: int
    total_hours_granted: Decimal
    total_amount_paid: Decimal
    active_balance: Decimal


class RolloverRequest(BaseModel):
    """Schema for manual rollover trigger."""
    force: bool = Field(default=False, description="Force rollover even if conditions not met")


class RolloverResponse(BaseModel):
    """Schema for rollover operation response."""
    success: bool
    purchase_id: str
    rollover_hours: Decimal
    rollover_status: str
    message: str
