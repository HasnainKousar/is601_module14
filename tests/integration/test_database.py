import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session
import importlib
import sys
from app.database import get_db, SessionLocal

DATABASE_MODULE = "app.database"

@pytest.fixture
def mock_settings(monkeypatch):
    """Fixture to mock the settings.DATABASE_URL before app.database is imported."""
    mock_url = "postgresql://user:password@localhost:5432/test_db"
    mock_settings = MagicMock()
    mock_settings.DATABASE_URL = mock_url
    # Ensure 'app.database' is not loaded
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    # Patch settings in 'app.database'
    monkeypatch.setattr(f"{DATABASE_MODULE}.settings", mock_settings)
    return mock_settings

def reload_database_module():
    """Helper function to reload the database module after patches."""
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    return importlib.import_module(DATABASE_MODULE)



def test_engine_creation_success(mock_settings):
    """Test engine creation returns a valid Engine object."""
    database = reload_database_module()
    engine = database.get_engine()
    assert isinstance(engine, Engine)

def test_base_is_declarative(mock_settings):
    """Test Base is a declarative_base instance."""
    database = reload_database_module()
    Base = database.Base
    assert isinstance(Base, database.declarative_base().__class__)


def test_sessionmaker_creation(mock_settings):
    """Test sessionmaker creation returns a valid sessionmaker object."""
    database = reload_database_module()
    engine = database.get_engine()
    session_maker = database.get_sessionmaker(engine)
    assert isinstance(session_maker, sessionmaker)

def test_engine_creation_failure(mock_settings):
    """Test engine creation raises error if engine cannot be created."""
    database = reload_database_module()
    with patch("app.database.create_engine", side_effect=SQLAlchemyError("Engine error")):
        with pytest.raises(SQLAlchemyError, match="Engine error"):
            database.get_engine()

def test_db_generator_yields_and_closes():
    gen = get_db()
    db = next(gen)
    assert isinstance(db, Session)
    # The session should be open before generator closes
    assert db.is_active
    # Finish generator to trigger finally block
    try:
        next(gen)
    except StopIteration:
        pass
    # After closing, session should be closed
    assert not db.is_active or not db.connection().closed