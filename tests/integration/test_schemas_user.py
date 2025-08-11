import pytest
from app.schemas.user import UserCreate, PasswordUpdate

def test_usercreate_passwords_must_match():
    # Should raise ValueError if passwords do not match
    with pytest.raises(ValueError, match="Passwords do not match"):
        UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            username="johndoe",
            password="SecurePass123!",
            confirm_password="WrongPass123!"
        )

def test_usercreate_password_strength():
    # Too short
    with pytest.raises(ValueError, match="at least 8 characters"):
        UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            username="johndoe",
            password="Short1!",
            confirm_password="Short1!"
        )
    # No uppercase
    with pytest.raises(ValueError, match="uppercase"):
        UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            username="johndoe",
            password="securepass123!",
            confirm_password="securepass123!"
        )
    # No lowercase
    with pytest.raises(ValueError, match="lowercase"):
        UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            username="johndoe",
            password="SECUREPASS123!",
            confirm_password="SECUREPASS123!"
        )
    # No digit
    with pytest.raises(ValueError, match="digit"):
        UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            username="johndoe",
            password="SecurePass!",
            confirm_password="SecurePass!"
        )
    # No special character
    with pytest.raises(ValueError, match="special character"):
        UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            username="johndoe",
            password="SecurePass123",
            confirm_password="SecurePass123"
        )
    # Valid password
    user = UserCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        username="johndoe",
        password="SecurePass123!",
        confirm_password="SecurePass123!"
    )
    assert user.password == "SecurePass123!"

def test_passwordupdate_verify_passwords():
    # Mismatched new passwords
    with pytest.raises(ValueError, match="do not match"):
        PasswordUpdate(
            current_password="OldPass123!",
            new_password="NewPass123!",
            confirm_new_password="WrongPass123!"
        )
    # New password same as current
    with pytest.raises(ValueError, match="different from current"):
        PasswordUpdate(
            current_password="SamePass123!",
            new_password="SamePass123!",
            confirm_new_password="SamePass123!"
        )
    # Valid update
    pw_update = PasswordUpdate(
        current_password="OldPass123!",
        new_password="NewPass123!",
        confirm_new_password="NewPass123!"
    )
    assert pw_update.new_password == "NewPass123!"