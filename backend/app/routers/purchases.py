"""
Purchase/Credits management endpoints for UNTANGLE.
Contains critical 180-day rollover business logic.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import math
from decimal import Decimal

from ..database import get_db
from ..schemas.purchases import (
    PurchaseCreate,
    PurchaseResponse,
    PurchaseListResponse,
    PurchaseHistoryResponse,
    RolloverRequest,
    RolloverResponse
)
from ..services import purchases_service, members_service
from ..dependencies import get_current_user, require_role
from ..models.user import User
from ..exceptions import NotFoundException

router = APIRouter()


@router.post("/", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    purchase_data: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new purchase and grant hours to member.

    This endpoint:
    - Creates a purchase record
    - Calculates 365-day expiry and 180-day rollover deadline
    - Immediately grants hours to member
    - Updates member's expiry date

    Requires authentication. All roles can create purchases.

    Business Logic:
    - Purchase expires exactly 365 days from purchase date
    - Rollover deadline is 180 days after expiry
    - Hours are immediately added to member's balance
    """
    purchase = purchases_service.create_purchase(
        db,
        member_id=purchase_data.member_id,
        hours_purchased=purchase_data.hours_purchased,
        amount_paid=purchase_data.amount_paid,
        payment_method=purchase_data.payment_method,
        payment_reference=purchase_data.payment_reference,
        purchase_date=purchase_data.purchase_date
    )

    return PurchaseResponse.from_orm(purchase)


@router.get("/", response_model=PurchaseListResponse)
async def list_purchases(
    member_id: Optional[str] = Query(None, description="Filter by member"),
    rollover_status: Optional[str] = Query(None, description="Filter by rollover status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all purchases with pagination and filters.

    Supports:
    - Filter by member
    - Filter by rollover status (pending/completed/expired)
    - Pagination

    Requires authentication.
    """
    purchases, total = purchases_service.list_purchases(
        db,
        member_id=member_id,
        rollover_status=rollover_status,
        page=page,
        page_size=page_size
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PurchaseListResponse(
        purchases=[PurchaseResponse.from_orm(p) for p in purchases],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/member/{member_id}/history", response_model=PurchaseHistoryResponse)
async def get_member_purchase_history(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete purchase history for a member with summary.

    Returns:
    - All purchases (paginated)
    - Total purchases count
    - Total hours granted
    - Total amount paid
    - Current active balance

    Requires authentication.
    """
    # Validate member exists
    member = members_service.get_member_by_id(db, member_id)
    if not member:
        raise NotFoundException("Member", member_id)

    # Get all purchases (no pagination for history summary)
    purchases, total = purchases_service.get_member_purchases(db, member_id, page=1, page_size=1000)

    # Calculate summary
    total_amount_paid = sum(p.amount_paid for p in purchases)

    return PurchaseHistoryResponse(
        member_id=member_id,
        purchases=[PurchaseResponse.from_orm(p) for p in purchases],
        total_purchases=total,
        total_hours_granted=member.total_hours_granted,
        total_amount_paid=total_amount_paid,
        active_balance=member.balance_hours
    )


@router.get("/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase(
    purchase_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get purchase details by ID.

    Returns complete purchase information including:
    - Purchase details
    - Expiry and rollover dates
    - Rollover status and hours

    Requires authentication.
    """
    purchase = purchases_service.get_purchase_by_id(db, purchase_id)

    if not purchase:
        raise NotFoundException("Purchase", purchase_id)

    return PurchaseResponse.from_orm(purchase)


@router.post("/{purchase_id}/rollover", response_model=RolloverResponse)
async def apply_rollover(
    purchase_id: str,
    rollover_request: RolloverRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Apply 180-day rollover to a purchase.

    CRITICAL BUSINESS LOGIC:
    Rollover conditions (all must be met unless forced):
    1. Purchase must be expired (after expiry_date)
    2. Must be within rollover window (before rollover_deadline)
    3. Member must have renewed within 180 days
    4. Rollover status must be "pending"

    Rollover calculation:
    - Unused hours from the expired purchase
    - Added to member's total hours
    - Rollover status changes to "completed"

    If deadline passed:
    - Status changes to "expired"
    - Unused hours are forfeited

    Only admin and manager roles can trigger rollover.
    Use force=true for admin override (bypasses validation).
    """
    try:
        purchase = purchases_service.apply_rollover(
            db,
            purchase_id=purchase_id,
            force=rollover_request.force
        )

        return RolloverResponse(
            success=True,
            purchase_id=purchase.id,
            rollover_hours=purchase.rollover_hours or Decimal("0.0"),
            rollover_status=purchase.rollover_status,
            message=f"Rollover applied successfully. {purchase.rollover_hours} hours added to member's balance."
        )

    except Exception as e:
        return RolloverResponse(
            success=False,
            purchase_id=purchase_id,
            rollover_hours=Decimal("0.0"),
            rollover_status="failed",
            message=str(e)
        )


@router.post("/batch/expire-rollovers", status_code=status.HTTP_200_OK)
async def batch_expire_rollovers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Batch job: Expire all rollovers past their deadline.

    This endpoint should be called by a scheduled task (cron job) daily.
    It automatically marks all pending rollovers past their 180-day deadline as "expired".

    Only admin role can trigger this batch job.

    Returns:
        Number of rollovers expired
    """
    count = purchases_service.check_and_expire_rollovers(db)

    return {
        "success": True,
        "message": f"Expired {count} rollover(s) past deadline",
        "count": count
    }
