import pytest

from sqlalchemy.exc import OperationalError
from src.db_operations.db_connection import create_db_engine


def test_database_connection():
    """Test that the database connection can be established."""
    engine = create_db_engine()
    try:
        connection = engine.connect()
        assert connection is not None
    except OperationalError as e:
        pytest.fail(f"Database connection failed: {e}")
    finally:
        connection.close()
