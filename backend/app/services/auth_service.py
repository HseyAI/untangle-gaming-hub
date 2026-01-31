"""
Authentication service with business logic.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user import User, RefreshToken
from ..auth.jwt import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from ..exceptions import UnauthorizedException, ConflictException, NotFoundException
from ..config import settings


def create_user(db: Session, email: str, password: str, full_name: str, role: str = "staff") -> User:
    """Create a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ConflictException("Email already registered", field="email")

    # Create new user
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return user


def create_tokens_for_user(db: Session, user: User) -> dict:
    """Create access and refresh tokens for a user."""
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})

    # Create refresh token
    refresh_token_str = create_refresh_token(data={"sub": str(user.id)})

    # Save refresh token to database
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=expires_at,
        created_at=datetime.utcnow()
    )
    db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer"
    }


def refresh_access_token(db: Session, refresh_token_str: str) -> dict:
    """Refresh access token using refresh token."""
    # Verify refresh token
    payload = verify_token(refresh_token_str, token_type="refresh")
    if not payload:
        raise UnauthorizedException("Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid refresh token")

    # Check if refresh token exists and is not revoked
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token_str,
        RefreshToken.revoked == False
    ).first()

    if not refresh_token:
        raise UnauthorizedException("Refresh token revoked or not found")

    # Check if expired
    if refresh_token.expires_at < datetime.utcnow():
        raise UnauthorizedException("Refresh token expired")

    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    # Create new tokens
    return create_tokens_for_user(db, user)


def revoke_refresh_token(db: Session, refresh_token_str: str) -> bool:
    """Revoke a refresh token."""
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token_str
    ).first()

    if refresh_token:
        refresh_token.revoked = True
        db.commit()
        return True

    return False


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def create_or_update_oauth_user(db: Session, email: str, full_name: str, provider: str = "google") -> User:
    """Create or update user from OAuth."""
    user = get_user_by_email(db, email)

    if user:
        # Update existing user
        user.oauth_provider = provider
        user.is_verified = True
        user.is_active = True
        db.commit()
        db.refresh(user)
    else:
        # Create new user (no password for OAuth users)
        user = User(
            email=email,
            full_name=full_name,
            hashed_password="",  # No password for OAuth users
            oauth_provider=provider,
            is_verified=True,
            is_active=True,
            role="staff"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
