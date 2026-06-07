import os
import sys
import logging

from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

from models import Base
from src.log_info import setup_logging

# Load environment variables
load_dotenv()
setup_logging()


def create_db_engine() -> 'Engine':
    """
    Sets up the database engine using environment variables.

    Returns:
        Engine: A SQLAlchemy engine instance connected to the database.

    Raises:
        SystemExit: If required database credentials are missing or if the connection fails.
    """
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_USER, DB_PASSWORD, DB_NAME]):
        logging.critical(
            "Missing required database credentials in environment variables."
        )
        sys.exit("Missing required database credentials in environment variables.")

    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    logging.info(f"Connecting to database at: {DATABASE_URL}")

    try:
        engine = create_engine(DATABASE_URL, echo=True)
        engine.connect()
        logging.info("Database connection successful.")
        return engine
    except OperationalError as e:
        logging.critical(f"Database connection failed: {e}")
        sys.exit(f"Database connection failed: {e}")


def create_session(engine) -> 'Session':
    """
    Creates a new SQLAlchemy session.

    Args:
        engine: The SQLAlchemy engine to bind the session to.

    Returns:
        Session: A new SQLAlchemy session instance.
    """
    logging.info("Creating a new database session.")
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


def init_db(engine) -> None:
    """
    Initializes the database by creating all tables.

    Args:
        engine: The SQLAlchemy engine to use for creating the tables.
    """
    logging.info("Creating database tables.")
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created successfully.")

    # Create the view after creating the tables
    create_view(engine)


def create_view(engine) -> None:
    """
    Creates a view in the database if it doesn't already exist.

    Args:
        engine: The SQLAlchemy engine to use for executing the SQL command.

    Raises:
        Exception: If the SQL command to create the view fails.
    """
    with engine.connect() as connection:
        create_view_sql = """
            CREATE OR REPLACE VIEW precious_metals_prices_view AS
            SELECT metal, price, timestamp
            FROM precious_metals_prices;
        """
        try:
            connection.execute(text(create_view_sql))
            connection.commit()
            logging.info("View 'precious_metals_prices_view' created successfully.")
        except Exception as e:
            logging.error(f"Failed to create view: {e}")
            connection.rollback()
            raise  # Raise exception to stop execution
