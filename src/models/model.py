import pandas as pd
import logging

from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import text

from src.db_operations.db_connection import create_db_engine
from sktime.forecasting.arima import ARIMA
from src.log_info import setup_logging
from src.db_operations.models import ModelMetadata

setup_logging()


class Model:
    """Class to manage and train ARIMA models for precious metal prices."""
    
    def __init__(self, tickers: list[str]) -> None:
        """
        Initializes the Model instance.

        Args:
            tickers (list[str]): A list of ticker symbols for precious metals.
        """
        self.tickers: list[str] = tickers
        self.models: dict[str, ARIMA] = {}
        self.arima_order: tuple[int, int, int] = (1, 1, 0)  # ARIMA order (p, d, q)

    def fetch_data(self) -> pd.DataFrame:
        """Fetches the last 12 hours of data for the specified tickers from the database view.

        Returns:
            pd.DataFrame: DataFrame containing metal prices indexed by timestamp.
        """
        engine = create_db_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            twelve_hours_ago = datetime.utcnow() - timedelta(hours=12)

            query = text(
                """
                SELECT metal, price, timestamp
                FROM precious_metals_prices_view
                WHERE timestamp >= :twelve_hours_ago
                AND metal IN :tickers
                """
            )

            results = session.execute(
                query,
                {"twelve_hours_ago": twelve_hours_ago, "tickers": tuple(self.tickers)},
            ).fetchall()

            if not results:
                logging.warning("No data fetched from the view.")
                return pd.DataFrame()  # Return empty DataFrame if no results

            data = pd.DataFrame(results, columns=["metal", "price", "timestamp"])
            data["timestamp"] = pd.to_datetime(data["timestamp"])
            data.set_index("timestamp", inplace=True)
            data = data.pivot(columns="metal", values="price")

            logging.info("Data fetched successfully from the view.")
            return data

        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return pd.DataFrame()  # Return empty DataFrame in case of an error

        finally:
            session.close()

    def save_model_metadata(self, session: sessionmaker, ticker: str, model: ARIMA) -> None:
        """Saves model hyperparameters and parameters into the database.

        Args:
            session (sessionmaker): The database session to use.
            ticker (str): The ticker symbol of the metal.
            model (ARIMA): The trained ARIMA model.
        """
        try:
            fitted_params = model.get_fitted_params()
            logging.info(f"Fitted parameters for {ticker}: {fitted_params}")

            order = self.arima_order  # This holds the order you used, e.g., (1, 1, 0)

            # Extract parameters
            parameters = {
                "intercept": fitted_params.get("intercept"),
                "ar.L1": fitted_params.get("ar.L1"),
                "sigma2": fitted_params.get("sigma2"),
                "aic": fitted_params.get("aic"),
                "bic": fitted_params.get("bic"),
                "hqic": fitted_params.get("hqic"),
                # Add other relevant keys here
            }

            # Create a new ModelMetadata entry
            new_metadata = ModelMetadata(
                metal=ticker,
                hyperparameters={"p": order[0], "d": order[1], "q": order[2]},
                parameters=parameters,
                timestamp=datetime.utcnow(),
            )

            session.add(new_metadata)
            logging.info(f"Model metadata for {ticker} added to session.")

        except Exception as e:
            logging.error(f"Error while saving model metadata for {ticker}: {e}")

    def train(self) -> None:
        """Trains ARIMA models for each ticker using data from the last 12 hours."""
        engine = create_db_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        data = self.fetch_data()

        for ticker in self.tickers:
            if ticker in data.columns:
                dataset = data[ticker].dropna().values

                if dataset.size > 0 and dataset.ndim == 1:
                    logging.info(f"Dataset for {ticker}: {dataset}")

                    try:
                        model = ARIMA(
                            order=self.arima_order,
                            with_intercept=True,
                            suppress_warnings=True,
                        )
                        model.fit(dataset)
                        self.models[ticker] = model
                        logging.info(f"Trained model for {ticker}.")

                        # Save model metadata (order and parameters)
                        self.save_model_metadata(session, ticker, model)

                    except Exception as e:
                        logging.error(f"Error training model for {ticker}: {e}")

                else:
                    logging.warning(
                        f"No available data to train model for {ticker}. Dataset is empty or incorrectly shaped."
                    )
            else:
                logging.warning(f"{ticker} not found in the fetched data.")

        try:
            # Commit the session
            session.commit()
            logging.info("Session committed successfully. Model metadata should be saved.")
        except Exception as e:
            logging.error(f"Failed to commit the session: {e}")
            session.rollback()

        finally:
            session.close()

    def save(self, path_to_dir: str | Path) -> None:
        """Saves the trained models to the specified directory.

        Args:
            path_to_dir (str | Path): The directory path where models will be saved.
        """
        path_to_dir = Path(path_to_dir)
        path_to_dir.mkdir(parents=True, exist_ok=True)
        for ticker in self.tickers:
            full_path = path_to_dir / ticker
            self.models[ticker].save(full_path)
