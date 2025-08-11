# tests/integration/test_user_auth.py

import pytest
from uuid import UUID
import pydantic_core
from sqlalchemy.exc import IntegrityError
from app.models.user import User

def test_password_hashing_and_check(db_session, fake_user_data):
    """Password hashing should work and verify correctly."""
    original_password = "StrongPass456"
    hashed = User.hash_password(original_password)
    user = User(
        first_name=fake_user_data['first_name'],
        last_name=fake_user_data['last_name'],
        email=fake_user_data['email'],
        username=fake_user_data['username'],
        password=hashed
    )
    assert user.verify_password(original_password) is True
    assert user.verify_password("WrongPass789") is False
    assert hashed != original_password

def test_user_registration_success(db_session, fake_user_data):
    """User registration should succeed with valid data."""
    fake_user_data['password'] = "StrongPass456"
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    assert user.first_name == fake_user_data['first_name']
    assert user.last_name == fake_user_data['last_name']
    assert user.email == fake_user_data['email']
    assert user.username == fake_user_data['username']
    assert user.is_active is True
    assert user.is_verified is False
    assert user.verify_password("StrongPass456") is True

def test_registration_fails_for_duplicate_email(db_session):
    """Should not allow registration with duplicate email."""
    user1_data = {
        "first_name": "Alpha",
        "last_name": "UserA",
        "email": "unique.alpha@example.com",
        "username": "alphauser",
        "password": "StrongPass456"
    }
    user2_data = {
        "first_name": "Beta",
        "last_name": "UserB",
        "email": "unique.alpha@example.com",
        "username": "betauser",
        "password": "StrongPass456"
    }
    first_user = User.register(db_session, user1_data)
    db_session.commit()
    db_session.refresh(first_user)
    with pytest.raises(ValueError, match="Username or email already exists"):
        User.register(db_session, user2_data)

def test_user_authentication_and_token(db_session, fake_user_data):
    """Authentication should return a valid token."""
    fake_user_data['password'] = "StrongPass456"
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    auth_result = User.authenticate(
        db_session,
        fake_user_data['username'],
        "StrongPass456"
    )
    assert auth_result is not None
    assert "access_token" in auth_result
    assert "token_type" in auth_result
    assert auth_result["token_type"] == "bearer"
    assert "user" in auth_result

def test_last_login_field_is_updated(db_session, fake_user_data):
    """last_login should be set after authentication."""
    fake_user_data['password'] = "StrongPass456"
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    assert user.last_login is None
    auth_result = User.authenticate(db_session, fake_user_data['username'], "StrongPass456")
    db_session.refresh(user)
    assert user.last_login is not None

def test_unique_email_and_username_constraint(db_session):
    """Should enforce uniqueness for email and username."""
    user1_data = {
        "first_name": "Gamma",
        "last_name": "UserG",
        "email": "unique.gamma@example.com",
        "username": "gammauser",
        "password": "StrongPass456"
    }
    User.register(db_session, user1_data)
    db_session.commit()
    user2_data = {
        "first_name": "Delta",
        "last_name": "UserD",
        "email": "unique.gamma@example.com",
        "username": "deltauser",
        "password": "StrongPass456"
    }
    with pytest.raises(ValueError, match="Username or email already exists"):
        User.register(db_session, user2_data)

def test_registration_fails_with_short_password(db_session):
    """Should not allow registration with password less than 6 chars."""
    test_data = {
        "first_name": "Short",
        "last_name": "Pwd",
        "email": "short.pwd@example.com",
        "username": "shortpwd",
        "password": "Tiny1"
    }
    with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
        User.register(db_session, test_data)

def test_invalid_token_is_rejected():
    """Should return None for invalid tokens."""
    invalid_token = "not.a.valid.token"
    result = User.verify_token(invalid_token)
    assert result is None

def test_token_creation_and_check(db_session, fake_user_data):
    """Should create and verify access token for user."""
    fake_user_data['password'] = "StrongPass456"
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    token = User.create_access_token({"sub": str(user.id)})
    decoded_user_id = User.verify_token(token)
    assert decoded_user_id == user.id

def test_authenticate_with_email_instead_of_username(db_session, fake_user_data):
    """Should allow authentication using email as identifier."""
    fake_user_data['password'] = "StrongPass456"
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    auth_result = User.authenticate(
        db_session,
        fake_user_data['email'],
        "StrongPass456"
    )
    assert auth_result is not None
    assert "access_token" in auth_result

def test_user_model_str_representation(test_user):
    """User model __str__ should return expected string."""
    expected = f"<User(name={test_user.first_name} {test_user.last_name}, email={test_user.email})>"
    assert str(test_user) == expected

def test_registration_fails_without_password(db_session):
    """Should not allow registration if password is missing."""
    test_data = {
        "first_name": "NoPwd",
        "last_name": "Missing",
        "email": "no.pwd@example.com",
        "username": "nopwduser",
        # Password is missing
    }
    with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
        User.register(db_session, test_data)

