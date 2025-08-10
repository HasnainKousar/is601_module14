#app/auth/dependencies.py

"""
Authentication and user dependency utilities for FastAPI routes.

Provides functions to retrieve and validate the current user from JWT tokens,
and to ensure the user is active for protected endpoints.
"""


from datetime import datetime
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.schemas.user import UserResponse
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> UserResponse:
    """
    Retrieve the current user from the JWT token in the request.

    Decodes and validates the token, returning a UserResponse object.
    Raises HTTP 401 if credentials are invalid or missing.

    Args:
        token (str): JWT token from the request (injected by FastAPI).

    Returns:
        UserResponse: The user information extracted from the token.

    Raises:
        HTTPException: If credentials are invalid or token is not valid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = User.verify_token(token)
    if token_data is None:
        raise credentials_exception

    try:
        # if the token data is a dictionary
        if isinstance(token_data, dict):
            # if the payload contains a username, use it
            if "username" in token_data:
                return UserResponse(**token_data)
            # otherwise, assume it is a minimal payload with only the 'sub' key.
            elif "sub" in token_data:
                return UserResponse(
                    id=token_data["sub"],
                    username="unknown",
                    email="unknown@example.com",
                    first_name="Unknown",
                    last_name="User",
                    is_active=True,
                    is_verified=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            else:
                raise credentials_exception

        # If the token data is directly a UUID (minimal payload):
        elif isinstance(token_data, UUID):
            return UserResponse(
                id=token_data,
                username="unknown",
                email="unknown@example.com",
                first_name="Unknown",
                last_name="User",
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        else:
            raise credentials_exception

    except Exception:
        raise credentials_exception

def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency to ensure that the current user is active.

    Raises HTTP 400 if the user is inactive.

    Args:
        current_user (UserResponse): The current user object (injected by FastAPI).

    Returns:
        UserResponse: The active user object.

    Raises:
        HTTPException: If the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

