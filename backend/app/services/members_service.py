"""
Member management service with business logic.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import date

from ..models.member import Member
from ..exceptions import ConflictException, NotFoundException
from ..utils import normalize_mobile


def create_member(
    db: Session,
    full_name: str,
    mobile: str,
    email: Optional[str] = None,
    branch_id: Optional[str] = None,
    notes: Optional[str] = None
) -> Member:
    """
    Create a new member.

    Args:
        db: Database session
        full_name: Member's full name
        mobile: Mobile number (will be normalized)
        email: Optional email address
        branch_id: Optional branch assignment
        notes: Optional notes

    Returns:
        Member: Created member instance

    Raises:
        ConflictException: If mobile number already exists
    """
    # Normalize mobile number
    normalized_mobile = normalize_mobile(mobile)

    # Check if mobile already exists
    existing = db.query(Member).filter(Member.mobile == normalized_mobile).first()
    if existing:
        raise ConflictException("Mobile number already registered", field="mobile")

    # Create new member
    member = Member(
        full_name=full_name,
        mobile=normalized_mobile,
        email=email,
        branch_id=branch_id,
        notes=notes
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


def get_member_by_id(db: Session, member_id: str) -> Optional[Member]:
    """Get member by ID."""
    return db.query(Member).filter(Member.id == member_id).first()


def get_member_by_mobile(db: Session, mobile: str) -> Optional[Member]:
    """Get member by mobile number."""
    normalized_mobile = normalize_mobile(mobile)
    return db.query(Member).filter(Member.mobile == normalized_mobile).first()


def update_member(
    db: Session,
    member_id: str,
    full_name: Optional[str] = None,
    mobile: Optional[str] = None,
    email: Optional[str] = None,
    branch_id: Optional[str] = None,
    notes: Optional[str] = None
) -> Member:
    """
    Update member information.

    Args:
        db: Database session
        member_id: Member ID to update
        full_name: New full name (optional)
        mobile: New mobile number (optional, will be normalized)
        email: New email (optional)
        branch_id: New branch assignment (optional)
        notes: New notes (optional)

    Returns:
        Member: Updated member instance

    Raises:
        NotFoundException: If member not found
        ConflictException: If new mobile number already exists
    """
    member = get_member_by_id(db, member_id)
    if not member:
        raise NotFoundException("Member", member_id)

    # Update fields if provided
    if full_name is not None:
        member.full_name = full_name

    if mobile is not None:
        normalized_mobile = normalize_mobile(mobile)
        # Check if new mobile is already taken by another member
        existing = db.query(Member).filter(
            Member.mobile == normalized_mobile,
            Member.id != member_id
        ).first()
        if existing:
            raise ConflictException("Mobile number already in use", field="mobile")
        member.mobile = normalized_mobile

    if email is not None:
        member.email = email

    if branch_id is not None:
        member.branch_id = branch_id

    if notes is not None:
        member.notes = notes

    db.commit()
    db.refresh(member)

    return member


def delete_member(db: Session, member_id: str) -> bool:
    """
    Delete a member (soft delete).

    Args:
        db: Database session
        member_id: Member ID to delete

    Returns:
        bool: True if deleted successfully

    Raises:
        NotFoundException: If member not found
    """
    member = get_member_by_id(db, member_id)
    if not member:
        raise NotFoundException("Member", member_id)

    # Soft delete (if using SoftDeleteMixin)
    # For now, we'll do a hard delete
    db.delete(member)
    db.commit()

    return True


def search_members(
    db: Session,
    search: Optional[str] = None,
    branch_id: Optional[str] = None,
    is_expired: Optional[bool] = None,
    page: int = 1,
    page_size: int = 50
) -> Tuple[list[Member], int]:
    """
    Search members with pagination and filters.

    Args:
        db: Database session
        search: Search term for name or mobile (optional)
        branch_id: Filter by branch (optional)
        is_expired: Filter by expiry status (optional)
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple[list[Member], int]: List of members and total count
    """
    query = db.query(Member)

    # Apply search filter
    if search:
        # Normalize search if it looks like a mobile number
        normalized_search = normalize_mobile(search) if search.isdigit() else search
        query = query.filter(
            or_(
                Member.full_name.ilike(f"%{search}%"),
                Member.mobile.like(f"%{normalized_search}%")
            )
        )

    # Apply branch filter
    if branch_id:
        query = query.filter(Member.branch_id == branch_id)

    # Apply expiry filter
    if is_expired is not None:
        today = date.today()
        if is_expired:
            query = query.filter(Member.expiry_date < today)
        else:
            query = query.filter(
                or_(
                    Member.expiry_date >= today,
                    Member.expiry_date.is_(None)
                )
            )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    members = query.order_by(Member.created_at.desc()).offset(offset).limit(page_size).all()

    return members, total
