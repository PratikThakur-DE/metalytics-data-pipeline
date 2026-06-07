import requests
import datetime
import os
import logging
from typing import Dict

from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from src.db_operations.db_connection import create_db_engine
from src.db_operations.models import PreciousMetalPrice
from src.log_info import setup_logging

setup_logging()
load_dotenv()

API_KEY = os.getenv("METALS_API_KEY")
API_URL = "https://api.metalpriceapi.com/v1/latest"
BASE_CURRENCY = "EUR"
CURRENCIES = "XAU,XAG,XPT,XPD"


def fetch_metal_prices() -> Dict[str, float]:
    """
    Fetches the latest metal prices from the MetalPrice API.

    Returns:
        Dict[str, float]: A dictionary with metal codes (e.g., 'XAU', 'XAG') 
                          as keys and their respective prices as values.

    Raises:
        Exception: If there is an error in fetching the data or an issue 
                   with the API response.
    """
    params = {
        "api_key": API_KEY,
        "base": BASE_CURRENCY,
        "currencies": CURRENCIES,
    }

    logging.info(f"Sending request to {API_URL} with params: {params}")

    try:
        # Send the request and log response status and content
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        logging.info(f"Received response status: {response.status_code}")

        # Log the response JSON data
        data = response.json()
        logging.info(f"Response data: {data}")

        if data.get("success"):
            logging.info("Successfully fetched metal prices.")
            return data.get("rates")
        else:
            error_message = data.get("error", "Unknown error")
            logging.error(f"API Error: {error_message}")
            raise Exception(f"API Error: {error_message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP Error: {e}")
        raise  # Re-raise the exception to stop execution


def load_data_into_db() -> None:
    """
    Fetches metal prices and loads them into the database.

    This function connects to the database, retrieves the metal prices using 
    the fetch_metal_prices function, and inserts the data into the 
    'PreciousMetalPrice' table.

    Raises:
        Exception: If there is an issue saving data to the database.
    """
    try:
        rates = fetch_metal_prices()

        # Prepare the database connection
        engine = create_db_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        # Iterate over the desired metals and store only the metal code (e.g., 'XAU')
        for metal in ["EURXAU", "EURXAG", "EURXPT", "EURXPD"]:
            price = rates.get(metal)
            if price is not None:
                # Strip the 'EUR' prefix from the metal code
                metal_code = metal.replace("EUR", "")

                # Create a new PreciousMetalPrice entry
                metal_price = PreciousMetalPrice(
                    metal=metal_code,
                    price=price,
                    timestamp=datetime.datetime.utcnow(),
                )
                session.add(metal_price)

        # Commit the transaction
        session.commit()
        logging.info("Metal prices saved to database successfully.")

    except Exception as e:
        logging.error(f"Failed to save metal prices: {e}")
        raise  # Re-raise the exception to stop execution
    finally:
        # Close the session
        session.close()
