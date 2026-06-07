import pytest

from unittest.mock import patch
from sqlalchemy.orm import sessionmaker

from src.db_operations.models import Base
from src.data_ingestion.data_loader import fetch_metal_prices, load_data_into_db
from src.db_operations.db_connection import create_db_engine

@pytest.fixture
def setup_database():
    """Set up an in-memory SQLite database for testing."""
    engine = create_db_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@patch("requests.get")
def test_fetch_metal_prices(mock_get):
    """Test that fetch_metal_prices correctly processes the mocked API response."""

    # Define mock API response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "success": True,
        "base": "EUR",
        "timestamp": 1729209599,
        "rates": {"XAU": 0.0004059982, "XAG": 0.0342170837},
    }

    # Call the function
    data = fetch_metal_prices()

    # Assertions to validate the returned data
    assert data["XAU"] == 0.0004059982, "The XAU price should match the mocked data"
    assert data["XAG"] == 0.0342170837, "The XAG price should match the mocked data"


def test_load_data_into_db(setup_database):
    """Test that we can load data into the database."""
    load_data_into_db()  # You can mock the API response if needed
