import pandas as pd

from src.models.model import Model


def test_model_training():
    """Test that the model can be trained on sample data."""
    model = Model(tickers=["XAU", "XAG"])

    # Mock the fetch_data method to return sample data
    model.fetch_data = lambda: pd.DataFrame(
        {"XAU": [2463.06, 2465.07, 2462.34], "XAG": [29.22, 29.30, 29.25]},
        index=pd.date_range(start="2024-10-18", periods=3, freq="h"),
    )

    model.train()
    assert len(model.models) == 2  # Ensure models for both tickers are trained
