# ======================================================================================
# tests/integration/test_user.py
# ======================================================================================
# Purpose: Demonstrate user model interactions with the database using pytest fixtures.
#          Relies on 'conftest.py' for database session management and test isolation.
# ======================================================================================

import pytest
import logging
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from app.models.user import User
from tests.conftest import create_fake_user, managed_db_session

# Use the logger configured in conftest.py
logger = logging.getLogger(__name__)

# ======================================================================================
# Basic Connection & Session Tests
# ======================================================================================

def test_database_connection(db_session):
    """
    Verify that the database connection is working.
    
    Uses the db_session fixture from conftest.py, which truncates tables after each test.
    """
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
    logger.info("Database connection test passed")


def test_managed_session():
    """
    Test the managed_db_session context manager for one-off queries and rollbacks.
    Demonstrates how a manual session context can work alongside the fixture-based approach.
    """
    with managed_db_session() as session:
        # Simple query
        session.execute(text("SELECT 1"))
        
        # Generate an error to trigger rollback
        try:
            session.execute(text("SELECT * FROM nonexistent_table"))
        except Exception as e:
            assert "nonexistent_table" in str(e)

# ======================================================================================
# Session Handling & Partial Commits
# ======================================================================================
def test_partial_commit_and_rollback(db_session):
    """
    Test that only valid users are committed when a duplicate triggers rollback.
    """
    initial_count = db_session.query(User).count()
    logger.info(f"Initial user count before test_partial_commit_and_rollback: {initial_count}")

    user1 = User(
        first_name="Alpha",
        last_name="One",
        email="alpha1@example.com",
        username="alphaone",
        password="hashed_password"
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        first_name="Beta",
        last_name="Two",
        email="alpha1@example.com",  # Duplicate email
        username="betatwo",
        password="hashed_password"
    )
    db_session.add(user2)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.info(f"Expected failure on duplicate user2: {e}")

    user3 = User(
        first_name="Gamma",
        last_name="Three",
        email="gamma3@example.com",
        username="gammathree",
        password="hashed_password"
    )
    db_session.add(user3)
    db_session.commit()

    final_count = db_session.query(User).count()
    expected_final = initial_count + 2
    assert final_count == expected_final, (
        f"Expected {expected_final} users after test, found {final_count}"
    )

# ======================================================================================
# User Creation Tests
# ======================================================================================

def test_create_user_with_faker(db_session):
    """
    Create a single user using Faker-generated data and verify it was saved.
    """
    user_data = create_fake_user()
    logger.info(f"Creating user with data: {user_data}")
    
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)  # Refresh populates fields like user.id
    
    assert user.id is not None
    assert user.email == user_data["email"]
    logger.info(f"Successfully created user with ID: {user.id}")


def test_create_several_users(db_session):
    """
    Create three users and confirm they are saved.
    """
    users = []
    for _ in range(3):
        user_data = create_fake_user()
        user = User(**user_data)
        users.append(user)
        db_session.add(user)
    db_session.commit()
    assert len(users) == 3
    logger.info(f"Successfully created {len(users)} users")

# ======================================================================================
# Query Tests
# ======================================================================================

def test_query_user_methods(db_session, seed_users):
    """
    Test user queries: count, filter by email, order by email.
    """
    user_count = db_session.query(User).count()
    assert user_count >= len(seed_users), "The user table should have at least the seeded users"
    first_user = seed_users[0]
    found = db_session.query(User).filter_by(email=first_user.email).first()
    assert found is not None, "Should find the seeded user by email"
    users_by_email = db_session.query(User).order_by(User.email).all()
    assert len(users_by_email) >= len(seed_users), "Query should return at least the seeded users"

# ======================================================================================
# Transaction / Rollback Tests
# ======================================================================================

def test_transaction_forces_rollback(db_session):
    """
    Add a user, force error, rollback, and confirm user not committed.
    """
    initial_count = db_session.query(User).count()
    try:
        user_data = create_fake_user()
        user = User(**user_data)
        db_session.add(user)
        db_session.execute(text("SELECT * FROM nonexistent_table"))
        db_session.commit()
    except Exception:
        db_session.rollback()
    final_count = db_session.query(User).count()
    assert final_count == initial_count, "The new user should not have been committed"

