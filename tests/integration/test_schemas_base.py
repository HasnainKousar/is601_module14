import pytest
from pydantic import ValidationError
from app.schemas.base import UserBase, PasswordMixin, UserCreate, UserLogin


def test_user_base_accepts_valid_data():
    """UserBase should accept correct user information."""
    data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "username": "alicesmith",
    }
    user = UserBase(**data)
    assert user.first_name == "Alice"
    assert user.email == "alice.smith@example.com"


def test_user_base_rejects_bad_email():
    """UserBase should raise error for malformed email."""
    data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "not-an-email",
        "username": "alicesmith",
    }
    with pytest.raises(ValidationError):
        UserBase(**data)


def test_password_mixin_accepts_strong_password():
    """PasswordMixin should accept a strong password."""
    data = {"password": "StrongPass456"}
    password_mixin = PasswordMixin(**data)
    assert password_mixin.password == "StrongPass456"



def test_password_mixin_requires_digit():
    """PasswordMixin should require at least one digit."""
    data = {"password": "NoDigitsPresent"}
    with pytest.raises(ValidationError, match="Password must contain at least one digit"):
        PasswordMixin(**data)

def test_password_mixin_requires_uppercase():
    """PasswordMixin should require at least one uppercase character."""
    data = {"password": "alllowercase2"}
    with pytest.raises(ValidationError, match="Password must contain at least one uppercase letter"):
        PasswordMixin(**data)


def test_password_mixin_requires_lowercase():
    """PasswordMixin should require at least one lowercase character."""
    data = {"password": "ALLUPPERCASE2"}
    with pytest.raises(ValidationError, match="Password must contain at least one lowercase letter"):
        PasswordMixin(**data)

def test_password_mixin_rejects_too_short():
    """PasswordMixin should not allow short passwords."""
    data = {"password": "tiny"}
    with pytest.raises(ValidationError):
        PasswordMixin(**data)



def test_user_create_accepts_valid_input():
    """UserCreate should accept valid user details."""
    data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "username": "alicesmith",
        "password": "StrongPass456",
    }
    user_create = UserCreate(**data)
    assert user_create.username == "alicesmith"
    assert user_create.password == "StrongPass456"


def test_user_create_rejects_bad_password():
    """UserCreate should not allow weak passwords."""
    data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "username": "alicesmith",
        "password": "tiny",
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)

def test_user_login_rejects_bad_password():
    """UserLogin should not allow weak passwords."""
    data = {"username": "alicesmith", "password": "tiny"}
    with pytest.raises(ValidationError):
        UserLogin(**data)

def test_user_login_accepts_valid_credentials():
    """UserLogin should accept correct credentials."""
    data = {"username": "alicesmith", "password": "StrongPass456"}
    user_login = UserLogin(**data)
    assert user_login.username == "alicesmith"


def test_user_login_rejects_short_username():
    """UserLogin should not allow usernames that are too short."""
    data = {"username": "as", "password": "StrongPass456"}
    with pytest.raises(ValidationError):
        UserLogin(**data)


