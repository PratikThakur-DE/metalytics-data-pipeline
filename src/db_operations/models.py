from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()


class PreciousMetalPrice(Base):
    """Represents the price of a precious metal at a given timestamp."""
    
    __tablename__ = "precious_metals_prices"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    metal: str = Column(String(10), nullable=False, index=True)
    price: float = Column(Float, nullable=False)
    timestamp: datetime.datetime = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        """Returns a string representation of the PreciousMetalPrice instance."""
        return f"<PreciousMetalPrice(metal='{self.metal}', price={self.price}, timestamp={self.timestamp})>"


class ModelMetadata(Base):
    """Stores metadata for model training, including hyperparameters and parameters."""
    
    __tablename__ = "model_training_metadata"

    id: int = Column(Integer, primary_key=True)
    metal: str = Column(String, nullable=False)
    hyperparameters: dict = Column(JSON, nullable=False)  # Using dict for JSON
    parameters: dict = Column(JSON, nullable=False)  # Using dict for JSON
    timestamp: datetime.datetime = Column(DateTime, nullable=False)

    def __repr__(self) -> str:
        """Returns a string representation of the ModelMetadata instance."""
        return (f"<ModelMetadata(metal='{self.metal}', "
                f"hyperparameters={self.hyperparameters}, "
                f"parameters={self.parameters}, "
                f"timestamp={self.timestamp})>")
