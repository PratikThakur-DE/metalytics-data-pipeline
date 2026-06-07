import pytest

from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.db_operations.models import Base, PreciousMetalPrice
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
    Base.metadata.drop_all(engine)


def test_precious_metal_price_model(setup_database):
    """Test that we can create and retrieve a PreciousMetalPrice instance."""
    session = setup_database

    metal_price = PreciousMetalPrice(
        metal="XAU",
        price=2463.0652037613,
        timestamp=datetime(2024, 10, 18, 15, 12, 44, 432236),
    )

    session.add(metal_price)
    session.commit()

    assert metal_price.id is not None

    retrieved_price = session.query(PreciousMetalPrice).filter_by(metal="XAU").first()

    # Assert that the retrieved price is not None and matches the input
    assert retrieved_price is not None
    assert retrieved_price.price == metal_price.price


def test_precious_metal_price_model_timestamp(setup_database):
    """Test that the timestamp is stored correctly for PreciousMetalPrice."""
    session = setup_database

    timestamp_value = datetime(2024, 10, 18, 15, 12, 44, 432236)
    metal_price = PreciousMetalPrice(
        metal="XAU", price=2463.06, timestamp=timestamp_value
    )

    session.add(metal_price)
    session.commit()

    # Query the database to retrieve the PreciousMetalPrice entry
    retrieved_price = session.query(PreciousMetalPrice).filter_by(metal="XAU").first()

    assert retrieved_price.timestamp == timestamp_value
