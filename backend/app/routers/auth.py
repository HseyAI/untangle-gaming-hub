"""
Authentication endpoints for UNTANGLE.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auth import (
    UserRegister,
    TokenResponse,
    TokenRefresh,
    UserResponse,
    UserUpdate,
    GoogleOAuthCallback
)
from ..services import auth_service
from ..auth.jwt import verify_token
from ..auth.oauth import exchange_code_for_token, get_google_user_info
from ..models.user import User
from ..exceptions import UnauthorizedException, NotFoundException

router = APIRouter()

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


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Creates a new user account and returns access/refresh tokens.
    """
    user = auth_service.create_user(
        db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role
    )

    tokens = auth_service.create_tokens_for_user(db, user)

    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password.

    Returns access and refresh tokens.
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise UnauthorizedException("Incorrect email or password")

    tokens = auth_service.create_tokens_for_user(db, user)

    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Returns new access and refresh tokens.
    """
    tokens = auth_service.refresh_access_token(db, token_data.refresh_token)

    return TokenResponse(**tokens)


@router.post("/logout")
async def logout(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logout by revoking refresh token.
    """
    auth_service.revoke_refresh_token(db, token_data.refresh_token)

    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    """
    if user_update.full_name:
        current_user.full_name = user_update.full_name

    if user_update.email and user_update.email != current_user.email:
        # Check if email is already taken
        existing = auth_service.get_user_by_email(db, user_update.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
        current_user.email = user_update.email

    db.commit()
    db.refresh(current_user)

    return UserResponse.from_orm(current_user)


@router.post("/google/callback", response_model=TokenResponse)
async def google_oauth_callback(
    callback_data: GoogleOAuthCallback,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.

    Exchanges authorization code for user info and creates/updates user.
    """
    # Exchange code for access token
    token_response = await exchange_code_for_token(
        callback_data.code,
        redirect_uri="http://localhost:8000/api/v1/auth/google/callback"
    )

    # Get user info from Google
    user_info = await get_google_user_info(token_response["access_token"])

    # Create or update user
    user = auth_service.create_or_update_oauth_user(
        db,
        email=user_info["email"],
        full_name=user_info.get("name", ""),
        provider="google"
    )

    # Create tokens
    tokens = auth_service.create_tokens_for_user(db, user)

    return TokenResponse(**tokens)
