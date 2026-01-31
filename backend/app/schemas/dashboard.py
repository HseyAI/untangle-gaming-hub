"""
Pydantic schemas for dashboard analytics and reports.
"""
from typing import Optional, List
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class DashboardStatsResponse(BaseModel):
    """Schema for overall dashboard statistics."""
    total_members: int
    active_members: int
    expired_members: int
    total_revenue: Decimal
    total_hours_granted: Decimal
    total_hours_used: Decimal
    total_balance_hours: Decimal
    active_sessions: int
    members_expiring_soon: int
    pending_rollovers: int


class RevenueStatsResponse(BaseModel):
    """Schema for revenue analytics."""
    total_revenue: Decimal
    revenue_this_month: Decimal
    revenue_last_month: Decimal
    average_purchase_value: Decimal
    total_purchases: int
    purchases_this_month: int
    payment_methods: dict  # {"cash": amount, "dodo": amount, "card": amount}


class MemberStatusCount(BaseModel):
    """Schema for member status counts."""
    status: str
    count: int


class ExpiringMemberInfo(BaseModel):
    """Schema for members expiring soon."""
    member_id: str
    full_name: str
    mobile: str
    balance_hours: Decimal
    expiry_date: date
    days_until_expiry: int


class ExpiringMembersResponse(BaseModel):
    """Schema for expiring members list."""
    members: List[ExpiringMemberInfo]
    total: int


class TopMemberInfo(BaseModel):
    """Schema for top members by usage."""
    member_id: str
    full_name: str
    mobile: str
    total_hours_used: Decimal
    total_purchases: int
    total_spent: Decimal


class TopMembersResponse(BaseModel):
    """Schema for top members list."""
    members: List[TopMemberInfo]


class DailyRevenueData(BaseModel):
    """Schema for daily revenue data point."""
    date: str
    revenue: Decimal
    purchases: int


class RevenueChartResponse(BaseModel):
    """Schema for revenue chart data."""
    data: List[DailyRevenueData]
    total_revenue: Decimal
    period_start: str
    period_end: str


class ExportFormat(BaseModel):
    """Schema for export format request."""
    format: str = Field(default="csv", pattern="^(csv|json)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_members: bool = True
    include_purchases: bool = True
    include_sessions: bool = True