# ======================================================================================
# Update Tests
# ======================================================================================

def test_update_user_email_and_refresh(db_session, test_user):
    """
    Update user's email, refresh, and check updated fields.
    """
    original_email = test_user.email
    original_update_time = test_user.updated_at
    new_email = f"updated_{original_email}"
    test_user.email = new_email
    db_session.commit()
    db_session.refresh(test_user)
    assert test_user.email == new_email, "Email should have been updated"
    assert test_user.updated_at > original_update_time, "Updated time should be newer"
    logger.info(f"Successfully updated user {test_user.id}")

# ======================================================================================
# Bulk Operation Tests
# ======================================================================================

@pytest.mark.slow
def test_bulk_insert_users(db_session):
    """
    Bulk insert ten users and verify count (slow test).
    """
    users_data = [create_fake_user() for _ in range(10)]
    users = [User(**data) for data in users_data]
    db_session.bulk_save_objects(users)
    db_session.commit()
    count = db_session.query(User).count()
    assert count >= 10, "At least 10 users should now be in the database"
    logger.info(f"Successfully performed bulk operation with {len(users)} users")

# ======================================================================================
# Uniqueness Constraint Tests
# ======================================================================================

def test_email_uniqueness_constraint(db_session):
    """
    Should raise IntegrityError for duplicate email.
    """
    first_user_data = create_fake_user()
    first_user = User(**first_user_data)
    db_session.add(first_user)
    db_session.commit()
    second_user_data = create_fake_user()
    second_user_data["email"] = first_user_data["email"]
    second_user = User(**second_user_data)
    db_session.add(second_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_username_uniqueness_constraint(db_session):
    """
    Should raise IntegrityError for duplicate username.
    """
    first_user_data = create_fake_user()
    first_user = User(**first_user_data)
    db_session.add(first_user)
    db_session.commit()
    second_user_data = create_fake_user()
    second_user_data["username"] = first_user_data["username"]
    second_user = User(**second_user_data)
    db_session.add(second_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

# ======================================================================================
# Persistence after Constraint Violation
# ======================================================================================

def test_user_still_exists_after_constraint_violation(db_session):
    """
    Confirm original user persists after duplicate email attempt.
    """
    initial_user_data = {
        "first_name": "First",
        "last_name": "User",
        "email": "first@example.com",
        "username": "firstuser",
        "password": "password123"
    }
    initial_user = User(**initial_user_data)
    db_session.add(initial_user)
    db_session.commit()
    saved_id = initial_user.id
    try:
        duplicate_user = User(
            first_name="Second",
            last_name="User",
            email="first@example.com",
            username="seconduser",
            password="password456"
        )
        db_session.add(duplicate_user)
        db_session.commit()
        assert False, "Should have raised IntegrityError"
    except IntegrityError:
        db_session.rollback()
    found_user = db_session.query(User).filter_by(id=saved_id).first()
    assert found_user is not None, "Original user should exist"
    assert found_user.id == saved_id, "Should find original user by ID"
    assert found_user.email == "first@example.com", "Email should be unchanged"
    assert found_user.username == "firstuser", "Username should be unchanged"

# ======================================================================================
# Error Handling Test
# ======================================================================================

def test_error_handling():
    """
    Verify that a manual managed_db_session can capture and log invalid SQL errors.
    """
    with pytest.raises(Exception) as exc_info:
        with managed_db_session() as session:
            session.execute(text("INVALID SQL"))
    assert "INVALID SQL" in str(exc_info.value)



def test_user_update_fields(monkeypatch):
    # Patch utcnow to return a fixed datetime
    fixed_time = datetime(2025, 8, 11, 15, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr("app.models.user.utcnow", lambda: fixed_time)
    user = User(first_name="Alice", last_name="Smith", email="alice@example.com", username="alicesmith", password="pw")
    user.updated_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
    updated = user.update(first_name="Bob", is_active=True)
    assert updated is user
    assert user.first_name == "Bob"
    assert user.is_active is True
    assert user.updated_at == fixed_time