import logging
from src.db_operations.db_connection import create_db_engine, init_db
from src.data_ingestion.data_loader import load_data_into_db
from src.models.model import Model
from src.log_info import setup_logging


def main() -> None:
    """Main function to initialize the database, load data, train models, and save them."""
    
    setup_logging()

    # Step 1: Initialize the database and create tables
    logging.info("Initializing database...")
    try:
        engine = create_db_engine()
        init_db(engine)
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing the database: {e}")
        return  # Exit if initialization fails

    # Step 2: Load metal price data into the database
    logging.info("Loading metal prices into the database...")
    try:
        load_data_into_db()
        logging.info("Metal prices loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading metal prices: {e}")
        return  # Exit if loading fails

    # Step 3: Define metal tickers and train models
    tickers = ["XAU", "XAG", "XPT", "XPD"]
    model_instance = Model(tickers)

    logging.info("Training models...")
    try:
        model_instance.train()
        logging.info("Models trained successfully.")
    except Exception as e:
        logging.error(f"Error during model training: {e}")
        return  # Exit if training fails

    # Step 4: Save the trained models
    try:
        model_instance.save("trained_models")
        logging.info("Trained models saved successfully.")
    except Exception as e:
        logging.error(f"Error saving trained models: {e}")

    logging.info("Process completed successfully.")


if __name__ == "__main__":
    main()
