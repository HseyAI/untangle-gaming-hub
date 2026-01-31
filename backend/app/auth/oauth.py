"""
Google OAuth integration for UNTANGLE.
"""
from typing import Optional
import httpx
from fastapi import HTTPException, status

from ..config import settings


async def get_google_user_info(access_token: str) -> dict:
    """
    Get user information from Google OAuth.

    Args:
        access_token: Google OAuth access token

    Returns:
        dict: User information from Google

    Raises:
        HTTPException: If unable to fetch user info
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user information from Google"
            )

        return response.json()


async def exchange_code_for_token(code: str, redirect_uri: str) -> dict:
    """
    Exchange authorization code for access token.

    Args:
        code: Authorization code from Google
        redirect_uri: Redirect URI used in the auth request

    Returns:
        dict: Token response from Google

    Raises:
        HTTPException: If unable to exchange code
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code"
            )

        return response.json()


def get_google_oauth_url(redirect_uri: str, state: Optional[str] = None) -> str:
    """
    Generate Google OAuth authorization URL.

    Args:
        redirect_uri: Redirect URI after authorization
        state: Optional state parameter for CSRF protection

    Returns:
        str: Google OAuth authorization URL
    """
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    if state:
        params["state"] = state

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"
