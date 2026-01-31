"""
Purchase/Credits management service with 180-day rollover business logic.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from decimal import Decimal

from ..models.purchase import Purchase
from ..models.member import Member
from ..exceptions import ConflictException, NotFoundException, ValidationException
from ..services import members_service


def create_purchase(
    db: Session,
    member_id: str,
    hours_purchased: Decimal,
    amount_paid: Decimal,
    payment_method: str = "cash",
    payment_reference: Optional[str] = None,
    purchase_date: Optional[date] = None
) -> Purchase:
    """
    Create a new purchase and grant hours to member.

    This function handles the complete purchase workflow:
    1. Validates member exists
    2. Creates purchase record
    3. Calculates expiry dates (365 days + 180 day rollover deadline)
    4. Updates member's total_hours_granted
    5. Updates member's expiry_date to the latest purchase expiry

    Args:
        db: Database session
        member_id: Member ID
        hours_purchased: Number of hours to grant
        amount_paid: Amount paid in PHP
        payment_method: Payment method (cash/dodo/card)
        payment_reference: Optional payment reference
        purchase_date: Optional purchase date (defaults to today)

    Returns:
        Purchase: Created purchase instance

    Raises:
        NotFoundException: If member not found
        ValidationException: If hours or amount are invalid

    Business Logic:
        - Every purchase expires exactly 365 days from purchase date
        - Rollover deadline is 180 days after expiry (545 days total)
        - Hours are immediately added to member's total_hours_granted
    """
    # Validate member exists
    member = members_service.get_member_by_id(db, member_id)
    if not member:
        raise NotFoundException("Member", member_id)

    # Validate inputs
    if hours_purchased <= 0:
        raise ValidationException("Hours purchased must be greater than 0")

    if amount_paid < 0:
        raise ValidationException("Amount paid cannot be negative")

    # Use today if purchase_date not provided
    if purchase_date is None:
        purchase_date = date.today()

    # Create purchase record
    purchase = Purchase(
        member_id=member_id,
        purchase_date=purchase_date,
        hours_purchased=hours_purchased,
        amount_paid=amount_paid,
        payment_method=payment_method,
        payment_reference=payment_reference,
        rollover_status="pending"
    )

    # Calculate expiry dates (this is done automatically in the model's __init__)
    # But we'll call it explicitly to ensure it's set
    purchase.calculate_expiry_dates()

    db.add(purchase)

    # Update member's total hours and expiry date
    member.total_hours_granted += hours_purchased

    # Update member's expiry_date to the latest purchase expiry
    if member.expiry_date is None or purchase.expiry_date > member.expiry_date:
        member.expiry_date = purchase.expiry_date

    db.commit()
    db.refresh(purchase)
    db.refresh(member)

    return purchase


def get_purchase_by_id(db: Session, purchase_id: str) -> Optional[Purchase]:
    """Get purchase by ID."""
    return db.query(Purchase).filter(Purchase.id == purchase_id).first()


def get_member_purchases(
    db: Session,
    member_id: str,
    page: int = 1,
    page_size: int = 50
) -> Tuple[list[Purchase], int]:
    """
    Get all purchases for a member with pagination.

    Args:
        db: Database session
        member_id: Member ID
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple[list[Purchase], int]: List of purchases and total count
    """
    query = db.query(Purchase).filter(Purchase.member_id == member_id)

    total = query.count()

    offset = (page - 1) * page_size
    purchases = query.order_by(Purchase.purchase_date.desc()).offset(offset).limit(page_size).all()

    return purchases, total


def list_purchases(
    db: Session,
    member_id: Optional[str] = None,
    rollover_status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Tuple[list[Purchase], int]:
    """
    List all purchases with optional filters.

    Args:
        db: Database session
        member_id: Optional filter by member
        rollover_status: Optional filter by rollover status (pending/completed/expired)
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple[list[Purchase], int]: List of purchases and total count
    """
    query = db.query(Purchase)

    # Apply filters
    if member_id:
        query = query.filter(Purchase.member_id == member_id)

    if rollover_status:
        query = query.filter(Purchase.rollover_status == rollover_status)

    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    purchases = query.order_by(Purchase.purchase_date.desc()).offset(offset).limit(page_size).all()

    return purchases, total


def apply_rollover(
    db: Session,
    purchase_id: str,
    force: bool = False
) -> Purchase:
    """
    Apply 180-day rollover to a purchase.

    CRITICAL BUSINESS LOGIC:
    Rollover conditions:
    1. Current date must be AFTER expiry_date (plan has expired)
    2. Current date must be BEFORE rollover_deadline (within 180-day window)
    3. Member must have renewed (bought another plan within 180 days)
    4. Rollover status must be "pending"

    Rollover calculation:
    - Unused hours = hours_purchased - hours_used_from_this_purchase
    - These unused hours are added to member's next purchase

    Args:
        db: Database session
        purchase_id: Purchase ID to rollover
        force: Force rollover even if conditions not met (admin override)

    Returns:
        Purchase: Updated purchase with rollover applied

    Raises:
        NotFoundException: If purchase not found
        ValidationException: If rollover conditions not met

    Business Logic:
        - Only unused hours from expired purchases can rollover
        - Rollover must happen within 180 days of expiry
        - Member must have renewed within this window
        - Once rolled over, status changes to "completed"
        - If deadline passes, status changes to "expired"
    """
    purchase = get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise NotFoundException("Purchase", purchase_id)

    # Check if already processed
    if purchase.rollover_status in ["completed", "expired"]:
        raise ValidationException(f"Purchase rollover already {purchase.rollover_status}")

    today = date.today()

    # Validate rollover conditions (unless forced)
    if not force:
        # Must be after expiry date
        if today <= purchase.expiry_date:
            raise ValidationException(
                f"Cannot rollover - purchase not yet expired. Expires on {purchase.expiry_date}"
            )

        # Must be before rollover deadline
        if today > purchase.rollover_deadline:
            purchase.rollover_status = "expired"
            db.commit()
            raise ValidationException(
                f"Rollover deadline passed on {purchase.rollover_deadline}. Unused hours forfeited."
            )

        # Check if member has renewed (has another purchase after this one's expiry)
        member = members_service.get_member_by_id(db, purchase.member_id)
        if not member:
            raise NotFoundException("Member", purchase.member_id)

        renewal_purchase = db.query(Purchase).filter(
            Purchase.member_id == purchase.member_id,
            Purchase.purchase_date > purchase.expiry_date,
            Purchase.purchase_date <= purchase.rollover_deadline
        ).first()

        if not renewal_purchase:
            raise ValidationException(
                "No renewal found within 180-day window. Member must renew to claim rollover."
            )

    # Calculate unused hours
    # Note: In a real implementation, we'd track hours used per purchase
    # For now, we'll use a simplified calculation
    member = members_service.get_member_by_id(db, purchase.member_id)
    if not member:
        raise NotFoundException("Member", purchase.member_id)

    # Calculate rollover hours
    # For simplicity: rollover_hours = balance_hours (capped at this purchase's hours)
    rollover_hours = min(member.balance_hours, purchase.hours_purchased)

    if rollover_hours <= 0:
        rollover_hours = Decimal("0.0")

    # Apply rollover
    purchase.rollover_hours = rollover_hours
    purchase.rollover_status = "completed"
    purchase.rollover_applied_at = today

    # Add rollover hours to member's total
    member.total_hours_granted += rollover_hours

    db.commit()
    db.refresh(purchase)
    db.refresh(member)

    return purchase


def check_and_expire_rollovers(db: Session) -> int:
    """
    Batch job: Check all pending rollovers and expire those past deadline.

    This should be run as a scheduled task (e.g., daily cron job).

    Returns:
        int: Number of rollovers expired
    """
    today = date.today()

    # Find all pending rollovers past deadline
    expired_purchases = db.query(Purchase).filter(
        Purchase.rollover_status == "pending",
        Purchase.rollover_deadline < today
    ).all()

    count = 0
    for purchase in expired_purchases:
        purchase.rollover_status = "expired"
        count += 1

    db.commit()

    return count
