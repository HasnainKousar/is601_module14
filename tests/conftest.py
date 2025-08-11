# tests/e2e/conftest.py
"""
THis file contains the configuration for end-to-end tests using Playwright.
It sets up the Playwright test environment, including the browser context and page fixtures.
"""


import socket
import subprocess
import time
import logging
from typing import Generator, Dict, List
from contextlib import contextmanager

import pytest
import requests
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from playwright.sync_api import sync_playwright, Browser, Page

from app.database import Base, get_engine, get_sessionmaker
from app.models.user import User
from app.core.config import settings
from app.database_init import init_db, drop_db


#######################################################
# Logging Configuration
#######################################################

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#######################################################
# Database Configuration
#######################################################

fake = Faker()
Faker.seed(12345)

test_engine = get_engine(database_url=settings.DATABASE_URL)
TestingSessionLocal = get_sessionmaker(engine=test_engine)

#######################################################
# Helper Functions
#######################################################
def create_fake_user() -> Dict[str, str]:
    """
    Generate a dictionary with fake user data for testing purposes.
    """
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "username": fake.unique.user_name(),
        "password": fake.password(length=12)
    }

@contextmanager
def managed_db_session():
    """
    Context manager for handling a database session with rollback on error.
    """
    session = TestingSessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

#######################################################
# Server Startup / Healthcheck
#######################################################
def wait_for_server(url: str, timeout: int = 30) -> bool:
    """
    Wait for the FastAPI server to respond at the given URL within a timeout.
    Returns True if the server responds with status 200, else False.
    """
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False

class ServerStartupError(Exception):
    """
    Custom exception for FastAPI server startup failures in tests.
    """
    pass

#######################################################
# Database Fixtures
#######################################################
@pytest.fixture(scope="session", autouse=True)
def setup_test_database(request):
    """
    Pytest fixture to set up and tear down the test database for the session.
    Drops and recreates tables before tests, and optionally drops them after.
    """
    logger.info("Setting up test database...")
    try:
        Base.metadata.drop_all(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)
        init_db()
        logger.info("Test database initialized.")
    except Exception as e:
        logger.error(f"Error setting up test database: {str(e)}")
        raise

    yield  # Tests run after this

    if not request.config.getoption("--preserve-db"):
        logger.info("Dropping test database tables...")
        drop_db()

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Pytest fixture to provide a database session for a test.
    Commits on success, rolls back on error, and closes after use.
    """
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

#######################################################
# Test Data Fixtures
#######################################################
@pytest.fixture
def fake_user_data() -> Dict[str, str]:
    """Provide fake user data."""
    return create_fake_user()

@pytest.fixture
def test_user(db_session: Session) -> User:
    """
    Create and return a single test user in the database.
    """
    user_data = create_fake_user()
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    logger.info(f"Created test user ID: {user.id}")
    return user

@pytest.fixture
def seed_users(db_session: Session, request) -> List[User]:
    """
    Pytest fixture to seed the database with multiple test users.
    Number of users can be set via request.param (default 5).
    """
    num_users = getattr(request, "param", 5)
    users = [User(**create_fake_user()) for _ in range(num_users)]
    db_session.add_all(users)
    db_session.commit()
    logger.info(f"Seeded {len(users)} users.")
    return users

#######################################################
# FastAPI Server Fixture
#######################################################
def find_available_port() -> int:
    """
    Find and return an available port on localhost for the test server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

@pytest.fixture(scope="session")
def fastapi_server():
    """
    Pytest fixture to start and stop a FastAPI server for tests.
    Finds an available port, starts the server, waits for health, and stops after tests.
    """
    base_port = 8000
    server_url = f'http://127.0.0.1:{base_port}/'

    # Check if port is free; if not, pick an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', base_port)) == 0:
            base_port = find_available_port()
            server_url = f'http://127.0.0.1:{base_port}/'

    logger.info(f"Starting FastAPI server on port {base_port}...")

    process = subprocess.Popen(
        ['uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(base_port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='.'  # ensure the working directory is set correctly
    )

    # IMPORTANT: Use the /health endpoint for the check!
    health_url = f"{server_url}health"
    if not wait_for_server(health_url, timeout=30):
        stderr = process.stderr.read()
        logger.error(f"Server failed to start. Uvicorn error: {stderr}")
        process.terminate()
        raise ServerStartupError(f"Failed to start test server on {health_url}")

    logger.info(f"Test server running on {server_url}.")
    yield server_url

    logger.info("Stopping test server...")
    process.terminate()
    try:
        process.wait(timeout=5)
        logger.info("Test server stopped.")
    except subprocess.TimeoutExpired:
        process.kill()
        logger.warning("Test server forcefully stopped.")

#######################################################
# Playwright Fixtures for UI Testing
#######################################################
@pytest.fixture(scope="session")
def browser_context():
    """
    Pytest fixture to launch and close a Playwright browser for UI tests.
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        logger.info("Playwright browser launched.")
        try:
            yield browser
        finally:
            logger.info("Closing Playwright browser.")
            browser.close()

@pytest.fixture
def page(browser_context: Browser):
    """
    Pytest fixture to create and close a new browser page and context for UI tests.
    """
    context = browser_context.new_context(
        viewport={'width': 1920, 'height': 1080},
        ignore_https_errors=True
    )
    page = context.new_page()
    logger.info("New browser page created.")
    try:
        yield page
    finally:
        logger.info("Closing browser page and context.")
        page.close()
        context.close()

# #######################################################
# Pytest Command-Line Options
# #######################################################
def pytest_addoption(parser):
    """
    Add custom command line options:
      --preserve-db : Keep test database after tests
      --run-slow    : Run tests marked as 'slow'
    """
    parser.addoption("--preserve-db", action="store_true", help="Keep test database after tests")
    parser.addoption("--run-slow", action="store_true", help="Run tests marked as slow")

def pytest_collection_modifyitems(config, items):
    """
    Skip tests marked as 'slow' unless --run-slow is specified.
    """
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="use --run-slow to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)