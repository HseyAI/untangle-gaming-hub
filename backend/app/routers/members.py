"""
Member management endpoints for UNTANGLE.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from ..database import get_db
from ..schemas.members import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
)
from ..services import members_service
from ..dependencies import get_current_user, require_role
from ..models.user import User
from ..exceptions import NotFoundException, ConflictException

router = APIRouter()


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    member_data: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new member.

    Requires authentication. All roles can create members.
    """
    member = members_service.create_member(
        db,
        full_name=member_data.full_name,
        mobile=member_data.mobile,
        email=member_data.email,
        branch_id=member_data.branch_id
    )

    return MemberResponse.from_orm(member)


@router.get("/", response_model=MemberListResponse)
async def list_members(
    search: Optional[str] = Query(None, description="Search by name or mobile"),
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    is_expired: Optional[bool] = Query(None, description="Filter by expiry status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List and search members with pagination.

    Supports:
    - Search by name or mobile number
    - Filter by branch
    - Filter by expiry status
    - Pagination

    Requires authentication.
    """
    members, total = members_service.search_members(
        db,
        search=search,
        branch_id=branch_id,
        is_expired=is_expired,
        page=page,
        page_size=page_size
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return MemberListResponse(
        members=[MemberResponse.from_orm(m) for m in members],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/mobile/{mobile}", response_model=MemberResponse)
async def get_member_by_mobile(
    mobile: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get member by mobile number.

    Mobile number will be automatically normalized.
    Requires authentication.
    """
    member = members_service.get_member_by_mobile(db, mobile)

    if not member:
        raise NotFoundException("Member", f"mobile={mobile}")

    return MemberResponse.from_orm(member)


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get member by ID.

    Returns complete member information including balance and expiry status.
    Requires authentication.
    """
    member = members_service.get_member_by_id(db, member_id)

    if not member:
        raise NotFoundException("Member", member_id)

    return MemberResponse.from_orm(member)


@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: str,
    member_update: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update member information.

    Can update:
    - Full name
    - Mobile number (will check for conflicts)
    - Email
    - Branch assignment
    - Notes

    Requires authentication.
    """
    member = members_service.update_member(
        db,
        member_id=member_id,
        full_name=member_update.full_name,
        mobile=member_update.mobile,
        email=member_update.email,
        branch_id=member_update.branch_id,
        notes=member_update.notes
    )

    return MemberResponse.from_orm(member)


@router.delete("/{member_id}", status_code=status.HTTP_200_OK)
async def delete_member(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Delete a member.

    Only admin and manager roles can delete members.
    This is a hard delete - all member data will be removed.

    Warning: This will fail if the member has associated purchases or sessions.
    Consider deactivating instead by updating member status.
    """
    success = members_service.delete_member(db, member_id)

    return {
        "success": success,
        "message": f"Member {member_id} deleted successfully"
    }
