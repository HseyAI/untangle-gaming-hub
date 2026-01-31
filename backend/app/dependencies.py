"""
UNTANGLE - FastAPI Dependencies
"""
from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db as _get_db
from .models.user import User
from .auth.jwt import verify_token
from .services import auth_service
from .exceptions import UnauthorizedException, NotFoundException

# Re-export get_db for convenience
get_db = _get_db

# OAuth2 scheme for bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    payload = verify_token(token, token_type="access")

    if not payload:
        raise UnauthorizedException("Could not validate credentials")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Could not validate credentials")

    user = auth_service.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User", user_id)

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (must be is_active=True).

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is inactive

    Note:
        This is now redundant since get_current_user already checks is_active,
        but kept for semantic clarity in endpoints.
    """
    return current_user


def require_role(allowed_roles: List[str]) -> Callable:
    """
    Dependency factory for role-based access control.

    Args:
        allowed_roles: List of role names that are allowed (e.g., ["admin", "manager"])

    Returns:
        Callable: Dependency function that checks user role

    Example:
        @router.get("/admin-only", dependencies=[Depends(require_role(["admin"]))])
        async def admin_endpoint():
            return {"message": "Admin access granted"}
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        """Check if current user has required role."""
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker
